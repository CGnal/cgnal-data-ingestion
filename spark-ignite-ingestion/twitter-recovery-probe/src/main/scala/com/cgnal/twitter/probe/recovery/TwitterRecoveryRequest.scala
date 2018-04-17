package com.cgnal.twitter.probe.recovery

import twitter4j.Query

case class TwitterRecoveryRequest(name : String, timeRef : Long, query : Query )
