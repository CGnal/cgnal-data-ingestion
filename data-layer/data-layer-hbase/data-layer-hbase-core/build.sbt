name := "data-layer-hbase-core"

version := "1.0.0-SNAPSHOT"

libraryVersions ++= Map()

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "cgnal-core-config" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-layer-core" % "1.0.0-SNAPSHOT",
  "org.apache.hadoop" % "hadoop-common" % "2.6.0-cdh5.7.0" % "compile" ,
  "org.apache.hbase" % "hbase-common" % "1.2.0-cdh5.7.0" % "compile" ,
  "org.apache.hbase" % "hbase-client" % "1.2.0-cdh5.7.0" % "compile" ,
  "org.apache.hadoop" % "hadoop-common" % "2.6.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hadoop" % "hadoop-client" % "2.6.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hbase" % "hbase-common" % "1.2.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hbase" % "hbase-server" % "1.2.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hbase" % "hbase-testing-util" % "1.2.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hbase" % "hbase-hadoop-compat" % "1.2.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hbase" % "hbase-hadoop2-compat" % "1.2.0-cdh5.7.0" % "test" classifier "tests",
  "org.apache.hadoop" % "hadoop-minicluster" % "2.6.0-cdh5.7.0" % "test",
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}