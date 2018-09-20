name := "data-model"

version := "1.0.1"

organization := "com.cgnal"

scalaVersion := "2.11.8"

libraryDependencies ++= {
  val shapelessV      = "2.3.2"
  val scalaTestV      = "3.0.1"
  Seq(
    "com.chuusai" %% "shapeless" % shapelessV,
    "org.scalatest" %% "scalatest" % scalaTestV % "test"
  )
}
