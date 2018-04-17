package com.cgnal.twitter.probe.search

import java.util.concurrent.LinkedBlockingQueue

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import org.apache.ignite.IgniteCache
import twitter4j.Query.ResultType
import twitter4j.{Query, Twitter}

import scala.collection.JavaConversions._

class TwitterSearchRequestConsumer(twitter: Twitter, requests : LinkedBlockingQueue[TwitterSearchRequest], documentsCache : IgniteCache[String,Document])
  extends Runnable
    with BaseLogging {

  override def run(): Unit = {
    while(true){
      val currentQuery = requests.take()
      consume(currentQuery)
    }
  }

  def consume(request : TwitterSearchRequest) : Unit = {

    import com.cgnal.twitter.probe.common.TweetsUtils._

    logger.info(s"Call query ${request.name} with query ${request.query.getQuery} sinceId : ${request.query.getSinceId} on maxId : ${request.query.getMaxId}")

    try {
      val result = twitter.search(request.query)

      val saved = result.getTweets.toList.map(tweet => {
        logger.info(s"Saving Tweet : ${tweet.getId} at ${tweet.getCreatedAt}")
        if (documentsCache.containsKey(tweet.getId.toString)) {
          logger.warn(s"Tweet ${tweet.getId} already present in the cache")
        }

        documentsCache.put(tweet.getId.toString, toDocument(tweet))
        tweet
      }).sortBy(_.getId)

      logger.info(s"------------------------------------------------------")
      logger.info(s"Result size for query ${request.name} : ${result.getTweets.size}")

      //    if (result.hasNext) {
      //      logger.info("Including next query ")
      //      requests.put(TwitterSearchRequest(request.name ,result.nextQuery))
      //    }
      //    } else if (saved.head.getId <= maxId) {
      //
      if (saved.nonEmpty) {
        val query = new Query()
        query.setLang(request.query.getLang)
        query.setQuery(request.query.getQuery)
        query.setCount(100)
        query.setResultType(ResultType.mixed)
        query.setSinceId(request.query.getSinceId)
        query.setMaxId(saved.head.getId - 1)

        requests.put(TwitterSearchRequest(request.name, query))
      }
      //    }
    } catch {
      case _: Throwable => {
        logger.warn(s"Request query $request failed!")
        requests.put(request)
      }
    }

    Thread.sleep(TwitterProbeConfig.twitterSearchDelayTime)

  }
}
