package com.cgnal.data.layer.hbase

import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.hbase.TableName
import org.apache.hadoop.hbase.client.{Admin, Connection, ConnectionFactory, Table}

package object core {

  type Raw     = Array[Byte]
  type Column  = (Raw, Raw)
  type Columns = List[(Raw, Raw)]

  /**
    * create an hbase connection, do stuff and close.
    * @param configuration the conf
    * @param businessLogic what you want to do
    * @tparam T
    * @return
    */
  def withHBaseConnection[T](configuration:Configuration)(businessLogic: Connection => T ) : T = {
    var connection: Connection = null
    try {
      connection =  ConnectionFactory.createConnection(configuration)
      businessLogic(connection)
    } finally {
      if (connection != null) {
        connection.close()
      }
    }
  }

  /**
    * create an hbase table, do stuff and then close
    * @param connection the conn
    * @param tableName the table name
    * @param businessLogic what you want to do
    * @tparam T
    * @return
    */
  def withHBaseTable[T](connection:Connection,tableName:String)(businessLogic: Table => T ) : T = {

    var table: Table = null
    try {
      table = connection.getTable(TableName.valueOf(tableName))
      businessLogic(table)
    } finally {
      if (table != null) {
        table.close()
      }
    }
  }

  /**
    * create an Admin, do stuff then close
    * @param connection the hbase connection
    * @param tableName the table
    * @param businessLogic what you want to do
    * @tparam T
    * @return
    */
  def withHBaseAdmin[T](connection:Connection,tableName:String)(businessLogic: Admin => T ) : T = {

    var admin: Admin = null
    try {
      admin = connection.getAdmin
      businessLogic(admin)
    } finally {
      if (admin != null) {
        if(admin.tableExists(TableName.valueOf(tableName))){
          admin.flush(TableName.valueOf(tableName))
        }
        admin.close()
      }
    }
  }





}
