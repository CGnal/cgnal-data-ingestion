package com.cgnal.data.layer.hbase.document

import java.util
import scala.collection.JavaConversions._

import com.cgnal.data.layer.hbase.core.{HBaseDAO, Raw}
import com.cgnal.data.model.DocumentIndex
import org.apache.hadoop.hbase.client.{Put, Result}
import org.apache.hadoop.hbase.util.Bytes

import scala.collection.mutable

class DocumentIndexDAO(override val howManyBuckets: Int = 1) extends HBaseDAO[DocumentIndex]{

  override val columnFamilies: Seq[Raw] = Seq { Bytes.toBytes(DocumentIndexDAO.columnFamily) }

  override def computeKey(entity: DocumentIndex) : Raw = computeKey(entity.documentHash)

  protected[document] def computeKey(documentHash : String) : Raw = {
    val buffer = createEmptyKeyArray
    Bytes.putBytes(buffer, 0, Bytes.toBytes(documentHash), 0 , DocumentIndexDAO.keyLength)
    buffer
  }

  override def getPut(entity: DocumentIndex): Put = {
    val p = new Put(computeKey(entity))
    entity.documentIds.zipWithIndex.foreach {
      case (el,idx) => p.addColumn(Bytes.toBytes(DocumentIndexDAO.columnFamily),Bytes.toBytes(idx), el)
    }
    p
  }

  /**
    * reads a result back into an entity
    */
  override def resultToEntity(result : Result) : DocumentIndex = {
    val id: Raw = result.getRow
    val familyMap: util.NavigableMap[Raw, Raw] = result.getFamilyMap(Bytes.toBytes(DocumentIndexDAO.columnFamily))

    val propertyKeys: mutable.Set[Int] = familyMap.keySet().map(Bytes.toInt)
    val ids : Seq[Array[Byte]] = propertyKeys.map( key => familyMap.get(Bytes.toBytes(key))).toSeq

    DocumentIndex(new String(id), ids)
  }

  protected def createEmptyKeyArray : Raw = new Raw(DocumentIndexDAO.keyLength)

}

object DocumentIndexDAO {

  val defaultTableName = "DocumentsIndex"
  val columnFamily     = "i"
  val keyLength        = 64

}

