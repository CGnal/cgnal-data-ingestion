package com.cgnal.twitter.probe.common.config

import com.cgnal.core.config._
import com.typesafe.config.Config

object TwitterProbeConfig extends HasConfiguration {

  lazy val configuration: Config = DefaultConfigHolder.configuration

  val defaultFilesKeywords  = "keywords.txt"
  val defaultDbName         = "documents-cache"

  lazy val keywordsFilename: String     = configuration.getString("files.keywords")
  lazy val documentsDbName : String     = configuration.getString("documents.dbName")

  lazy val twitterConsumerKey : String        = configuration.getString("twitter.consumerKey")
  lazy val twitterConsumerSecret : String     = configuration.getString("twitter.consumerSecret")
  lazy val twitterAccessToken : String        = configuration.getString("twitter.accessToken")
  lazy val twitterAccessTokenSecret : String  = configuration.getString("twitter.accessTokenSecret")

  lazy val restPort: Int     = configuration.getInt("rest.port")

  lazy val streamingProcessingWindow: Int = configuration.getInt("streaming.processingWindow")

  lazy val withoutSymbolsAndHashTags : Boolean = configuration.getBoolean("filters.withoutSymbolsAndHashTags")

  lazy val configurationAsMap: Map[String, Any] = configuration.flattenToMap

}