package com.cgnal.data.probe

import io.vertx.core.Vertx

trait DataProbe {

  protected val vertx : Vertx = Vertx.vertx()

  def name : String

  def start() : Unit

  def stop() : Unit

}
