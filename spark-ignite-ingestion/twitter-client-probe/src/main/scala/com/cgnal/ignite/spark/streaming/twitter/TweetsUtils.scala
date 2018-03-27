package com.cgnal.ignite.spark.streaming.twitter

import java.util.Date

import com.cgnal.data.model._
import com.cgnal.utility.DateTimeUtility
import twitter4j.Status

object TweetsUtils {

  // Some type aliases to give a little bit of context
  type TTweet = Status
  type TTweetText = String


  private def formatPublishDay(date : Date)   : Long    = DateTimeUtility.dateTimeFormatter(DateTimeUtility.PublishDayFormat).format(date).toLong
  private def formatPublishDate(date : Date)  : String  = DateTimeUtility.dateTimeFormatter(DateTimeUtility.PublishDateFormat).format(date)

  private def formatTimeWindow(date : Date)   : Long    = DateTimeUtility.dateTimeFormatter("yyyyMMddHHmm").format(date).toLong

  def toDocument : TTweet => Document = tweet => {
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
  }


}
