package com.cgnal.twitter.probe.ignite.spark.streaming

import com.cgnal.core.logging.BaseLogging
import com.cgnal.twitter.probe.common.TwitterProbeRuntime
import org.apache.spark.streaming.scheduler.{StreamingListener, StreamingListenerBatchCompleted}

class TwitterProbeListener(runtime : TwitterProbeRuntime)
  extends StreamingListener with BaseLogging {

  override def onBatchCompleted(batchCompleted: StreamingListenerBatchCompleted): Unit = {
    logger.debug(s"Batch successful completed at ${batchCompleted.batchInfo.batchTime.milliseconds}")
    runtime.updateTime()
    runtime.updateTweetsCount(batchCompleted.batchInfo.numRecords)
  }


}
