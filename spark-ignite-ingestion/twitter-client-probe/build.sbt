name := "twitter-client-probe"

version := "1.0.0-SNAPSHOT"

scalaVersion := "2.11.8"

resolvers ++= Seq(
  "GridGain Repository" at "http://www.gridgainsystems.com/nexus/content/repositories/external/"
)

libraryDependencies ++= {
  val mongoScalaDriverV = "2.2.1"
  val igniteV           = "2.4.0"
  val sparkV            = "2.2.0"
  val scalaConfigV      = "1.3.1"
  val scalaTestV        = "3.0.1"
  val scalaLoggingV     = "3.7.2"
  val logbackV          = "1.2.3"
  Seq(
    "com.cgnal" %% "cgnal-core" % "1.0.0-SNAPSHOT",
    "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
    "com.cgnal" %% "data-access-ignite-mongo" % "1.0.0-SNAPSHOT",
    "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.6.5",
    "org.mongodb.scala" %% "mongo-scala-driver" % mongoScalaDriverV ,
    "org.apache.ignite" % "ignite-core" % igniteV ,
    "org.apache.ignite" % "ignite-spring" % igniteV ,
    "org.apache.ignite" % "ignite-spark" % igniteV excludeAll ExclusionRule("org.apache.spark"),
    "org.apache.spark" %% "spark-streaming" % sparkV ,
    "org.apache.bahir" %% "spark-streaming-twitter" % sparkV ,
    "org.apache.spark" %% "spark-sql" % sparkV ,
    "com.typesafe" % "config" % scalaConfigV ,
    "com.typesafe.scala-logging" %% "scala-logging" % scalaLoggingV ,
    "ch.qos.logback" % "logback-classic" % logbackV ,
    "org.scalatest" %% "scalatest" % scalaTestV % "test"
  )
}

assemblyMergeStrategy in assembly := {
  case m if m.toLowerCase.endsWith("manifest.mf")               => MergeStrategy.discard
  case m if m.toLowerCase.matches("meta-inf.*\\.sf$")  => MergeStrategy.discard
  case "log4j.properties"                                       => MergeStrategy.discard
  case m if m.toLowerCase.startsWith("meta-inf/services/") => MergeStrategy.filterDistinctLines
  case "reference.conf"                                    => MergeStrategy.concat
  case m if m.toLowerCase.startsWith("meta-inf/spring.")   => MergeStrategy.filterDistinctLines
  case _                                                   => MergeStrategy.first
}

/*
assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs @ _*) =>
    (xs map {_.toLowerCase}) match {
      case ("manifest.mf" :: Nil) | ("index.list" :: Nil) | ("dependencies" :: Nil) => MergeStrategy.discard
      case ps @ (x :: xs) if ps.last.endsWith(".sf") || ps.last.endsWith(".dsa") => MergeStrategy.discard
      case "plexus" :: xs => MergeStrategy.discard
      case "spring.tooling" :: xs => MergeStrategy.discard
      case "services" :: xs => MergeStrategy.filterDistinctLines
      case ("spring.schemas" :: Nil) | ("spring.handlers" :: Nil) => MergeStrategy.filterDistinctLines
      case _ => MergeStrategy.discard
    }
  case x => MergeStrategy.first
}
*/