package com.cgnal.twitter.probe.common

import java.io.File

import com.cgnal.core.logging.BaseLogging
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import twitter4j.FilterQuery

import scala.io.Source

trait KeywordsLoader {
  self : BaseLogging =>

  protected def keywordsFilter( keywords : Seq[String]): FilterQuery = new FilterQuery()
    .language("en")
    .track(keywords : _*)

  private lazy val allLines: Seq[String] = {
    val keywordsFile = new File(TwitterProbeConfig.keywordsFilename)
    if (keywordsFile.exists()) {
      logger.info(s"Loading keywords file $keywordsFile ..")
      Source.fromFile(keywordsFile).getLines().toSeq
    } else {
      logger.warn(s"Keywords file $keywordsFile not found !!")
      //Seq.empty[String]
      Seq("APPL,apple", "FB,facebook")
    }
  }

  protected def allSymbols: Seq[String] = {
    allLines.map(line => {
      val Array(key: String, _*) = line.split(",")
      key.toLowerCase.replace("\"", "")
    })
  }

  protected def allHashTags : Seq[String] = {
    allLines.map(line => {
      val Array(key: String, name: String, _*) = line.split(",")
      name.toLowerCase.replace("\"", "")
    })
  }

  protected def allKeywords: Seq[String] = {
    allLines.flatMap(line => {
      val Array(key: String, name: String, _*) = line.split(",")
      List("$" + key.toLowerCase.replace("\"", ""), "#" + name.toLowerCase.replace("\"", ""))
    })

  }
}
