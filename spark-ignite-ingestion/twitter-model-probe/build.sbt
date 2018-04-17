name := "twitter-model-probe"

version := "1.0.0-SNAPSHOT"

libraryDependencies <++= libraryVersions { v => Seq(
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}
