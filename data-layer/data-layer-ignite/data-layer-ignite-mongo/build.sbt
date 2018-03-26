name := "data-layer-ignite-mongo"

version := "1.0.0-SNAPSHOT"

libraryVersions ++= Map(
  'mongoscaladriver -> "1.2.1",
  'ignite -> "2.4.0"
)

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "cgnal-core-config" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
  "org.apache.ignite" % "ignite-core" % v('ignite) ,
  "org.mongodb.scala" %% "mongo-scala-driver" % v('mongoscaladriver) ,
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}

