package com.cgnal.data.probe

import com.cgnal.web.rest._
import io.vertx.ext.web.Router

class DataProbeRest( properties : DataProbeProperties ) extends RestVerticle(properties.vertxPort){

  val healthEndpoint : String = "{ \"name\" : \"" + properties.name + "\" , \"status\" : \"OK\" }"

  override def addRoutes(router: Router): Unit = {
    router.get("/health").handler(generateJsonResponseHandler(healthEndpoint))
  }

}
