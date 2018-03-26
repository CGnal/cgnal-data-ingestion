package com.cgnal.data.access.ignite.mongo

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.access.ignite.mongo.config.MongoStorageConfig
import com.cgnal.data.model.{Document => CgnalDocument, _}
import javax.cache.Cache
import org.apache.ignite.cache.store.CacheStoreAdapter
import org.apache.ignite.lifecycle.LifecycleAware
import org.mongodb.scala.bson.collection.immutable.Document
import org.mongodb.scala.model.Filters.equal
import org.mongodb.scala.{MongoClient, MongoCollection, MongoDatabase}

import scala.concurrent.duration._
import scala.concurrent.{Await, Awaitable}
import scala.language.postfixOps

class DocumentMongoStorageAdapter
  extends CacheStoreAdapter[String, CgnalDocument]
    with LifecycleAware
    with BaseLogging {

  val defaultCollectionName: String = "documents"

  protected var mongoClient: MongoClient = _
  protected var mongoDatabase: MongoDatabase = _
  protected var mongoCollection: MongoCollection[Document] = _

  override def start(): Unit = {
    logger.info(s"Starting Mongo Document Adapter")

    val connectionString: String = s"mongodb://${MongoStorageConfig.mongoUser}:${MongoStorageConfig.mongoPassword}@${MongoStorageConfig.mongoHost}:${MongoStorageConfig.mongoPort}/?authSource=${MongoStorageConfig.documentsDbName}"

    mongoClient = MongoClient(connectionString)
    mongoDatabase = mongoClient.getDatabase(MongoStorageConfig.documentsDbName)
    mongoCollection = mongoDatabase.getCollection(defaultCollectionName)

    logger.info(s"Mongo Document Adapter Successful Started")

  }

  override def stop(): Unit = {
    logger.info(s"Closing Mongo Document Adapter")
    mongoClient.close()

  }

  override def delete(key: Any): Unit = {
    mongoCollection.deleteOne(equal("tweetId", key))
  }

  override def write(entry: Cache.Entry[_ <: String, _ <: CgnalDocument]): Unit = {
    logger.debug(s"Inserting record key: ${entry.getKey} value: ${entry.getValue}")
    val inserted = execute(mongoCollection.insertOne(toDocument(entry.getValue)).toFuture())
    logger.debug(s"Inserting result [ $inserted ]")

  }


  override def load(key: String): CgnalDocument = {
    logger.debug(s"Loading record with key : $key")

    val loaded = execute(mongoCollection.find(equal("documentId", key)).first()
      .map(toCgnalDocument)
      .toFuture())

    loaded.head
  }

  private def toDocument: CgnalDocument => Document = document =>
    Document(
      DocumentMongoStoreAdapter.DocumentId -> document.id,
      DocumentMongoStoreAdapter.PublishDay -> document.property[Long](DocumentProperties.PublishDay),
      DocumentMongoStoreAdapter.PublishDate -> document.property[String](DocumentProperties.PublishDate),
      DocumentMongoStoreAdapter.Language -> document.property[String](DocumentProperties.Language),
      DocumentMongoStoreAdapter.UserId -> document.property[Long]("UserId"),
      DocumentMongoStoreAdapter.SourceType -> document.property[String](DocumentProperties.SourceType),
      DocumentMongoStoreAdapter.SourceName -> document.property[String](DocumentProperties.SourceName),
      DocumentMongoStoreAdapter.Text -> document.property[String](DocumentProperties.Text),
      DocumentMongoStoreAdapter.Symbols -> document.property[List[String]]("Symbols"),
      DocumentMongoStoreAdapter.HashTags -> document.property[List[String]]("HashTags"),
      DocumentMongoStoreAdapter.Status -> document.property[String]("Status")
    )

  private def toCgnalDocument: Document => CgnalDocument = document => {
    val text: String = document.getString(DocumentMongoStoreAdapter.Text)

    CgnalDocument(document.getString(DocumentMongoStoreAdapter.DocumentId), Map.empty, DocumentBody(Some(MimeTypes.applicationJson), text.getBytes("UTF-8")))
      .withProperty(DocumentProperties.PublishDay, document.getString(DocumentMongoStoreAdapter.PublishDay).toLong)
      .withProperty(DocumentProperties.PublishDate, document.getString(DocumentMongoStoreAdapter.PublishDate))
      .withProperty(DocumentProperties.Language, document.getString(DocumentMongoStoreAdapter.Language))
      .withProperty(DocumentProperties.SourceType, document.getString(DocumentMongoStoreAdapter.SourceType))
      .withProperty(DocumentProperties.SourceName, document.getString(DocumentMongoStoreAdapter.SourceName))
      .withProperty(DocumentProperties.Text, text)
      .withProperty("UserId", document.getString(DocumentMongoStoreAdapter.UserId).toLong)
      .withProperty("Symbols", document.getOrDefault(DocumentMongoStoreAdapter.Symbols, List.empty[String]).asInstanceOf[List[String]])
      .withProperty("HashTags", document.getOrDefault(DocumentMongoStoreAdapter.HashTags, List.empty[String]).asInstanceOf[List[String]])
      .withProperty("Status", document.getOrDefault(DocumentMongoStoreAdapter.Status, "{}").asInstanceOf[String])

  }

  private def execute[A](await: Awaitable[A]): A = Await.result[A](await, 500 milliseconds)


}

object DocumentMongoStoreAdapter {

  val DocumentId = "documentId"
  val PublishDay = "publishDay"
  val PublishDate = "publishDate"
  val UserId = "userId"
  val Language = "language"
  val SourceType = "sourceType"
  val SourceName = "sourceName"
  val Text = "text"
  val Symbols = "symbols"
  val HashTags = "hashTags"
  val Status = "status"

}
