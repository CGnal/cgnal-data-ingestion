package com.cgnal.twitter.probe.recovery

import java.util.concurrent.LinkedBlockingQueue
import java.util.{Date, UUID}

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import com.cgnal.twitter.probe.common.loader.KeywordsLoader
import com.cgnal.twitter.probe.model.TwitterProbeIteration
import org.apache.ignite.IgniteCache
import twitter4j.Twitter

import scala.collection.JavaConversions._

class TwitterRecoveryRequestConsumer(twitter: Twitter, requests : LinkedBlockingQueue[TwitterRecoveryRequest], documentsCache : IgniteCache[String,Document], iterationCache : IgniteCache[UUID,TwitterProbeIteration])
  extends Runnable
  with KeywordsLoader
  with BaseLogging {

    override def run(): Unit = {
      while(true){
        logger.info(s"Processing requests queue current size ${requests.size()}")
        logger.info(s"Waiting to process ...")
        val currentQuery = requests.take()
        consume(currentQuery)
      }
    }

    def consume(request : TwitterRecoveryRequest): Unit ={

      try {

        import com.cgnal.twitter.probe.common.TweetsUtils._
        val checkTime = (TwitterProbeConfig.streamingProcessingWindow - (5 * TwitterProbeConfig.streamingProcessingWindow / 100)) * 1000

        logger.info(s"Call query ${request.name} with query ${request.query.getQuery} sinceId : ${request.query.getSinceId} and maxId : ${request.query.getMaxId}")
        val result = twitter.search(request.query)
        logger.info(s"Query ${request.name} has ${result.getTweets.size()} results")

        val saved = result.getTweets.toList
          .filter( containsSymbolsOrHashTags(allSymbols , allHashTags , TwitterProbeConfig.withoutSymbolsAndHashTags) )
          .map(tweet => {
            logger.debug(s"Saving Tweet : ${tweet.getId} at ${tweet.getCreatedAt.getTime}")
            if (documentsCache.containsKey(tweet.getId.toString)) {
              logger.warn(s"Tweet ${tweet.getId} already present in the cache")
            }

            documentsCache.put(tweet.getId.toString, toDocument(tweet))
            tweet
          }).sortBy(_.getCreatedAt.getTime)


        if (saved.nonEmpty) {
          val minTweet = saved.head
          val maxTweet = saved.last

          logger.debug(s"TimeRef is ${request.timeRef} Min Tweet is at ${minTweet.getCreatedAt.getTime} and Max Tweet is at ${maxTweet.getCreatedAt.getTime}")

          var time = request.timeRef
          logger.debug(s"Current TimeRef is ${new Date(request.timeRef)}")

          var lastTime = if (minTweet.getCreatedAt.getTime - time > 0) minTweet.getCreatedAt.getTime else time

          var minTweetId = minTweet.getId
          var maxTweetId = minTweet.getId

          var currentBlock = 1
          var count = 0

          val firstInterval = minTweet.getCreatedAt.getTime - time
          logger.debug(s"first interval is $firstInterval with checkTime $checkTime")

          val emptyBlocks = firstInterval / checkTime

          // Empty initial blocks
          (0 until emptyBlocks.toInt).seq.foreach(idx => {
            logger.warn(s"No tweets in the block time insert empty block $idx")
            val uuid = UUID.randomUUID

            lastTime = time + checkTime
            // Saving
            iterationCache.put(uuid, TwitterProbeIteration(uuid, request.name, lastTime, request.query.getSinceId, request.query.getSinceId, count, recovery = true))

            time = lastTime
            logger.debug(s"Advancing time to ${new Date(time)}")

            currentBlock = currentBlock + 1
          })

          saved.seq.foreach(s => {

            logger.info(s"Getting tweet at ${s.getCreatedAt} - ${s.getCreatedAt.getTime} and reference is $time with diff ${s.getCreatedAt.getTime - time} [$checkTime]")

            if (s.getCreatedAt.getTime - time < 0) {
              // Discard previous tweets
              logger.warn("Tweet is out of temporal window!")

            } else if (s.getCreatedAt.getTime - time < checkTime) {
              // Inside the current block
              logger.debug(s"Adding tweet to block $currentBlock")
              count = count + 1

              // Advance timeline
              lastTime = s.getCreatedAt.getTime
              maxTweetId = s.getId
              logger.debug(s"Tweet ID : ${s.getId} with total diff ${s.getCreatedAt.getTime - request.timeRef}")

            } else {
              // Distance between two blocks more than temporal window
              logger.debug(s"Skipping tweet to next block ${currentBlock + 1}")

              currentBlock = currentBlock + 1

              val uuid = UUID.randomUUID
              val timeDiff = lastTime - time

              // Saving previous bloc data
              logger.debug(s"Saving in block $currentBlock Iteration $uuid with maxId : ${maxTweet.getId} at $lastTime and diff $timeDiff")
              iterationCache.put(uuid, TwitterProbeIteration(uuid, request.name, lastTime, minTweetId, maxTweetId, count, recovery = true))

              // New references
              time = s.getCreatedAt.getTime
              logger.debug(s"Advancing time to ${new Date(time)}")
              minTweetId = s.getId
              count = 1

              // Advance timeline
              lastTime = s.getCreatedAt.getTime
              maxTweetId = s.getId
              logger.debug(s"Tweet ID : ${s.getId} with total diff ${s.getCreatedAt.getTime - request.timeRef}")

            }

          })

          // Save last records
          if (count > 0) {

            val uuid = UUID.randomUUID
            val timeDiff = lastTime - time

            // Saving
            logger.debug(s"Saving Last Iteration $uuid on maxId : ${maxTweet.getId} at $lastTime with diff $timeDiff")
            iterationCache.put(uuid, TwitterProbeIteration(uuid, request.name, lastTime, minTweetId, maxTweetId, count , recovery = true))

          }

          if (result.hasNext) {
            requests.put(TwitterRecoveryRequest(request.name, lastTime, result.nextQuery))
          }

        } else {
          // Empty search query results
          logger.warn(s"Results for query ${request.name} are empty! ")

          val uuid = UUID.randomUUID
          val time = request.timeRef.+(checkTime)

          // Saving
          logger.debug(s"Saving empty iteration $uuid with maxId : ${request.query.getMaxId} at $time and ref ${request.timeRef}")
          iterationCache.put(uuid, TwitterProbeIteration(uuid, request.name, time, request.query.getMaxId, request.query.getMaxId, result.getTweets.size, recovery = true))

        }

        Thread.sleep(TwitterProbeConfig.twitterSearchDelayTime)

      } catch {
        case t : Throwable => logger.error(t.getMessage)
      }
    }

}
