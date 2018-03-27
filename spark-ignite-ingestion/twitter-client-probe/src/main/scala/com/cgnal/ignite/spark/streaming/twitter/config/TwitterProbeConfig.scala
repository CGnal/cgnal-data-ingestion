package com.cgnal.ignite.spark.streaming.twitter.config

import com.typesafe.config.{Config, ConfigFactory}

object TwitterProbeConfig {

  protected lazy val configuration : Config = ConfigFactory.load

  lazy val keywordsFilename: String = configuration.getString("files.keywords")

  lazy val documentsCollectionName : String = configuration.getString("documents.collectionName")

  lazy val twitterConsumerKey : String        = configuration.getString("twitter.consumerKey")
  lazy val twitterConsumerSecret : String     = configuration.getString("twitter.consumerSecret")
  lazy val twitterAccessToken : String        = configuration.getString("twitter.accessToken")
  lazy val twitterAccessTokenSecret : String  = configuration.getString("twitter.accessTokenSecret")

}
