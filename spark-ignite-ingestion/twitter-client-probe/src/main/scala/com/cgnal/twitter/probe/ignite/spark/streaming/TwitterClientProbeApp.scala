package com.cgnal.twitter.probe.ignite.spark.streaming

object TwitterClientProbeApp extends App {

  val probe = new TwitterProbe

  Runtime.getRuntime.addShutdownHook( new Thread(new Runnable {
    override def run(): Unit = probe.stop()
  }))

  probe.start()

}
