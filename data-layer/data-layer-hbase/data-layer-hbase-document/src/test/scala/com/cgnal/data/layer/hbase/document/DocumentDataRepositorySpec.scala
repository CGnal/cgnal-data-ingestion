package com.cgnal.data.layer.hbase.document

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model._
import org.apache.hadoop.hbase.{HBaseTestingUtility, TableName}
import org.apache.hadoop.hbase.client.Connection
import org.scalatest.{BeforeAndAfterAll, FunSuite}

final class DocumentDataRepositorySpec
  extends FunSuite
    with BeforeAndAfterAll
    with BaseLogging {


  protected val hbaseUtil = new HBaseTestingUtility()
  protected var connection : Connection = _
  protected val repository = new DocumentDataRepository()

  override def beforeAll(): Unit = {
    super.beforeAll()

    hbaseUtil.getConfiguration.set("hfile.format.version", "3")
    hbaseUtil.startMiniCluster(1)

    connection = hbaseUtil.getConnection

    hbaseUtil.createTable(TableName.valueOf("Documents"), Array("Documents"))
    hbaseUtil.createTable(TableName.valueOf("DocumentsIndex"), Array("i"))

    val properties = Map("com.cgnal.data.layer.hbase.buckets" -> "1")

    repository.configure(properties)
    repository.connection = Some(connection)
    repository.start()

  }

  override def afterAll(): Unit = {

    repository.stop()

    connection.close()
    hbaseUtil.shutdownMiniCluster()

    super.afterAll()
  }


  val document1 = Document(
    id = "id-1",
    properties = Map(
      DocumentProperties.Text -> "Document Text",
      DocumentProperties.Title -> "Document Title",
      DocumentProperties.PublishDay -> 20151212
    ),
    body = DocumentBody(Some(MimeType("text", "plain")), "Document Body Text".getBytes)
  )

  val document2 = Document(
    id = "id-2",
    properties = Map(
      DocumentProperties.Text -> "Document Text",
      DocumentProperties.Title -> "Document Title",
      DocumentProperties.PublishDay -> 20151221
    ),
    body = DocumentBody(Some(MimeType("text", "plain")), "Document Body Text".getBytes)
  )




  test("retrieve a document by its id") {
    val dao  = new DocumentDAO()


    repository.write(document1)
    repository.write(document2)

    val result1 = repository.load(dao.computeKey(document1))

    assert(result1.isDefined)
    assertResult(result1.get.id)("id-1")

    val result2 = repository.load(dao.computeKey(document2))

    assert(result2.isDefined)
    assertResult(result2.get.id)("id-2")

  }

}
