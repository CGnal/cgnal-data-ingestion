package com.cgnal.ignite.spark.streaming.twitter

import java.io.File

import com.cgnal.data.access.ignite.mongo.DocumentMongoStorageAdapter
import com.cgnal.data.model.Document
import com.cgnal.ignite.spark.streaming.twitter.config.TwitterProbeConfig
import com.typesafe.scalalogging.StrictLogging
import javax.cache.configuration.FactoryBuilder
import org.apache.ignite.cache.CacheMode
import org.apache.ignite.configuration.CacheConfiguration
import org.apache.ignite.spark.{IgniteContext, IgniteRDD}
import org.apache.spark.streaming.dstream.DStream
import org.apache.spark.streaming.twitter.TwitterUtils
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.spark.{SparkConf, SparkContext}
import twitter4j.{FilterQuery, Status}

import scala.io.Source

class TwitterProbe extends StrictLogging {

  type SparkStreamingIgniteContext = (StreamingContext , IgniteContext )

  protected def createContexts : SparkStreamingIgniteContext = {
    // First, let's configure Spark
    // We have to at least set an application name and master
    // If no master is given as part of the configuration we
    // will set it to be a local deployment running an
    // executor per thread
    val sparkConfiguration = new SparkConf().
      setAppName("spark-streaming-twitter-probe").
      setMaster(sys.env.getOrElse("spark.master", "local[*]"))

    // Let's create the Spark Context using the configuration we just created
    val sparkContext = new SparkContext(sparkConfiguration)

    // Now let's wrap the context in a streaming one, passing along the window size
    (new StreamingContext(sparkContext, Seconds(30)) , new IgniteContext(sparkContext, "ignite-config.xml"))
  }

  val contexts : SparkStreamingIgniteContext = createContexts

  val streamingContext: StreamingContext = contexts._1
  val igniteContext : IgniteContext = contexts._2


  protected def keywordsFilter( keywords : Seq[String]): FilterQuery = new FilterQuery()
    .language("en")
    .track(keywords : _*)


  protected def allKeywords: Seq[String] = {
    val keywordsFile = new File(TwitterProbeConfig.keywordsFilename)

    val allLines: Seq[String] = if (keywordsFile.exists()) {
      logger.info(s"Loading keywords file $keywordsFile ..")
      Source.fromFile(keywordsFile).getLines().toSeq
    } else {
      logger.warn(s"Keywords file $keywordsFile not found !!")
      Seq.empty[String]
    }

    allLines.flatMap(line => {
      val Array(key: String, name: String, _*) = line.split(",")
      List("$" + key.replace("\"", ""), "#" + name.replace("\"", ""))
    })

  }

  protected def createDocumentCacheConfig: CacheConfiguration[String, Document] = {

    val cacheCfg: CacheConfiguration[String, Document] = new CacheConfiguration[String, Document]()
    cacheCfg.setName(TwitterProbeConfig.documentsCollectionName)
    cacheCfg.setCacheMode(CacheMode.PARTITIONED)
    cacheCfg.setIndexedTypes(classOf[String], classOf[Document])

    cacheCfg.setCacheStoreFactory(FactoryBuilder.factoryOf(classOf[DocumentMongoStorageAdapter]))
    cacheCfg.setReadThrough(true)
    cacheCfg.setWriteThrough(true)

    // Set write-behind flag for synchronous/asynchronous persistent store update
    cacheCfg.setWriteBehindEnabled(true)
    cacheCfg.setWriteBehindFlushSize(2000)
    //cacheCfg.setWriteBehindFlushFrequency(5000)


    cacheCfg
  }

  // Set the system properties so that Twitter4j library used by Twitter stream
  // can use them to generate OAuth credentials
  System.setProperty("twitter4j.oauth.consumerKey", TwitterProbeConfig.twitterConsumerKey)
  System.setProperty("twitter4j.oauth.consumerSecret", TwitterProbeConfig.twitterConsumerSecret)
  System.setProperty("twitter4j.oauth.accessToken", TwitterProbeConfig.twitterAccessToken)
  System.setProperty("twitter4j.oauth.accessTokenSecret", TwitterProbeConfig.twitterAccessTokenSecret)

  // Creating a stream from Twitter (se  e the README to learn how to
  // provide a configuration to make this work - you'll basically
  // need a set of Twitter API keys)
  val tweets: DStream[Status] =
  TwitterUtils.createFilteredStream(streamingContext, None , Some(keywordsFilter(allKeywords)))

  def start(): Unit = {
    import TweetsUtils._

    logger.info("Starting Twitter Probe ...")

    val documentCacheCfg : CacheConfiguration[String, Document] = createDocumentCacheConfig

    // Saving to cache
    val documentCacheRdd : IgniteRDD[String,Document] = igniteContext.fromCache(documentCacheCfg)
    tweets
      .map( tweet => (tweet.getId.toString, toDocument(tweet)))
      .foreachRDD( rdd => documentCacheRdd.savePairs(rdd, overwrite = true) )


    val tweetPairs : DStream[(Long, TTweetText)] =
    tweets.
      map( tweet => (tweet.getId ,tweet.getText))

    tweetPairs.print()


    // Now that the streaming is defined, start it
    streamingContext.start()
    // Let's await the stream to end - forever
    streamingContext.awaitTermination()

  }

  def stop(): Unit = {
    logger.info("Stopping Twitter Probe ...")
    streamingContext.stop(stopSparkContext = true,stopGracefully = true)
    logger.info("Twitter Probe successful stopped")
  }

}