package com.cgnal.ignite

import com.typesafe.scalalogging.StrictLogging
import org.apache.ignite.{Ignite, Ignition}

class IgniteNode extends StrictLogging {

  protected var ignite : Ignite = _

  def start(): Unit = {
    ignite = Ignition.start("ignite-config.xml")

  }

  def stop() : Unit = {
    ignite.close()
  }

}
