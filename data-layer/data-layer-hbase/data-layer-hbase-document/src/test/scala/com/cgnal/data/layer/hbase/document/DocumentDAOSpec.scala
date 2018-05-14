package com.cgnal.data.layer.hbase.document

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.model._
import org.apache.hadoop.hbase.{HBaseTestingUtility, TableName}
import org.apache.hadoop.hbase.client._
import org.apache.hadoop.hbase.util.Bytes
import org.scalatest.{BeforeAndAfterAll, FunSuite}
import shapeless.Coproduct

import scala.collection.mutable.ArrayBuffer

final class DocumentDAOSpec
  extends FunSuite
    with BeforeAndAfterAll
    with BaseLogging {


  protected val hbaseUtil = new HBaseTestingUtility()
  protected val emptyBody: Array[Byte] = Array[Byte]()
  protected val dao = new DocumentDAO()

  protected var connection : Connection = _

  val document = Document(
    id = "id",
    properties = Map(
      DocumentProperties.Text -> "Lorem Ipsum",
      DocumentProperties.Title -> "Lorem Ipsum",
      DocumentProperties.PublishDay -> 20151212
    ),
    body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
  )

  override def beforeAll(): Unit = {
    super.beforeAll()

    hbaseUtil.getConfiguration.set("hfile.format.version", "3")
    hbaseUtil.startMiniCluster(1)

    connection = hbaseUtil.getConnection
    hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

  }

  override def afterAll(): Unit = {
    connection.close()

    hbaseUtil.shutdownMiniCluster()

    super.afterAll()
  }

  test("a key creation have to be invariant when publish day is present into the document") {

    assertResult(dao.computeKey(document))(dao.computeKey(document))

  }


  test("document id bytes encoding and decoding should work") {

    val key1: Array[Byte] = dao.computeKey(document)

    val recomputed = new String(key1, "ISO-8859-1").getBytes("ISO-8859-1")

    assertResult(key1.length)(recomputed.length)
    assertResult(key1)(recomputed)

  }


  test("document id encoding and decoding should work") {

    val marshall: Document = dao.preMarshall(document)
    val toBytes: Array[Byte] = marshall.id.getBytes("ISO-8859-1")
    val key: Array[Byte] = dao.computeKey(document)

    assertResult(toBytes)(key)

  }

  test("a document postmarshall must cancel the premarshall") {

    assertResult(document)(dao.postMarshall(dao.preMarshall(document)))

  }

  test("a document must be put and retrieved correctly by id") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDay -> 20151212
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    dao.writeToHBase(doc)

    val key: Array[Byte] = dao.computeKey(doc)
    val res = dao.readFromHBase(key)


    assertResult(true)(res.isDefined)

    val document: Document = res.get

    assertResult(doc.id)(document.id)
    assertResult(doc.properties)(document.properties)
    assertResult(doc.body.mimeType.get)(document.body.mimeType.get)

  }

  test("a document must be put and retrieved correctly also when id is in alien language") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = '\u3333' + "id" + '\u3334',
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDay -> 20151212
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    dao.writeToHBase(doc)

    val key: Array[Byte] = dao.computeKey(doc)
    val res = dao.readFromHBase(key)


    assertResult(true)(res.isDefined)

    val document: Document = res.get

    assertResult(doc.id)(document.id)
    assertResult(doc.properties)(document.properties)
    assertResult(doc.body.mimeType.get)(document.body.mimeType.get)

  }

  test("a document must be put and retrieved correctly with a scan") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010"
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    dao.writeToHBase(doc)

    val table1: Table = connection.getTable(TableName.valueOf(DocumentDAO.defaultTableName))
    val testScanner: ResultScanner = table1.getScanner(new Scan())

    val results = ArrayBuffer[Result]()
    var nextResult = testScanner.next()
    while (nextResult != null) {
      results += nextResult
      nextResult = testScanner.next()
    }
    testScanner.close()

    assertResult(1)(results.size)

    val results1: Result = results(0)
    val document: Document = dao.resultToEntity(results1)

    assertResult(doc.id)(document.id)
    assertResult(doc.properties)(document.properties)
    assertResult(doc.body.mimeType.get)(document.body.mimeType.get)

  }

  test("an hbase Append should create new fields") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010"
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    dao.writeToHBase(doc)

    val key: Array[Byte] = dao.computeKey(doc)
    val append: Append = new Append(key)
    append.add(Bytes.toBytes("Documents"), Bytes.toBytes(DocumentDAO.encodeColumnName[String]("FreakingString")), Bytes.toBytes("Freak"))

    table.append(append)

    val res = dao.readFromHBase(key)

    assertResult(true)(res.isDefined)

    val retrievedDocument: Document = res.get

    assertResult(doc.id)(retrievedDocument.id)

    val expected = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010",
        "FreakingString" -> "Freak"
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    assertResult(expected.properties)(retrievedDocument.properties)
  }

  test("an hbase Put should overwrite fields") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010",
        "FreakingString" -> "Freak"
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    dao.writeToHBase(doc)

    val key: Array[Byte] = dao.computeKey(doc)
    val put: Put = new Put(key)
    put.addColumn(Bytes.toBytes("Documents"), Bytes.toBytes(DocumentDAO.encodeColumnName[String]("FreakingString")), Bytes.toBytes("Freak2"))

    table.put(put)

    val res = dao.readFromHBase(key)

    assertResult(true)(res.isDefined)

    val retrievedDocument: Document = res.get

    assertResult(doc.id)(retrievedDocument.id)

    val expected = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010",
        "FreakingString" -> "Freak2"
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    assertResult(expected.properties)(retrievedDocument.properties)


  }

  test("an scan over some fields should pickup a partially filled Document, and mimetype should be OK") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010",
        "FreakingString" -> "Freak"
      ),
      body = DocumentBody(Some( MimeType("text", "plain")), Bytes.toBytes("lorem ipsum dolor sit amet"))
    )

    dao.writeToHBase(doc)

    val scan: Scan = new Scan()
    scan.addColumn(Bytes.toBytes("Documents"), Bytes.toBytes(DocumentDAO.encodeColumnName[String]("FreakingString")))
    scan.addColumn(Bytes.toBytes("Documents"), Bytes.toBytes(DocumentDAO.encodeColumnName[String]("OriginalId")))
    val scanner: ResultScanner = table.getScanner(scan)

    val results = ArrayBuffer[Result]()
    var nextResult = scanner.next()
    while (nextResult != null) {
      results += nextResult
      nextResult = scanner.next()
    }
    scanner.close()

    assertResult(1)(results.size)

    val results1: Result = results(0)
    val document: Document = dao.resultToEntity(results1)

    val expectedDocument = Document(
      id = "id",
      properties = Map(
        "FreakingString" -> "Freak"
      ),
      body = DocumentBody(None, emptyBody)
    )

    assertResult(expectedDocument.properties)(document.properties)
    assertResult(expectedDocument.id)(document.id)


  }

  test("a Document with unusual properties must be saved") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(id = "me", Map[String, DocumentProperty](), DocumentBody(None, emptyBody))

    val enrichedDoc: Document = doc.withProperty("one", 1).withProperty("two", 2).withProperty("three", 3)

    dao.writeToHBase(enrichedDoc)

    val scan: Scan = new Scan()
    val scanner: ResultScanner = table.getScanner(scan)

    val results = ArrayBuffer[Result]()
    var nextResult = scanner.next()
    while (nextResult != null) {
      results += nextResult
      nextResult = scanner.next()
    }
    scanner.close()

    assertResult(1)(results.size)

    val results1: Result = results(0)
    val document: Document = dao.resultToEntity(results1)

    val expectedDocument = Document(
      id = "me",
      properties = Map(
        "one" -> 1,
        "two" -> 2,
        "three" -> 3
      ),
      body = DocumentBody(None, emptyBody)
    )

    assertResult(expectedDocument.properties)(document.properties)
    assertResult(expectedDocument.id)(document.id)

  }

  test("a Document populated in a funny way must be saved") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(id = "me", Map[String, DocumentProperty](), DocumentBody(None, emptyBody))

    val propNames = List("one", "two", "three")

    val map1: List[DocumentProperty] = List("1", "2").map(x => Coproduct[DocumentProperty](x))
    val map2: List[DocumentProperty] = List(3).map(x => Coproduct[DocumentProperty](x))

    val tuples: List[(String, DocumentProperty)] = propNames zip (map1 ++ map2)

    val enrichedDoc: Document = tuples.foldLeft(doc)((accu, pair) => accu.withProperty(pair._1, pair._2))

    dao.writeToHBase(enrichedDoc)

    val scan: Scan = new Scan()
    val scanner: ResultScanner = table.getScanner(scan)

    val results = ArrayBuffer[Result]()
    var nextResult = scanner.next()
    while (nextResult != null) {
      results += nextResult
      nextResult = scanner.next()
    }
    scanner.close()

    assertResult(1)(results.size)

    val results1: Result = results(0)
    val document: Document = dao.resultToEntity(results1)

    val expectedDocument = Document(
      id = "me",
      properties = Map(
        "one" -> "1",
        "two" -> "2",
        "three" -> 3
      ),
      body = DocumentBody(None, emptyBody)
    )

    assertResult(expectedDocument.properties)(document.properties)
    assertResult(expectedDocument.id)(document.id)

  }

  test("a Document should be removed") {

    hbaseUtil.deleteTableIfAny(TableName.valueOf(DocumentDAO.defaultTableName))
    implicit val table: Table = hbaseUtil.createTable(TableName.valueOf(DocumentDAO.defaultTableName), Array(DocumentDAO.columnFamily))

    val doc = Document(
      id = "id",
      properties = Map(
        DocumentProperties.Text -> "Lorem Ipsum",
        DocumentProperties.Title -> "Lorem Ipsum",
        DocumentProperties.PublishDate -> "20151010101010"
      ),
      body = DocumentBody(Some(MimeType("text", "plain")), emptyBody)
    )

    dao.writeToHBase(doc)

    val table1: Table = connection.getTable(TableName.valueOf(DocumentDAO.defaultTableName))
    val testScanner1: ResultScanner = table1.getScanner(new Scan())

    val results1 = ArrayBuffer[Result]()
    var nextResult1 = testScanner1.next()
    while (nextResult1 != null) {
      results1 += nextResult1
      nextResult1 = testScanner1.next()
    }
    testScanner1.close()

    assertResult(1)(results1.size)

    dao.deleteFromHBase(dao.computeKey(doc))(table1)

    val testScanner2: ResultScanner = table1.getScanner(new Scan())

    val results2 = ArrayBuffer[Result]()
    var nextResult2 = testScanner2.next()
    while (nextResult2 != null) {
      results2 += nextResult2
      nextResult2 = testScanner2.next()
    }
    testScanner2.close()

    assertResult(0)(results2.size)


  }


}
