package com.cgnal.ignite

import com.cgnal.web.rest._
import io.vertx.ext.web.Router

class IgniteTwitterServerNodeRest(name : String, vertxPort : Int, metadata: RestMetadata, configuration : Map[String,Any])
  extends BaseRestService(name, vertxPort, metadata , configuration){

  override def addCustomRoutes(router: Router): Unit = {

  }

}
