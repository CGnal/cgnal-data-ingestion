package com.cgnal.twitter.probe.search

object TwitterSearchProbeApp extends App {

  val probe = new TwitterSearchProbe

  Runtime.getRuntime.addShutdownHook( new Thread(new Runnable {
    override def run(): Unit = probe.stop()
  }))

  probe.start()
}
