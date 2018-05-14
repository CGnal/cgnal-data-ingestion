name := "data-layer"

lazy val `data-layer` = (project in file(".")).aggregate(`data-layer-core`, `data-layer-hbase` , `data-layer-ignite`)

lazy val `data-layer-core`   = project in file("data-layer-core")
lazy val `data-layer-hbase`  = project in file("data-layer-hbase")
lazy val `data-layer-sql`    = project in file("data-layer-sql")
lazy val `data-layer-ignite` = project in file("data-layer-ignite")