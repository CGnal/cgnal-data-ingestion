# Spark-Ignite Twitter Client Probe

Implements the Twitter Probe as client node in an Apache Ignite topology using Apache Spark Streaming


## Building probe

The Twitter Client Probe is built using sbt , to build the probe run : 

```

> sbt clean assembly

```


## Running the probe

To run the client probe execute :

```

> java -jar -Dconfig.file=[your-application.conf-file] twitter-client-probe-assembly-[version].jar

```

## Configuration

Here an example of application.conf 

```
files {
  keywords : "- your keywords file -"
}

documents {
  dbName : "documents-cache-spx"
}

twitter {

  consumerKey       : "*"
  consumerSecret    : "*"
  accessToken       : "*"
  accessTokenSecret : "*"

}

mongo {

  user : "- your user -"
  password : "- your password -"
  host : "- your host -"
  port : 27017

}

rest {
  port : 8020
}

streaming {
  processingWindow : 30
}
```

## The probe REST API

The running probe has a set of API that expose information on the status of the probe

### The health API

```
http://localhost:8020/health
```


### The config API
```
http://localhost:8020/config
```

### The runtime API
```
http://localhost:8020/runtime
```
