package com.cgnal.data.probe

case class DataProbeProperties(name : String , vertxPort : Int, startDateTime : Long = System.currentTimeMillis)