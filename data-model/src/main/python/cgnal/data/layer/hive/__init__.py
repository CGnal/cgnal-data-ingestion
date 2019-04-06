import os


def init_hive(ip_hive_server=None, db_user=None, conf_dict={"spark.app.name": "app"}):
    """
    Init the spark context (hive client)

    :param ip_hive_server: ip of the hive server
    :param db_user: username on database
    :param conf_dict: dictionary of Spark properties.
        For a comprehensive list see https://spark.apache.org/docs/2.2.0/configuration.html

    :return: a tuple with the Spark and the Hive Contexts
    """

    from pyspark import SparkContext, SparkConf
    from pyspark.sql import HiveContext
    from cgnal.logging.defaults import logger

    if db_user is not None:
        os.environ["HADOOP_USER_NAME"] = db_user

    conf = SparkConf()

    for k, v in conf_dict.items():
        conf.set(conf_dict[k], conf_dict[k])

    # conf.set("spark.app.name", "2000m")
    # conf.set("spark.kryoserializer.buffer.max", "2000m")
    # conf.set("spark.sql.shuffle.partitions", 500)
    # conf.set("spark.dynamicAllocation.maxExecutors", "10")
    # conf.set("spark.executor.memory", "8g")
    # conf.set("hive.exec.stagingdir", "/tmp/hive/gtaa_ds_ita_staging")
    # conf.set("hive.exec.scratchdir", "/tmp/hive/gtaa_ds_ita_scratchdir")
    # conf.set("spark.driver.maxResultSize","16g")

    if ip_hive_server is not None:
        pass
        # conf.setMaster(IP_hive_server)

    logger().debug("Spark conf: %s" % str(conf.getAll()))

    sc = SparkContext(conf=conf)
    sqlContext = HiveContext(sc)

    return sqlContext