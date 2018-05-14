package com.cgnal.data.layer.hbase.core

import org.apache.hadoop.hbase.client._
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.hbase.{HColumnDescriptor, HTableDescriptor, TableName}

import scala.collection.JavaConverters._

trait HBaseDAO[A] {

  val howManyBuckets: Int = 1

  val columnFamilies: Seq[Raw]

  /**
    * creates a Put object out of an entity
    */
  def getPut(entity: A): Put

  def computeKey(entity: A): Raw

  /**
    * Create the HBase table with the given format
    */
  def createTable(connection: Connection, tableName: String, useCompression : Boolean = false , maxVersions: Int = 1): Unit = {
    withHBaseAdmin(connection,tableName){hBaseAdmin =>
      if (!hBaseAdmin.tableExists(TableName.valueOf(tableName))) {
        val desc = new HTableDescriptor(TableName.valueOf(tableName))

        columnFamilies.map { new HColumnDescriptor(_) }.foreach { columnDescriptor =>
          columnDescriptor.setMaxVersions(maxVersions)
          desc.addFamily(columnDescriptor)
        }

        hBaseAdmin.createTable(desc)
      }
    }
  }

  /**
    * writes to hbase
    */
  def   writeToHBase(entity: A)(implicit documentsTable: Table): Unit = {
    val put: Put = getPut(entity)
    documentsTable.put(put)
  }

  /**
    * writes to HBase with a mutator
    */
  def writeToHBase(entity: A, mutator: BufferedMutator): Unit = {
    mutator.mutate(getPut(entity))
  }

  def readFromHBase(id: String)(implicit documentsTable: Table): Option[A]
  = readFromHBase(Bytes.toBytes(id))(documentsTable)

  /**
    * read from hbase
    */
  def readFromHBase(id: Raw)(implicit documentsTable: Table): Option[A] = {
    val get = new Get(id)
    val row: Result = documentsTable.get(get)
    if (row.isEmpty) None
    else Some(resultToEntity(row))
  }

  /**
    * read a list of rows from hbase
    */
  def readFromHBase(ids: List[Raw])(implicit documentsTable: Table): List[A] = {
    val gets = ids.map(new Get(_))
    documentsTable.get(gets.asJava).toList.collect {
      case result if !result.isEmpty => resultToEntity(result)
    }
  }

  /**
    * reads a result back into an entity
    */
  def resultToEntity(result:Result) : A


  def deleteFromHBase(id : Raw)(implicit documentsTable: Table) : Unit = {
    val deleteOperation = new Delete(id)
    documentsTable.delete(deleteOperation)
  }

  /**
    * specifies which columns are going to be removed out of a record
    */
  protected[core] def getPropertiesDelete(row: Result): Delete = {
    val deleteOperation = new Delete(row.getRow)
    getColumns(row).foreach { case (family, qualifier) =>
      deleteOperation.addColumns(family, qualifier)
    }
    deleteOperation
  }

  /**
    * Specifies list of pairs: (columnfamily,column)
    */
  protected[core] def getColumns(row: Result): Columns = columnFamilies.flatMap { family =>
    row.getFamilyMap(family).keySet.asScala.map { column => family -> column }
  }.toList


}
