# Entity Resolution Pipeline

### Usage


### Running web_crawler service to pull data from the source and parse it to output file.

* Search parameter for the crawler and the output file path can be configured with the command in docker-compose.yml.  

```sh
docker-compose run web_crawler
```  

### Running er service to visualize the relationship between companies, registered agents, and owners in the crawled data.

* Output file path for the plot can be configured with the command in docker-compose.yml.  

```sh
docker-compose run er
```  
