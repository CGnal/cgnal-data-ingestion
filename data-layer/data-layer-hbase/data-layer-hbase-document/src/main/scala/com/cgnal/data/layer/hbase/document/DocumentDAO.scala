package com.cgnal.data.layer.hbase.document

import java.time.{LocalDate, LocalDateTime}
import java.util

import com.cgnal.core.utility.datetime.DateTimeUtility
import com.cgnal.data.layer.hbase.core.{HBaseDAO, Raw}
import com.cgnal.data.model._
import org.apache.hadoop.hbase.client.{Put, Result}
import org.apache.hadoop.hbase.util.Bytes

import scala.collection.JavaConversions._
import scala.collection.mutable
import scala.reflect.runtime.universe._

class DocumentDAO(override val howManyBuckets: Int = 1, val typeSeparator :Char = DocumentDAO.typeSeparator)
  extends HBaseDAO[Document]{

  import Bytes._
  import com.cgnal.core.utility.digest.DigesterSha512._

  override val columnFamilies: Seq[Raw] = Seq { Bytes.toBytes(DocumentDAO.columnFamily) }

  /**
    * WARNING: This method can return a wrong key if used with incomplete documents
    *
    * @param document to be used to compute the key
    * @return
    */
  def computeKey(document: Document): Raw = {

    val publishDay: Int =
      safeGetOrElse(
        document.properties, DocumentProperties.PublishDay,
        DateTimeUtility.timestampToPublishDay(0)
      )

    computeKey(document.id, publishDay)
  }

  /**
    *
    * @param docId      Document ID
    * @param publishDay Document publish date
    * @return document key
    */
  def computeKey(docId: String, publishDay: Int): Raw = {

    val buffer = createEmptyKeyArray

    //#1 salt
    val salt: Byte = calculateBucket(docId)


    //#2 publish day
    // publishDay

    //#4 normalized id
    val normalizedId: String = stringToDigest(docId)

    Bytes.putByte(buffer, 0, salt)
    Bytes.putInt(buffer, 1, publishDay)
    Bytes.putBytes(buffer, 5, Bytes.toBytes(normalizedId), 0, digestByteArrayLenght)

    buffer
  }


  override def getPut(doc : Document): Put = {

    val document = preMarshall(doc)

    val p = new Put(documentIdToByteArray(document))

    if (document.body.mimeType.isDefined) {
      val mt = document.body.mimeType.get
      val primaryType: String = mt.primary
      val secodaryType: String = mt.secondary
      val value = primaryType + "___" + secodaryType
      p.addColumn(toBytes(DocumentDAO.columnFamily), toBytes(DocumentDAO.mimeTypeKey), toBytes(value))
    }

    if (document.body.blob.length > 0) {
      p.addColumn(toBytes(DocumentDAO.columnFamily), toBytes(DocumentDAO.documentBlob), document.body.blob)
    }

    document.properties.foreach { pair =>
      val serialized = pair._2.reduce(reducer)
      p.addColumn(toBytes(DocumentDAO.columnFamily), serialized._1(pair._1), serialized._2)
    }
    p
  }

  override def resultToEntity(row : Result): Document = {
    val id: Raw = row.getRow
    val familyMap: util.NavigableMap[Raw, Raw] = row.getFamilyMap(toBytes(DocumentDAO.columnFamily))

    val mimeType: Option[MimeType] = Option(familyMap.get(toBytes(DocumentDAO.mimeTypeKey))) match {
      case Some(s) =>
        val string: String = Bytes.toString(s)
        val split: Array[String] = string.split("___")
        Some(MimeType(split(0), split(1)))
      case None => None
    }

    val blob: Raw = Option(familyMap.get(toBytes(DocumentDAO.documentBlob))).getOrElse(Array[Byte]())
    val propertyKeys: mutable.Set[String] = familyMap.keySet().map(Bytes.toString).filter(rp => rp.charAt(rp.length - 2) == DocumentDAO.typeSeparator)

    val maybeTuples: List[Option[(String, DocumentProperty)]] = propertyKeys.map { rawkey =>
      val length = rawkey.length
      val key = rawkey.substring(0, length - 2)
      val typeIdentifier = rawkey.charAt(length - 1)
      types.get(typeIdentifier).map(t => key -> t(familyMap.get(toBytes(rawkey))))
    }.toList

    val collected: List[(String, DocumentProperty)] = maybeTuples.collect({ case Some(x) => x })
    val propertiesInMap: Map[String, DocumentProperty] = collected.toMap

    val retrievedDoc = Document(byteArrayToDocumentId(id), propertiesInMap, DocumentBody(mimeType, blob))

    postMarshall(retrievedDoc)
  }



  protected def createEmptyKeyArray : Raw = new Raw(1 + 4 + digestByteArrayLenght)

  protected def calculateBucket(docId:String) :Byte =
    (Math.abs(docId.hashCode) % howManyBuckets).toByte

  protected def documentIdToByteArray(doc: Document): Raw = doc.id.getBytes("ISO-8859-1")

  protected def byteArrayToDocumentId(byteArray: Raw) = new String(byteArray, "ISO-8859-1")

  protected[document] def preMarshall(document: Document): Document = {
    document.copy(
      id = new String(computeKey(document), "ISO-8859-1"),
      properties = document.properties + (DocumentProperties.OriginalId -> document.id),
      body = document.body
    )
  }

  protected[document] def postMarshall(document: Document): Document = document.copy(
    id         = safeGetOrElse(document.properties, DocumentProperties.OriginalId, document.id),
    properties = document.properties - (DocumentProperties.OriginalId, document.id),
    body       = document.body
  )

}

object DocumentDAO {


  /**
    * centralizing the management of the Type separator.
    */
  val typeSeparator = '#'

  val defaultTableName = "Documents"
  val columnFamily     = "Documents"
  val mimeTypeKey      = "documentMimeType"
  val documentBlob     = "documentBlob"

  def suffix[A: TypeTag]: String = typeOf[A] match {
    case t if t =:= typeOf[Int]                 => "i"
    case t if t =:= typeOf[Long]                => "l"
    case t if t =:= typeOf[Float]               => "f"
    case t if t =:= typeOf[Double]              => "d"
    case t if t =:= typeOf[Boolean]             => "b"
    case t if t =:= typeOf[String]              => "s"
    case t if t =:= typeOf[LocalDate]           => "v"
    case t if t =:= typeOf[LocalDateTime]       => "t"
    case _                                      => ""
  }

  def encodeColumnName[A: TypeTag](column: String, separator: Char = typeSeparator): String = s"$column$separator${suffix[A]}"

}
