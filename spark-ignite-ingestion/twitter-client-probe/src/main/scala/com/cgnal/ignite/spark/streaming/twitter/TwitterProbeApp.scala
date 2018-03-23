package com.cgnal.ignite.spark.streaming.twitter

object TwitterProbeApp extends App {

  val probe = new TwitterProbe

  Runtime.getRuntime.addShutdownHook( new Thread(new Runnable {
    override def run(): Unit = probe.stop()
  }))

  probe.start()

}
