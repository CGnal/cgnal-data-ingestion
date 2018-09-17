name := "spark-ignite-ingestion"

lazy val `spark-ignite-ingestion` = (project in file(".")).aggregate(`twitter-server-probe`, `twitter-client-probe`, `twitter-common-probe`, `twitter-model-probe`,`twitter-recovery-probe`,`twitter-search-probe` ).disablePlugins(sbtassembly.AssemblyPlugin)


lazy val `twitter-server-probe`           = project in file("twitter-server-probe")

lazy val `twitter-client-probe`   = project in file("twitter-client-probe")
lazy val `twitter-common-probe`   = project in file("twitter-common-probe")
lazy val `twitter-model-probe`    = project in file("twitter-model-probe")
lazy val `twitter-recovery-probe` = project in file("twitter-recovery-probe")
lazy val `twitter-search-probe`   = project in file("twitter-search-probe")



