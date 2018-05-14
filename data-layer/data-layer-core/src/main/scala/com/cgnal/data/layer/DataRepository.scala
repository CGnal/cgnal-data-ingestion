package com.cgnal.data.layer

import com.cgnal.core.logging.BaseLogging

trait DataRepository[K,A] extends BaseLogging {

  def configure(properties : Map[String,Any])

  def start() : Unit

  def stop() : Unit

  def isActive : Boolean = false

  def load(key : K) : Option[A]

  def write(element : A)  : Option[A]

  def delete(key : K) : Boolean

}

