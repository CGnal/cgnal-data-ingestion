name := "server-probe"

version := "1.0.0-SNAPSHOT"

scalaVersion := "2.11.8"

resolvers ++= Seq(
  "GridGain Repository" at "http://www.gridgainsystems.com/nexus/content/repositories/external/"
)

libraryDependencies ++= {
  val igniteV           = "2.4.0"
  val scalaConfigV      = "1.3.1"
  val scalaTestV        = "3.0.1"
  val scalaLoggingV     = "3.7.2"
  val logbackV          = "1.2.3"
  Seq(
    "com.cgnal" %% "cgnal-core" % "1.0.0-SNAPSHOT",
    "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
    "com.cgnal" %% "data-access-ignite-mongo" % "1.0.0-SNAPSHOT",
    "org.apache.ignite" % "ignite-core" % igniteV ,
    "org.apache.ignite" % "ignite-spring" % igniteV ,
    "com.typesafe" % "config" % scalaConfigV ,
    "com.typesafe.scala-logging" %% "scala-logging" % scalaLoggingV ,
    "ch.qos.logback" % "logback-classic" % logbackV ,
    "org.scalatest" %% "scalatest" % scalaTestV % "test"
  )
}

