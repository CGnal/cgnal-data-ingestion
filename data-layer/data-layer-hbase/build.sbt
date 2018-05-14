name := "data-layer-hbase"

lazy val `data-layer-hbase` = (project in file(".")).aggregate(`data-layer-hbase-core` , `data-layer-hbase-document`)

lazy val `data-layer-hbase-core`      = project in file("data-layer-hbase-core")
lazy val `data-layer-hbase-document`  = project in file("data-layer-hbase-document")
