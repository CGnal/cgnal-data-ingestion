package com.cgnal.twitter.probe.common.config

import com.cgnal.core.config._
import com.typesafe.config.Config

object TwitterProbeConfig extends HasConfiguration {

  lazy val configuration: Config = DefaultConfigHolder.configuration

  val defaultFilesKeywords  = "keywords.txt"
  val defaultDbName         = "documents-cache"

  lazy val igniteConfigFilename : String    = configuration.getString("ignite.configFilename")

  lazy val cacheEvictionMaxSize : Int       = configuration.getInt("cache.evictionMaxSize")
  lazy val cacheWriteBehindFlushSize : Int  = configuration.getInt("cache.writeBehindFlushSize")

  lazy val keywordsFilename: String       = configuration.getString("files.keywords")
  lazy val searchQueriesFilename: String     = configuration.getString("files.searchQueries")

  lazy val documentsDbName : String     = configuration.getString("documents.dbName")
  lazy val documentsLanguage : String     = configuration.getString("documents.language")

  lazy val twitterConsumerKey : String        = configuration.getString("twitter.consumerKey")
  lazy val twitterConsumerSecret : String     = configuration.getString("twitter.consumerSecret")
  lazy val twitterAccessToken : String        = configuration.getString("twitter.accessToken")
  lazy val twitterAccessTokenSecret : String  = configuration.getString("twitter.accessTokenSecret")

  lazy val twitterSearchDelayTime : Long      = configuration.getLong("twitter.searchDelayTime")

  lazy val restPort: Int     = configuration.getInt("rest.port")

  lazy val streamingProcessingWindow: Int = configuration.getInt("streaming.processingWindow")

  lazy val recoveryEnabled : Boolean = configuration.getBoolean("recovery.enabled")
  lazy val recoveryProcessingWindow: Int = configuration.getInt("recovery.processingWindow")


  lazy val withoutSymbolsAndHashTags : Boolean = configuration.getBoolean("filters.withoutSymbolsAndHashTags")

  lazy val configurationAsMap: Map[String, Any] = configuration.flattenToMap

}