package com.cgnal.twitter.probe.common

import com.cgnal.web.rest._
import io.vertx.core.json.Json
import io.vertx.ext.web.{Router, RoutingContext}

class TwitterProbeRest (name : String, vertxPort : Int, metadata: RestMetadata, configuration : Map[String,Any], runtime: TwitterProbeRuntime)
  extends BaseRestService(name, vertxPort, metadata , configuration ){

  def runtimeEndpoint(runtime: TwitterProbeRuntime) : String = {
    Json.encodePrettily(runtime)
  }

  override def addCustomRoutes(router: Router): Unit = {

    router
      .get("/runtime")
      .produces("application/json")
      .handler(
        (rc: RoutingContext) => {
          logger.debug(s"Call runtime API on ${metadata.name}")
          rc.response().setStatusCode(200).end(runtimeEndpoint(runtime))
        }
      )

  }

}
