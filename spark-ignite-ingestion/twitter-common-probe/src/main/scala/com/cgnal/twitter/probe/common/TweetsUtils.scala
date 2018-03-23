package com.cgnal.twitter.probe.common

import java.util.Date

import com.cgnal.core.utility.datetime.DateTimeUtility
import com.cgnal.data.model._
import com.fasterxml.jackson.databind.ObjectMapper
import twitter4j.Status

object TweetsUtils {

  // Some type aliases to give a little bit of context
  type TTweet = Status
  type TTweetText = String

  protected val jsonObjectMapper = new ObjectMapper

  private def formatPublishDay(date : Date)   : Long    = DateTimeUtility.dateTimeFormatter(DateTimeUtility.PublishDayFormat).format(date).toLong
  private def formatPublishDate(date : Date)  : String  = DateTimeUtility.dateTimeFormatter(DateTimeUtility.PublishDateFormat).format(date)

  private def formatTimeWindow(date : Date)   : Long    = DateTimeUtility.dateTimeFormatter("yyyyMMddHHmm").format(date).toLong

  def toDocument : TTweet => Document = tweet => {

    val status: String = jsonObjectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(tweet)

    Document(tweet.getId.toString, Map.empty, DocumentBody(Some(MimeTypes.applicationJson),tweet.getText.getBytes("UTF-8")))
      .withProperty(DocumentProperties.Language, tweet.getLang)
      .withProperty(DocumentProperties.PublishDay , formatPublishDay(tweet.getCreatedAt))
      .withProperty(DocumentProperties.PublishDate , formatPublishDate(tweet.getCreatedAt))
      .withProperty(DocumentProperties.Text, tweet.getText)
      .withProperty("UserId" , tweet.getUser.getId)
      .withProperty(DocumentProperties.SourceType, SourceTypes.Twitter)
      .withProperty(DocumentProperties.SourceName, tweet.getUser.getName)
      .withProperty("Symbols" , tweet.getSymbolEntities.map( symbol => symbol.getText).toList)
      .withProperty("HashTags" , tweet.getHashtagEntities.map( hashtag => hashtag.getText).toList)
      .withProperty("Status", status)
  }


  def containsSymbolsOrHashTags( allSymbols : Seq[String], allHashTags : Seq[String], withoutSymbolsAndHashTags : Boolean) : TTweet => Boolean = {
    t => withoutSymbolsAndHashTags || t.getSymbolEntities.exists( s => allSymbols.contains(s.getText.trim.toLowerCase) ) || t.getHashtagEntities.exists( h => allHashTags.contains(h.getText.trim.toLowerCase) )
  }


}
