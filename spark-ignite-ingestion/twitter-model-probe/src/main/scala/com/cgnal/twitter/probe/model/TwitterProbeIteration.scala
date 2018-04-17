package com.cgnal.twitter.probe.model

import java.util.UUID

case class TwitterProbeIteration(id : UUID , name : String , lastUpdateTime : Long ,  minTweetID : Long ,maxTweetID : Long , tweetsCount : Int, recovery : Boolean = false)
