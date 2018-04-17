package com.cgnal.twitter.probe.common

import java.io.File

import com.cgnal.core.logging.BaseLogging
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig

import scala.io.Source

trait SearchQueryLoader {
  self : BaseLogging =>

  private lazy val allLines: Seq[String] = {
    val searchQueriesFile = new File(TwitterProbeConfig.searchQueriesFilename)
    if (searchQueriesFile.exists()) {
      logger.info(s"Loading searchQueries file $searchQueriesFile ..")
      Source.fromFile(searchQueriesFile).getLines().toSeq
    } else {
      logger.warn(s"SearchQueries file $searchQueriesFile not found !!")
      //Seq.empty[String]
      Seq("search-01,$aapl OR #appleinc OR $googl OR #google OR $goog OR #google OR $msft OR #microsoft OR $amzn OR #amazon")
    }
  }

  protected lazy val allQueries: Seq[NamedSearchQuery] = {
    allLines.map( line => {
      val Array(name: String, query: String, _*) = line.split(",")
      NamedSearchQuery(name, query)
    })
  }

  protected lazy val allQueriesMap : Map[String,String] = {
    allQueries.map( q =>  q.name -> q.query ).toMap
  }

}

case class NamedSearchQuery(name : String, query : String)
