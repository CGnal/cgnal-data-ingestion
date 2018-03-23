package com.cgnal.twitter.probe.ignite.spark.streaming

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.cache.CacheConfig
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import com.cgnal.twitter.probe.common.{KeywordsLoader, TwitterProbeRest, TwitterProbeRuntime}
import com.cgnal.web.rest.{HasVertx, RestMetadata, RestStatus}
import org.apache.ignite.configuration.CacheConfiguration
import org.apache.ignite.spark.{IgniteContext, IgniteRDD}
import org.apache.spark.streaming.dstream.DStream
import org.apache.spark.streaming.twitter.TwitterUtils
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.spark.{SparkConf, SparkContext}
import twitter4j.Status

class TwitterProbe
  extends CacheConfig
    with HasVertx
    with KeywordsLoader
    with BaseLogging {

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
    (new StreamingContext(sparkContext, Seconds(TwitterProbeConfig.streamingProcessingWindow)) , new IgniteContext(sparkContext, "ignite-config.xml"))
  }

  protected val runtime : TwitterProbeRuntime = new TwitterProbeRuntime()

  vertx.deployVerticle(new TwitterProbeRest("Twitter Client Probe", TwitterProbeConfig.restPort , RestMetadata("Twitter Client Probe", RestStatus.OK) , TwitterProbeConfig.configurationAsMap , runtime))

  val contexts : SparkStreamingIgniteContext = createContexts

  val streamingContext: StreamingContext = contexts._1
  val igniteContext : IgniteContext = contexts._2

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
    import com.cgnal.twitter.probe.common.TweetsUtils._

    logger.info("Starting Twitter Probe ...")
    runtime.updateKeywords(allKeywords)

    val documentCacheCfg : CacheConfiguration[String, Document] = createDocumentCacheConfig

    // Saving to cache
    val documentCacheRdd : IgniteRDD[String,Document] = igniteContext.fromCache(documentCacheCfg)
    tweets
      .filter( containsSymbolsOrHashTags(allSymbols , allHashTags , TwitterProbeConfig.withoutSymbolsAndHashTags) )
      .map( tweet => (tweet.getId.toString, toDocument(tweet)))
      .foreachRDD( rdd => documentCacheRdd.savePairs(rdd, overwrite = true) )

    val tweetPairs : DStream[(Long, TTweetText)] =
    tweets.
      map( tweet => (tweet.getId ,tweet.getText))

    streamingContext.addStreamingListener(new TwitterProbeListener(runtime))

    // Now that the streaming is defined, start it
    streamingContext.start()
    // Let's await the stream to end - forever
    streamingContext.awaitTermination()

  }

  def stop(): Unit = {
    logger.info("Stopping Twitter Probe ...")
    streamingContext.stop(stopSparkContext = true,stopGracefully = true)
    logger.info("Twitter Probe successful stopped")

    vertx.close()
  }

}