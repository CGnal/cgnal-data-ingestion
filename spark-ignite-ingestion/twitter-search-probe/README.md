# Twitter Search Probe

Implements the Twitter search probe for downloading the missing tweets for any possible failure that can occur


## Building probe

The Twitter Search Probe is built using sbt , to build the probe run :

```
> sbt clean assembly
```

## Running the probe

To run the search probe execute :

```
> java -jar -Dconfig.file=[your-application.conf-file] twitter-search-probe-assembly-[version].jar
```