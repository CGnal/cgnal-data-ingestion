package com.cgnal.twitter.probe.common

import com.fasterxml.jackson.module.scala.DefaultScalaModule
import io.vertx.core.json.Json
import org.scalatest.FunSuite

final class TwitterProbeRestSpec
  extends FunSuite{

  Json.mapper.registerModule(DefaultScalaModule)

  test("TwitterProbeRuntime json serialization") {

    val runtime = new TwitterProbeRuntime
    runtime.updateTime(10000000000L)
    runtime.updateTweetsCount(100)

    val json = Json.encode(runtime)

    assert(json.equals("{\"lastUpdateTime\":10000000000,\"keywords\":[],\"tweetsRead\":100,\"tweetsCount\":100}"))
  }
}
