package com.cgnal.ignite

object IgniteNodeApp extends App {

  val node = new IgniteNode

  Runtime.getRuntime.addShutdownHook( new Thread(new Runnable {
    override def run(): Unit = node.stop()
  }))

  node.start()

}
