name := "data-layer-hbase-document"

version := "1.0.0-SNAPSHOT"

libraryDependencies <++= libraryVersions { v => Seq(
  "com.cgnal" %% "cgnal-core-config" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-logging" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-process" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "cgnal-core-utility" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-model" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-layer-core" % "1.0.0-SNAPSHOT",
  "com.cgnal" %% "data-layer-hbase-core" % "1.0.0-SNAPSHOT",
  "org.apache.hadoop" % "hadoop-common" % "2.6.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hadoop" % "hadoop-client" % "2.6.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hadoop" % "hadoop-hdfs" % "2.6.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hadoop" % "hadoop-hdfs" % "2.6.0-cdh5.7.0" % "test" classifier "tests" extra "type" -> "test-jar" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hbase" % "hbase-common" % "1.2.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hbase" % "hbase-server" % "1.2.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hbase" % "hbase-testing-util" % "1.2.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hbase" % "hbase-hadoop-compat" % "1.2.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hbase" % "hbase-hadoop2-compat" % "1.2.0-cdh5.7.0" % "test" classifier "tests" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.apache.hadoop" % "hadoop-minicluster" % "2.6.0-cdh5.7.0" % "test" excludeAll ( ExclusionRule("log4j"), ExclusionRule("slf4j-log4j12")),
  "org.scalatest" %% "scalatest" %  v('scalatest) % "test"
)}