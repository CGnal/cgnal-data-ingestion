package com.cgnal.twitter.probe.recovery

import java.util.UUID
import java.util.concurrent.LinkedBlockingQueue

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model._
import com.cgnal.twitter.probe.common.cache.CacheConfig
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import com.cgnal.twitter.probe.common.{KeywordsLoader, SearchQueryLoader}
import com.cgnal.twitter.probe.model.TwitterProbeIteration
import com.cgnal.web.rest.HasVertx
import org.apache.ignite.cache.query.ScanQuery
import org.apache.ignite.configuration.CacheConfiguration
import org.apache.ignite.lang.IgniteBiPredicate
import org.apache.ignite.{Ignite, IgniteCache, Ignition}
import twitter4j.{Query, Twitter, TwitterFactory}

import scala.collection.JavaConversions._

class TwitterRecoveryProbe
  extends CacheConfig
    with HasVertx
    with KeywordsLoader
    with SearchQueryLoader
    with BaseLogging {


  protected var ignite : Ignite = _

  Ignition.setClientMode(true)

  // Set the system properties so that Twitter4j library used by Twitter stream
  // can use them to generate OAuth credentials
  System.setProperty("twitter4j.oauth.consumerKey", TwitterProbeConfig.twitterConsumerKey)
  System.setProperty("twitter4j.oauth.consumerSecret", TwitterProbeConfig.twitterConsumerSecret)
  System.setProperty("twitter4j.oauth.accessToken", TwitterProbeConfig.twitterAccessToken)
  System.setProperty("twitter4j.oauth.accessTokenSecret", TwitterProbeConfig.twitterAccessTokenSecret)

  val twitter: Twitter = new TwitterFactory().getInstance

  val requests : LinkedBlockingQueue[TwitterRecoveryRequest] = new LinkedBlockingQueue[TwitterRecoveryRequest]
  val serachQueriesMap: Map[String, String] = allQueriesMap

  def start() : Unit = {

    logger.info("Starting Twitter Recovery Probe ...")
    ignite = Ignition.start(TwitterProbeConfig.igniteConfigFilename)

    val documentCacheCfg : CacheConfiguration[String, Document] = createDocumentCacheConfig
    val documentsCache : IgniteCache[String,Document] = ignite.getOrCreateCache(documentCacheCfg)

    val iterationCacheCfg : CacheConfiguration[UUID, TwitterProbeIteration] = createIterationCacheConfig
    val iterationsCache : IgniteCache[UUID,TwitterProbeIteration] = ignite.getOrCreateCache(iterationCacheCfg)


    def predicate(timeRef : Long) : IgniteBiPredicate[UUID,TwitterProbeIteration] = new IgniteBiPredicate[UUID,TwitterProbeIteration] {
      override def apply(e1: UUID, e2: TwitterProbeIteration): Boolean = {
        e2.lastUpdateTime < timeRef //&& e2.lastUpdateTime < (timeRef - 3600000)
      }
    }

    val checkTime = TwitterProbeConfig.streamingProcessingWindow + (5 * TwitterProbeConfig.streamingProcessingWindow / 100)

    // Consumer
    val consumer = new TwitterRecoveryRequestConsumer(twitter, requests, documentsCache , iterationsCache)
    new Thread(consumer).start()

    // Producer
    while(true) {
      val currentTime  = System.currentTimeMillis

      logger.info(s"Executing check on time $currentTime")

      val q = new ScanQuery[UUID, TwitterProbeIteration](predicate(currentTime))
      val results = iterationsCache.query(q).getAll

      results.toList
        .sortBy(- _.getValue.lastUpdateTime)
/*       .map( x => {
          logger.info(s"Time : ${x.getValue.lastUpdateTime} ID ${x.getKey} min : ${x.getValue.minTweetID} and max : ${x.getValue.maxTweetID}")
          x
        })*/
        .foldLeft(Sequence(Seq.empty[Slide], null ,currentTime))((s : Sequence, i) => s.copy(slices = s.slices :+ Slide(i.getKey , s.lastRefId , i.getValue.name ,s.lastTimeRef - i.getValue.lastUpdateTime), lastRefId = i.getKey ,lastTimeRef = i.getValue.lastUpdateTime))
        .slices
//        .map( x => {
//            logger.info(s"Slice : $x")
//            x
//          }
//        )
        .filter(s => s.time > checkTime && s.refId != null)
        .foreach(s => {
          logger.debug(s"Slides : [${s.id} - ${s.refId}] at time ${s.time}")

          val upperIteration  = iterationsCache.get(s.id)
          val startSlide      = upperIteration.maxTweetID
          val bottomIteration = iterationsCache.get(s.refId)
          val endSlide        = bottomIteration.minTweetID - 1

          logger.debug(s"Tweet search by keywords for window $startSlide - $endSlide with reference time ${upperIteration.lastUpdateTime}")

          val query = allQueriesMap.get(s.name)

          if (query.isDefined) {
            requests.put(forgeQuery(s.name, query.get , upperIteration.lastUpdateTime, startSlide, endSlide))
          }

        })

      Thread.sleep(TwitterProbeConfig.recoveryProcessingWindow)
    }

  }


  def stop() : Unit = {
    ignite.close()

    vertx.close()
  }

  protected def forgeQuery(name: String, queryString : String , timeRef : Long , startSlide : Long, endSlide : Long): TwitterRecoveryRequest = {
    val query = new Query()

    query.setLang(TwitterProbeConfig.documentsLanguage)
    query.setQuery(queryString)
    query.setCount(100)
    query.setSinceId(startSlide)
    query.setMaxId(endSlide)

    TwitterRecoveryRequest(name, timeRef ,query)
  }



}



case class Slide(id : UUID, refId : UUID, name : String , time : Long )
case class Sequence(slices : Seq[Slide], lastRefId : UUID , lastTimeRef : Long)

