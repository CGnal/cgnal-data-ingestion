package com.cgnal.twitter.probe.recovery

object TwitterRecoveryProbeApp extends App {

  val probe = new TwitterRecoveryProbe

  Runtime.getRuntime.addShutdownHook( new Thread(new Runnable {
    override def run(): Unit = probe.stop()
  }))

  probe.start()

}
