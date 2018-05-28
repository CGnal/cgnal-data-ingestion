name := "twitter-search-probe"

version := "1.0.0-SNAPSHOT"

resolvers ++= Seq(
  "GridGain Repository" at "http://www.gridgainsystems.com/nexus/content/repositories/external/"
)

libraryVersions ++= Map(
  'jackson -> "2.9.0",
  'ignite -> "2.4.0",
  'twitter4j -> "4.0.4",
  'mongoscaladriver -> "1.2.1"
)

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "twitter-common-probe" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-config" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-utility" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-rest-vertx" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-layer-ignite-mongo" % "1.0.0-SNAPSHOT",
  "org.mongodb.scala" %% "mongo-scala-driver" % v('mongoscaladriver) ,
  "com.fasterxml.jackson.module" %% "jackson-module-scala" % v('jackson),
  "org.apache.ignite" % "ignite-core" % v('ignite) excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12") ),
  "org.apache.ignite" % "ignite-spring" % v('ignite) excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12") ),
  "org.apache.ignite" % "ignite-indexing" % v('ignite) excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12") ),
  "org.twitter4j" % "twitter4j-core" % v('twitter4j) ,
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