package com.cgnal.ignite

import com.cgnal.core.config._
import com.cgnal.core.logging.BaseLogging
import com.cgnal.web.rest.{HasVertx, RestMetadata, RestStatus}
import com.typesafe.config.Config
import org.apache.ignite.{Ignite, Ignition}

class IgniteTwitterServerNode
  extends BaseLogging
    with HasVertx{

  lazy val configuration: Config = DefaultConfigHolder.configuration

  protected var ignite : Ignite = _

  def start(): Unit = {
    logger.info("Starting ignite server node ..")

    vertx.deployVerticle(new IgniteTwitterServerNodeRest("Ignite Server Node", configuration.get[Int]("rest.port"), RestMetadata("Ignite Server Node",RestStatus.OK) , configuration.flattenToMap))

    ignite = Ignition.start(configuration.get[String]("ignite.configFilename"))

  }

  def stop() : Unit = {

    logger.info("Stopping ignite server node ..")

    ignite.close()

    logger.info("ignite server node stopped")

    vertx.close()
  }

}
