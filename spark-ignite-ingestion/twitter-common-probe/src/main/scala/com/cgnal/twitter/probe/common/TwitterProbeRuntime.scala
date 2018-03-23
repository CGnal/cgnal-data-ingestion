package com.cgnal.twitter.probe.common

class TwitterProbeRuntime {

  private var lastUpdateTime : Long   = System.currentTimeMillis
  private var keywords : Seq[String]  = Seq.empty
  private var tweetsRead : Long       = 0
  private var tweetsCount : Long      = 0

  def updateTime(time : Long = System.currentTimeMillis) : Unit = {
    this.lastUpdateTime = time
  }

  def updateKeywords(keywords : Seq[String]) : Unit = {
    this.keywords = keywords
  }

  def updateTweetsCount(count : Long) : Unit = {
    this.tweetsRead   = count
    this.tweetsCount  = this.tweetsCount + count
  }

  def getLastUpdateTime : Long = this.lastUpdateTime

  def getKeywords : Seq[String] = this.keywords

  def getTweetsRead : Long = this.tweetsRead

  def getTweetsCount : Long = this.tweetsCount

}
