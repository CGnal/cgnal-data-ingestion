name := "data-model"

version := "1.0.0-SNAPSHOT"

organization := "com.cgnal"

scalaVersion := "2.11.8"

libraryDependencies ++= {
  val shapelessV      = "2.3.2"
  val scalaTestV      = "3.0.1"
  val scalaLoggingV   = "3.7.2"
  val logbackV        = "1.2.3"
  Seq(
    "com.cgnal" %% "cgnal-core" % "1.0.0-SNAPSHOT",
    "com.chuusai" %% "shapeless" % shapelessV,
    "com.typesafe.scala-logging" %% "scala-logging" % scalaLoggingV ,
    "ch.qos.logback" % "logback-classic" % logbackV ,
    "org.scalatest" %% "scalatest" % scalaTestV % "test"
  )
}
