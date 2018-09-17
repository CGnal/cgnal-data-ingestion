package com.cgnal.twitter.probe.ignite.spark.streaming

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.TwitterProbeRuntime
import com.cgnal.twitter.probe.common.cache.CacheConfig
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import org.apache.ignite.{Ignite, IgniteCache}
import org.apache.ignite.cache.query.ScanQuery
import org.apache.ignite.lang.IgniteBiPredicate
import org.apache.spark.streaming.scheduler.{StreamingListener, StreamingListenerBatchCompleted}

class TwitterClientProbeListener(runtime : TwitterProbeRuntime, ignite : Ignite)
  extends StreamingListener
    with CacheConfig
    with BaseLogging {

  val documentsCache : IgniteCache[String,Document] = ignite.getOrCreateCache(createDocumentCacheConfig)

  override def onBatchCompleted(batchCompleted: StreamingListenerBatchCompleted): Unit = {
    logger.debug(s"Batch successful completed at ${batchCompleted.batchInfo.batchTime.milliseconds}")
    runtime.updateTime()
    runtime.updateTweetsCount(batchCompleted.batchInfo.numRecords)


    if (TwitterProbeConfig.metricsEnabled) {
      // Get the metrics of all the memory regions defined on the node.
      val metrics = ignite.dataRegionMetrics("default")

      logger.info(" ============ DATA REGION ============= ")
      logger.info(">>> Memory Region Name: " + metrics.getName)
      logger.info(">>> Physical Memory Size: " + metrics.getPhysicalMemorySize / (1024 * 1024) + " MB")
      logger.info(">>> Total Allocated Memory Size: " + metrics.getTotalAllocatedSize / (1024 * 1024) + " MB")
      logger.info(">>> Allocation Rate: " + metrics.getAllocationRate)
      logger.info(">>> Fill Factor: " + metrics.getPagesFillFactor)

    }

    // For expiry to be applied
    val q = new ScanQuery[String, Document](filter)
    val results = documentsCache.query(q).getAll
    logger.info("Query result size : " + results.size())

  }

  private def filter : IgniteBiPredicate[String,Document] = new IgniteBiPredicate[String,Document] {
    override def apply(s : String ,e: Document): Boolean = true
  }



}
