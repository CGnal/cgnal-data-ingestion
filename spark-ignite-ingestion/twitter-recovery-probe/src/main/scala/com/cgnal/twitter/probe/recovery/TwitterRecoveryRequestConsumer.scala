package com.cgnal.twitter.probe.recovery

import java.util.UUID
import java.util.concurrent.LinkedBlockingQueue

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import com.cgnal.twitter.probe.model.TwitterProbeIteration
import org.apache.ignite.IgniteCache
import twitter4j.Twitter

import scala.collection.JavaConversions._

class TwitterRecoveryRequestConsumer(twitter: Twitter, requests : LinkedBlockingQueue[TwitterRecoveryRequest], documentsCache : IgniteCache[String,Document], iterationCache : IgniteCache[UUID,TwitterProbeIteration])
  extends Runnable
    with BaseLogging {

  override def run(): Unit = {
    while(true){
      val currentQuery = requests.take()
      consume(currentQuery)
    }
  }

  def consume(request : TwitterRecoveryRequest): Unit ={

    import com.cgnal.twitter.probe.common.TweetsUtils._
    val checkTime = TwitterProbeConfig.streamingProcessingWindow - (15 * TwitterProbeConfig.streamingProcessingWindow / 100)

    logger.debug(s"Call query ${request.name} with query ${request.query.getQuery} sinceId : ${request.query.getSinceId} on maxId : ${request.query.getMaxId}")

    val result = twitter.search(request.query)

    val saved  = result.getTweets.toList.map( tweet => {
      logger.debug(s"Saving Tweet : ${tweet.getId} at ${tweet.getCreatedAt.getTime}")
      if (documentsCache.containsKey(tweet.getId.toString)) {
        logger.warn(s"Tweet ${tweet.getId} already present in the cache")
      }

      documentsCache.put( tweet.getId.toString ,toDocument(tweet))
      tweet
    }).sortBy(_.getCreatedAt.getTime)


    if (saved.nonEmpty) {
      val minTweet = saved.head
      val maxTweet = saved.last

      var time = request.timeRef

      var lastTime    = minTweet.getCreatedAt.getTime
      var minTweetId  = minTweet.getId

      var maxTweetId = minTweet.getId

      var currentBlock = 1
      var count = 0

      saved.foreach(s => {
          if (s.getCreatedAt.getTime - time < checkTime ) {
            count = count + 1
          } else {

            currentBlock = currentBlock + 1

            val uuid      = UUID.randomUUID
            val timeDiff  = lastTime - time

            // Saving
            logger.debug(s"Saving Iteration $uuid on maxId : ${maxTweet.getId} at $lastTime with diff $timeDiff")
            iterationCache.put(uuid, TwitterProbeIteration(uuid, request.name, lastTime , minTweetId, maxTweetId, result.getTweets.size, recovery = true))

            // New references
            time       = s.getCreatedAt.getTime
            minTweetId = s.getId
            count      = 1
          }

          // Advance timeline
          lastTime    = s.getCreatedAt.getTime
          maxTweetId  = s.getId

          logger.debug(s"Tweet ID : ${s.getId} with diff ${s.getCreatedAt.getTime - request.timeRef}")
      })

      if (count > 0) {
        val uuid      = UUID.randomUUID
        val timeDiff  = lastTime - time

        // Saving
        logger.debug(s"Saving Last Iteration $uuid on maxId : ${maxTweet.getId} at $lastTime with diff $timeDiff")
        iterationCache.put(uuid, TwitterProbeIteration(uuid, request.name, lastTime , minTweetId , maxTweetId, result.getTweets.size, recovery = true))

      }

      logger.info(s"------------------------------------------------------")
      logger.info(s"Result size for query ${request.name} : ${result.getTweets.size}")

      if (result.hasNext) {
        requests.put(TwitterRecoveryRequest(request.name, lastTime ,result.nextQuery))
      }

    }

    Thread.sleep(TwitterProbeConfig.twitterSearchDelayTime)

  }

}
