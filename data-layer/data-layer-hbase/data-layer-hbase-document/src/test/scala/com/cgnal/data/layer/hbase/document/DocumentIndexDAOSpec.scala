package com.cgnal.data.layer.hbase.document

import com.cgnal.core.logging.BaseLogging
import com.cgnal.core.utility.digest.DigesterSha256
import com.cgnal.data.model._
import org.apache.hadoop.hbase.client.{Connection, Table}
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.hbase.{HBaseTestingUtility, TableName}
import org.scalatest.{BeforeAndAfterAll, FunSuite}

final class DocumentIndexDAOSpec   extends FunSuite
  with BeforeAndAfterAll
  with BaseLogging {

  protected val hbaseUtil = new HBaseTestingUtility()
  protected val dao = new DocumentIndexDAO()

  protected var connection : Connection = _

  protected val document = Document(
    id = "id",
    properties = Map(
      DocumentProperties.Text -> "Document Text",
      DocumentProperties.Title -> "Document Title",
      DocumentProperties.PublishDay -> 20151212
    ),
    body = DocumentBody(Some(MimeType("text", "plain")), "Document Body Text".getBytes)
  )


  override def beforeAll(): Unit = {
    hbaseUtil.getConfiguration.set("hfile.format.version", "3")
    hbaseUtil.startMiniCluster(1)

    connection = hbaseUtil.getConnection
    hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    super.beforeAll()
  }

  override def afterAll(): Unit = {
    connection.close()

    hbaseUtil.shutdownMiniCluster()
  }

  test("a key creation") {

    val digest = DigesterSha256.byteArrayToDigest("Document Body Text".getBytes)

    val documentBodyIndex =  DocumentIndex(
      documentHash = digest,
      documentIds = Seq.empty
    )

    assertResult(dao.computeKey(documentBodyIndex))(Bytes.toBytes(digest))

  }

  test("a document index must be put and retrieved correctly by hash") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentIndexDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentIndexDAO.defaultTableName), Array(DocumentIndexDAO.columnFamily))

    val digest = DigesterSha256.byteArrayToDigest("Document Body Text".getBytes)

    val documentBodyIndex =  DocumentIndex(
      documentHash = digest,
      documentIds = Seq("aaaaaaaaaaaaaaaaaaaa".getBytes)
    )

    dao.writeToHBase(documentBodyIndex)

    val key: Array[Byte] = dao.computeKey(documentBodyIndex)
    val res = dao.readFromHBase(key)


    assertResult(true)(res.isDefined)

    val document: DocumentIndex = res.get

    assertResult(documentBodyIndex.documentHash)(document.documentHash)
    assertResult(documentBodyIndex.documentIds.size)(1)
    assertResult(documentBodyIndex.documentIds.head)("aaaaaaaaaaaaaaaaaaaa".getBytes)

  }

  test("a document index must be put and and could be overwrite correctly") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentIndexDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentIndexDAO.defaultTableName), Array(DocumentIndexDAO.columnFamily))

    val digest = DigesterSha256.byteArrayToDigest("Document Body Text".getBytes)


    val documentBodyIndex1 =  DocumentIndex(
      documentHash = digest,
      documentIds = Seq("aaaaaaaaaaaaaaaaaaaa".getBytes)
    )

    dao.writeToHBase(documentBodyIndex1)

    val key1: Array[Byte] = dao.computeKey(documentBodyIndex1)
    val res1 = dao.readFromHBase(key1)


    assertResult(true)(res1.isDefined)

    val result1 : DocumentIndex = res1.get

    assertResult(result1.documentHash)(documentBodyIndex1.documentHash)
    assertResult(result1.documentIds.size)(1)
    assertResult(result1.documentIds.head)("aaaaaaaaaaaaaaaaaaaa".getBytes)

    val documentBodyIndex2 =  DocumentIndex(
      documentHash = digest,
      documentIds = Seq("aaaaaaaaaaaaaaaaaaaa".getBytes, "bbbbbbbbbbbbbbbbbbbb".getBytes)
    )

    dao.writeToHBase(documentBodyIndex2)

    val key2: Array[Byte] = dao.computeKey(documentBodyIndex2)
    val res2 = dao.readFromHBase(key2)


    assertResult(true)(res2.isDefined)

    val result2 : DocumentIndex = res2.get

    assertResult(result2.documentHash)(documentBodyIndex2.documentHash)
    assertResult(result2.documentIds.size)(2)
    assertResult(result2.documentIds.count(id => id.sameElements("aaaaaaaaaaaaaaaaaaaa".getBytes)))(1)
    assertResult(result2.documentIds.count(id => id.sameElements("bbbbbbbbbbbbbbbbbbbb".getBytes)))(1)

    assertResult(key1.sameElements(key2))(true)

  }


}
