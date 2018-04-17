package com.cgnal.twitter.probe.search

import java.io.{File, PrintWriter}

import com.cgnal.core.logging.BaseLogging
import com.cgnal.twitter.probe.common.NamedSearchQuery

import scala.io.Source

object TwitterSearchQueryGeneratorApp
  extends App with BaseLogging {

  private  lazy val allLines: Seq[String] = {
    val keywordsFile = new File("/Volumes/Data/development/workspaces/cgnal/scala/cgnal-data-ingestion/spark-ignite-ingestion/twitter-search-probe/keywords-239.csv")
    if (keywordsFile.exists()) {
      logger.info(s"Loading keywords file $keywordsFile ..")
      Source.fromFile(keywordsFile).getLines().toSeq
    } else {
      logger.warn(s"Keywords file $keywordsFile not found !!")
      //Seq.empty[String]
      Seq("APPL,apple", "FB,facebook")
    }
  }

  protected def allQueriesFromKeywords : Seq[NamedSearchQuery] = {
    allLines.map(line => {
      val Array(key: String, name: String, _*) = line.split(",")
      NamedSearchQuery("search-" + name.toLowerCase,"$" + key.toLowerCase + " OR " + "#" + name.toLowerCase)
    })
  }

  // PrintWriter
  val pw = new PrintWriter(new File("/Volumes/Data/development/workspaces/cgnal/scala/cgnal-data-ingestion/spark-ignite-ingestion/twitter-search-probe/search-query-239.csv" ))
  allQueriesFromKeywords.foreach( x => {
    pw.println(x.name + "," + x.query)
  })
  pw.close

}
