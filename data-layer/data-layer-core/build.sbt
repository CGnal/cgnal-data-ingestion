name := "data-layer-core"

version := "1.0.0-SNAPSHOT"

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}