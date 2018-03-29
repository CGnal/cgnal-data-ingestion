name := "data-probe"

version := "1.0.0-SNAPSHOT"

scalaVersion := "2.11.8"

libraryDependencies ++= {
  val vertxV            = "3.2.0"
  val scalaConfigV      = "1.3.1"
  val scalaTestV        = "3.0.1"
  val scalaLoggingV     = "3.7.2"
  val logbackV          = "1.2.3"
  Seq(
    "com.cgnal" %% "cgnal-core" % "1.0.0-SNAPSHOT",
    "com.cgnal" %% "cgnal-rest" % "1.0.0-SNAPSHOT",
    "io.vertx" % "vertx-web" % vertxV,
    "com.typesafe" % "config" % scalaConfigV ,
    "com.typesafe.scala-logging" %% "scala-logging" % scalaLoggingV ,
    "ch.qos.logback" % "logback-classic" % logbackV ,
    "org.scalatest" %% "scalatest" % scalaTestV % "test"
  )
}
