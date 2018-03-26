
name := "data-layer-ignite"

lazy val `data-layer-ignite` = (project in file(".")).aggregate(`data-layer-ignite-mongo`)

lazy val `data-layer-ignite-mongo` = project in file("data-layer-ignite-mongo")

