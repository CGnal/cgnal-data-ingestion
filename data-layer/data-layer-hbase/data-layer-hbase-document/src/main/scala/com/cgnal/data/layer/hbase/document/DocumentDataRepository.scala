package com.cgnal.data.layer.hbase.document

import com.cgnal.data.layer.hbase.core.{HBaseDataRepository, Raw}
import com.cgnal.data.model.Document

class DocumentDataRepository
  extends HBaseDataRepository[Document] {

  override protected val tableNameKey: String       = "com.cgnal.data.layer.hbase.documents.documentsTable"
  protected val tableIndexNameKey : String          = "com.cgnal.data.layer.hbase.documents.documentsIndexTable"
  override protected val useCompressionKey: String  = "com.cgnal.data.layer.hbase.useCompression"
  protected val howManyBucketsKey : String          = "com.cgnal.data.layer.hbase.buckets"

  protected var howManyBuckets = 1
  override protected val defaultTableName: String = "Documents"
  protected var tableIndexName: String = s"${defaultTableName}Index"


  protected val idxDao = new DocumentIndexDAO(howManyBuckets = howManyBuckets)


  override protected def createTable(): Unit = {
    logger.debug(s"Document Data Repository is creating the table $tableName with its index table $tableIndexName")

    connection.foreach(connection => dao.createTable(connection, tableName, useCompression))
    connection.foreach(connection => idxDao.createTable(connection, tableIndexName, useCompression))

    logger.debug(s"Document Data Repository has created the table $tableName with its index table $tableIndexName")

  }

  override def configure(properties: Map[String, Any]): Unit = {
    logger.info(s"Configuring the Document Data Repository with properties : $properties")

    howManyBuckets = properties.get(howManyBucketsKey) match {
      case Some(x) if x.isInstanceOf[Int] => x.asInstanceOf[Int]
      case Some(x) if x.isInstanceOf[String] => x.asInstanceOf[String].toInt
      case _ => 1
    }

    tableName = properties.get(tableNameKey) match {
      case Some(x) => x.asInstanceOf[String]
      case None => defaultTableName
    }

    tableIndexName = properties.get(tableIndexNameKey) match {
      case Some(x) => x.asInstanceOf[String]
      case None => s"${tableName}Index"
    }

    useCompression = properties.get(useCompressionKey) match {
      case Some(x) if x.isInstanceOf[Boolean] => x.asInstanceOf[Boolean]
      case Some(x) if x.isInstanceOf[String] => x.asInstanceOf[String].toBoolean
      case None => true
    }

    dao = new DocumentDAO(howManyBuckets = howManyBuckets)


  }

  override def delete(key: Raw): Boolean = ???


}
