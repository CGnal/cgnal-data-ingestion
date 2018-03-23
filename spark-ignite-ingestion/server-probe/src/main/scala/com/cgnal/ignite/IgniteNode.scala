package com.cgnal.ignite

import com.cgnal.core.config._
import com.cgnal.core.logging.BaseLogging
import com.cgnal.web.rest.{HasVertx, RestMetadata, RestStatus}
import com.typesafe.config.Config
import org.apache.ignite.{Ignite, Ignition}

class IgniteNode
  extends BaseLogging
    with HasVertx{

  lazy val configuration: Config = DefaultConfigHolder.configuration

  protected var ignite : Ignite = _

  def start(): Unit = {
    logger.info("Starting ignite server node ..")

    vertx.deployVerticle(new IgniteNodeRest("Ignite Server Node", configuration.get[Int]("rest.port"), RestMetadata("Ignite Server Node",RestStatus.OK) , configuration.flattenToMap))

    ignite = Ignition.start("ignite-config.xml")

  }

  def stop() : Unit = {

    logger.info("Stopping ignite server node ..")

    ignite.close()

    logger.info("ignite server node stopped")

    vertx.close()
  }

}
