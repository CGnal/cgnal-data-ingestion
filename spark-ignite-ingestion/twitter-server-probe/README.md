# Ignite Server Probe

Implements the generic server node in an Apache Ignite topology


## Building probe

The Server Probe is built using sbt, to build the probe run :  

```

> sbt clean assembly

```


## Running the probe

To run the a single node execute :

```

> java -jar -Dconfig.file=[your-application.conf-file] server-probe-assembly-[version].jar

```

NOTE: you can execute how many node you wish, depending on the Ignite cache-configuration each node can auto-cluster itself with the others

## Configuration

Here an example of application.conf 

```
documents {
  dbName : "documents-cache-spx"
}

mongo {

  user : "- your username -"
  password : "- your password -"
  host : "- your host -"
  port : 27017

}

rest {
  port : 8010
}
```


## The REST API

The running probe has a set of API that expose information on the status of the probe

### The health API

```
http://localhost:8010/health
```


### The config API
```
http://localhost:8010/config
```