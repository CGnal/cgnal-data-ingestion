package com.cgnal.data.access.ignite.mongo.config

import com.cgnal.core.config._
import com.typesafe.config.Config

object MongoStorageConfig  {

  protected val configuration : Config = DefaultConfigHolder.configuration

  lazy val mongoHost : String     = configuration.get[String]("mongo.host")
  lazy val mongoPort : Int        = configuration.get[Int]("mongo.port")
  lazy val mongoUser : String     = configuration.get[String]("mongo.user")
  lazy val mongoPassword : String = configuration.get[String]("mongo.password")


  lazy val documentsDbName: String = configuration.get[String]("documents.dbName")
}

