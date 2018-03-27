name := "spark-ignite-ingestion"

version := "1.0.0-SNAPSHOT"

scalaVersion := "2.11.8"


lazy val `spark-ignite-ingestion` = (project in file(".")).aggregate(`twitter-client-probe`, `server-probe`).disablePlugins(sbtassembly.AssemblyPlugin)

lazy val `twitter-client-probe`   = project in file("twitter-client-probe")
lazy val `server-probe`           = project in file("server-probe")

fork in run := true

