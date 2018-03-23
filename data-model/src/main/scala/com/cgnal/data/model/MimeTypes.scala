package com.cgnal.data.model

case class MimeTypes(primary : String, secondary : String)


object MimeTypes {

  val textPlain = MimeTypes("text","plain")
  val textXml = MimeTypes("text","xml")
  val applicationXml =  MimeTypes("application","xml")
  val applicationJson = MimeTypes("application","json")
  val applicationRssFeed = MimeTypes("application","rss+xml")

}
