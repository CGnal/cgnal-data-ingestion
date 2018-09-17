package com.cgnal.data.access.ignite.mongo

import java.util.{Date, UUID}

import com.cgnal.core.logging.BaseLogging
import com.cgnal.data.access.ignite.mongo.config.MongoStorageConfig
import com.cgnal.twitter.probe.model.TwitterProbeIteration
import com.mongodb.client.model.UpdateOptions
import javax.cache.Cache
import org.apache.ignite.cache.store.CacheStoreAdapter
import org.apache.ignite.lifecycle.LifecycleAware
import org.mongodb.scala.bson.collection.immutable.Document
import org.mongodb.scala.model.Filters.equal
import org.mongodb.scala.{MongoClient, MongoCollection, MongoDatabase}

import scala.concurrent.duration._
import scala.concurrent.{Await, Awaitable}
import scala.language.postfixOps

class TwitterProbeIterationMongoStorageAdapter extends CacheStoreAdapter[UUID, TwitterProbeIteration]
  with LifecycleAware
  with BaseLogging {

  val defaultCollectionName: String = "iterations"

  protected var mongoClient: MongoClient = _
  protected var mongoDatabase: MongoDatabase = _
  protected var mongoCollection: MongoCollection[Document] = _

  override def start(): Unit = {

    val connectionString: String = s"mongodb://${MongoStorageConfig.mongoUser}:${MongoStorageConfig.mongoPassword}@${MongoStorageConfig.mongoHost}:${MongoStorageConfig.mongoPort}/?authSource=${MongoStorageConfig.documentsDbName}"

    logger.info(s"Starting Mongo Probe Iteration Adapter with $connectionString")


    mongoClient = MongoClient(connectionString)
    mongoDatabase = mongoClient.getDatabase(MongoStorageConfig.documentsDbName)
    mongoCollection = mongoDatabase.getCollection(defaultCollectionName)

    logger.info(s"Mongo Probe Iteration Adapter Successful Started")

  }

  override def stop(): Unit = {
    logger.info(s"Closing Mongo Probe Iteration Adapter")
    mongoClient.close()

  }

  override def delete(key: Any): Unit = {
    mongoCollection.deleteOne(equal("tweetId", key))
  }

  override def write(entry: Cache.Entry[_ <: UUID, _ <: TwitterProbeIteration]): Unit = {
    logger.debug(s"Inserting record key: ${entry.getKey} value: ${entry.getValue}")

    val options = new UpdateOptions
    options.upsert(true)

    val inserted = execute(mongoCollection.replaceOne(equal("uuid", entry.getValue.id), toDocument(entry.getValue) , options ).toFuture())
    logger.debug(s"Inserting result [ $inserted ]")

  }


  override def load(key: UUID): TwitterProbeIteration = {
    logger.debug(s"Loading record with key : $key")

    val loaded = execute(mongoCollection.find(equal("uuid", key)).first()
      .map(toIteration)
      .toFuture())

    logger.debug(s"Loaded iteration [ ${loaded.head} ]")

    loaded.head
  }

  private def execute[A](await: Awaitable[A]): A = Await.result[A](await, 5000 milliseconds)


  private def toDocument: TwitterProbeIteration => Document = iteration =>
    Document(
      "uuid" -> iteration.id.toString,
      "name" -> iteration.name,
      "creationDate" -> new Date(iteration.lastUpdateTime),
      "lastUpdateTime" -> iteration.lastUpdateTime,
      "minTweetId" -> iteration.minTweetID,
      "maxTweetId" -> iteration.maxTweetID,
      "tweetsCount" -> iteration.tweetsCount,
      "recovery" -> iteration.recovery
    )

  private def toIteration: Document => TwitterProbeIteration = document =>
    TwitterProbeIteration(
      UUID.fromString(document.getString("uuid")),
      document.getString("name"),
      document.getLong("lastUpdateTime"),
      document.getLong("minTweetId"),
      document.getLong("maxTweetId"),
      document.getInteger("tweetsCount"),
      document.getBoolean("recovery")
    )

}
