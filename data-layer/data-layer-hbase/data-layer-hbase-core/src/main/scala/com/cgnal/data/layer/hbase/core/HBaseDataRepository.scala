package com.cgnal.data.layer.hbase.core

import com.cgnal.data.layer.DataRepository
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.hbase.HBaseConfiguration
import org.apache.hadoop.hbase.client.{Connection, ConnectionFactory, RetriesExhaustedWithDetailsException}

import scala.collection.JavaConverters._

trait HBaseDataRepository[A]
  extends DataRepository[Raw,A] {

  protected val defaultTableName  : String

  protected val tableNameKey      : String
  protected val useCompressionKey : String


  var connection: Option[Connection]    = None

  protected var hBaseConfiguration: Configuration = _
  protected var dao: HBaseDAO[A]                  = _
  protected var useCompression = true
  protected var tableName: String = defaultTableName


  /**
    * activate the archiver:
    * If the archiver is already active this operation is uneffective.
    */
  override def start(): Unit = {

    logger.info("HBase Data Repository is initializing...")

    connection.fold {

      val configuration = HBaseConfiguration.create()
      hBaseConfiguration = configuration
      logger.info("HBase Data Repository is creating connection...")
      val theConnection = ConnectionFactory.createConnection(hBaseConfiguration)
      connection = Some(theConnection)
      logger.info("HBase Data Repository has created connection!")

      createTable()

    } { _ =>
      logger.info("the Data Repository is already active")
    }
  }

  /**
    * deactivate the data repository:
    * If the data repository is already deactivated
    */
  override def stop(): Unit = {

    logger.info(s"going to stop the Data Repository ...")

    connection.fold {
      logger.debug("Data Repository already deactivated")
    } { conn =>
      if (!conn.isClosed) {
        logger.debug(s"closing connection $conn")
        conn.close()
      }
      connection = None
    }

    logger.info(s"Stopped the Data Repository of type $getClass and instance $this")
  }

  /**
    * retrieves the entry using the HBASE key.
    *
    * @param key the key
    * @return
    */
  override def load(key: Raw): Option[A] =
    connection.flatMap { conn =>
      withHBaseTable(conn, tableName) { table =>
        logger.debug(s"retrieving element from HBase with key $key")
        val maybeA = dao.readFromHBase(key)(table)
        logger.debug(s"retrieved element from HBase with key $key")
        maybeA
      }
    }

  override def write(entity: A): Option[A] = {

    try {
      connection.foreach { conn =>
        withHBaseTable(conn, tableName) { table =>
          logger.debug(s"persisting entity  $entity with table $table")
          dao.writeToHBase(entity)(table)
          logger.debug(s"persisted entity  $entity with table $table")

        }
      }
      Some(entity)
    } catch {
      /**
        *
        * this is a specific HBase exception that communicates a reapeted
        * error on the client side.
        *
        */
      case e: RetriesExhaustedWithDetailsException =>
        logger.error("unexpected error", e)
        logger.error(s"mayHaveClusterIssues: ${e.mayHaveClusterIssues()}")
        logger.error(s"getNumExceptions: ${e.getNumExceptions}")
        logger.error(s"causes: ${e.getCauses.asScala}")
        logger.error(s"exhaustiveDescription: ${e.getExhaustiveDescription}")
        resetArchiverState()
        None
      case e: Throwable =>
        logger.error("unexpected error", e)
        resetArchiverState()
        None
    }
  }

  override def delete(key: Raw): Boolean = {
    try {
      connection.foreach { conn =>
      withHBaseTable(conn, tableName) { table =>
        logger.debug(s"delete element from HBase with key $key")
        dao.deleteFromHBase(key)(table)
        logger.debug(s"deleted element from HBase with key $key")
        }
      }
      true
    } catch {
      case e: Throwable =>
        logger.error("unexpected error", e)
        false
    }
  }

  private def createConnection(): Unit = {
    logger.info("HBase Data Repository is creating connection...")
    connection = Some(ConnectionFactory.createConnection(hBaseConfiguration))
    logger.info("Connection created")
  }

  protected def createTable(): Unit = {
    logger.debug(s"HBase Data Repository is creating the table $tableName")
    connection.foreach(connection => dao.createTable(connection, tableName, useCompression))
    logger.debug(s"HBase Data Repository has created the table $tableName")
  }

  protected def resetArchiverState(): Unit = {
    logger.info("resetting the Data Repository state")
    stop()
    start()
  }

}
