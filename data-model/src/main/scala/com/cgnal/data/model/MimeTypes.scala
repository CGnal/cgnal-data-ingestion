package com.cgnal.data.model

case class MimeType(primary : String, secondary : String)


object MimeTypes {

  val textPlain = MimeType("text","plain")
  val textXml = MimeType("text","xml")
  val applicationXml =  MimeType("application","xml")
  val applicationJson = MimeType("application","json")
  val applicationRssFeed = MimeType("application","rss+xml")

}
