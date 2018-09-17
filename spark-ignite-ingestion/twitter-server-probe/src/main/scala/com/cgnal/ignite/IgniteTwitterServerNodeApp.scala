package com.cgnal.ignite

object IgniteTwitterServerNodeApp extends App {

  val node = new IgniteTwitterServerNode

  Runtime.getRuntime.addShutdownHook( new Thread(new Runnable {
    override def run(): Unit = node.stop()
  }))

  node.start()

}
