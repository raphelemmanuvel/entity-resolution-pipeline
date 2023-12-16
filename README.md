# Entity Resolution Pipeline

<p align="center">
  <img src="docs/plot.png">
</p>


### [Entity Relationship - Interactive Plot](https://raphelemmanuvel.github.io/entity-resolution-pipeline/)
### [Data Source](https://firststop.sos.nd.gov/search/business)
### [Data used for Entity Resolution](https://github.com/raphelemmanuvel/entity-resolution-pipeline/blob/main/tmp/data/active_listings_x.csv)

### Usage


### Run web_crawler service to pull data from the source and parse it to output file.

* Search parameter for the crawler and the output file path can be configured with the command in docker-compose.yml.  

```sh
docker-compose run web_crawler
```  

### Run er service to visualize the relationship between entities in the crawled data.

* Output file path for the plot can be configured with the command in docker-compose.yml.  

```sh
docker-compose run er
```  

### Format Python Scripts.

```sh
docker-compose run format
```  
