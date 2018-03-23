name := "spark-ignite-ingestion"

lazy val `spark-ignite-ingestion` = (project in file(".")).aggregate(`twitter-client-probe`, `twitter-common-probe`, `server-probe`).disablePlugins(sbtassembly.AssemblyPlugin)

lazy val `twitter-client-probe`   = project in file("twitter-client-probe")
lazy val `twitter-common-probe`   = project in file("twitter-common-probe")
lazy val `server-probe`           = project in file("server-probe")


