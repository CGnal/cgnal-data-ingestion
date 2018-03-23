name := "twitter-common-probe"

version := "1.0.0-SNAPSHOT"

libraryVersions ++= Map(
  'vertx -> "3.5.0",
  'jackson -> "2.9.0",
  'twitter4j -> "4.0.4",
  'ignite -> "2.4.0"

)

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "cgnal-core-config" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-utility" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-rest-vertx" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-layer-ignite-mongo" % "1.0.0-SNAPSHOT",
  "com.fasterxml.jackson.module" %% "jackson-module-scala" % v('jackson),
  "org.twitter4j" % "twitter4j-core" % v('twitter4j) ,
  "org.twitter4j" % "twitter4j-stream" % v('twitter4j) ,
  "io.vertx" % "vertx-web" % v('vertx) excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12") ),
  "org.apache.ignite" % "ignite-core" % v('ignite) excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12") ),
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}
