package com.cgnal.twitter.probe.search

import java.util.concurrent.LinkedBlockingQueue

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.cache.CacheConfig
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import com.cgnal.twitter.probe.common.loader.{KeywordsLoader, SearchQueryLoader}
import org.apache.ignite.configuration.CacheConfiguration
import org.apache.ignite.{Ignite, IgniteCache, Ignition}
import twitter4j.Query.ResultType
import twitter4j.{Query, Twitter, TwitterFactory}

class TwitterSearchProbe extends CacheConfig
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

  val requests : LinkedBlockingQueue[TwitterSearchRequest] = new LinkedBlockingQueue[TwitterSearchRequest]
  val searchQueriesMap: Map[String, String] = allQueriesMap

  def start() : Unit = {
    logger.info("Starting Twitter Search Probe ...")
    ignite = Ignition.start(TwitterProbeConfig.igniteConfigFilename)

    val documentCacheCfg : CacheConfiguration[String, Document] = createDocumentCacheConfig
    val documentsCache : IgniteCache[String,Document] = ignite.getOrCreateCache(documentCacheCfg)

    // Consumer
    val consumer = new TwitterSearchRequestConsumer(twitter, requests, documentsCache)
    new Thread(consumer).start()

    allQueriesFromKeywords.foreach( q => requests.put(forgeQuery(q.name , q.query, TwitterProbeConfig.configuration.getLong("search.sinceId"),TwitterProbeConfig.configuration.getLong("search.maxId"))))

    while(true) {

      logger.info("Search Probe is processing .....")
      Thread.sleep(60000)

    }

  }

  def stop() : Unit = {

    ignite.close()

  }


  protected def forgeQuery(name: String, queryString : String , sinceId : Long, maxId : Long): TwitterSearchRequest = {
    val query = new Query()
    query.setLang(TwitterProbeConfig.documentsLanguage)
    query.setQuery(queryString)
    query.setCount(100)
    query.setResultType(ResultType.mixed)
    query.setSinceId(sinceId)
    query.setMaxId(maxId)

    TwitterSearchRequest(name, query)
  }

}

case class TwitterSearchRequest(name : String , query: Query)