package com.cgnal.twitter.probe.common.cache

import com.cgnal.data.access.ignite.mongo.DocumentMongoStorageAdapter
import com.cgnal.data.model.Document
import com.cgnal.twitter.probe.common.config.TwitterProbeConfig
import javax.cache.configuration.FactoryBuilder
import org.apache.ignite.cache.CacheMode
import org.apache.ignite.cache.eviction.fifo.FifoEvictionPolicyFactory
import org.apache.ignite.configuration.CacheConfiguration

trait CacheConfig {

  protected def createDocumentCacheConfig: CacheConfiguration[String, Document] = {

    val cacheCfg: CacheConfiguration[String, Document] = new CacheConfiguration[String, Document]()

    cacheCfg.setName(TwitterProbeConfig.documentsDbName)
    cacheCfg.setBackups(1)
    cacheCfg.setCacheMode(CacheMode.PARTITIONED)

    cacheCfg.setIndexedTypes(classOf[String], classOf[Document])

    cacheCfg.setCacheStoreFactory(FactoryBuilder.factoryOf(classOf[DocumentMongoStorageAdapter]))
    cacheCfg.setReadThrough(true)
    cacheCfg.setWriteThrough(true)

    // Setting eviction policy
    cacheCfg.setOnheapCacheEnabled(true)
    cacheCfg.setEvictionPolicyFactory(new FifoEvictionPolicyFactory[String,Document](200000))

    // Set write-behind flag for synchronous/asynchronous persistent store update
    cacheCfg.setWriteBehindEnabled(true)
    cacheCfg.setWriteBehindFlushSize(2000)
    //cacheCfg.setWriteBehindFlushFrequency(5000)

    cacheCfg
  }

}
