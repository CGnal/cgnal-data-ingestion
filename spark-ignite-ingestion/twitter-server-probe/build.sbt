
name := "twitter-server-probe"

version := "1.0.0-SNAPSHOT"

resolvers ++= Seq(
  "GridGain Repository" at "http://www.gridgainsystems.com/nexus/content/repositories/external/"
)

libraryVersions ++= Map(
  'vertx -> "3.5.0",
  'ignite -> "2.4.0",
  'mongoscaladriver -> "1.2.1"
)

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "cgnal-core-config" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-rest-vertx" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-layer-ignite-mongo" % "1.0.0-SNAPSHOT",
  "org.mongodb.scala" %% "mongo-scala-driver" % v('mongoscaladriver) ,
  "io.vertx" % "vertx-web" % v('vertx),
  "org.apache.ignite" % "ignite-core" % v('ignite) ,
  "org.apache.ignite" % "ignite-spring" % v('ignite) ,
  "org.apache.ignite" % "ignite-indexing" % v('ignite) ,
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}


assemblyMergeStrategy in assembly := {
  case m if m.toLowerCase.endsWith("manifest.mf")             => MergeStrategy.discard
  case m if m.toLowerCase.matches("meta-inf.*\\.sf$")  => MergeStrategy.discard
  case m if m.toLowerCase.startsWith("meta-inf/services/")    => MergeStrategy.filterDistinctLines
  case m if m.toLowerCase.startsWith("meta-inf/spring.")      => MergeStrategy.filterDistinctLines
  case "log4j.properties"                                     => MergeStrategy.discard
  case "application.conf"                                     => MergeStrategy.discard
  case _                                                      => MergeStrategy.first
}

