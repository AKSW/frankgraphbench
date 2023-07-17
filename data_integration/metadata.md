# Metadata for data enriching
Some useful DBpedia's properties for enriching Recommender Systems datasets, considering their domain (movies, books, artists ...)

# Datasets
Useful properties per dataset.

## MovieLens-100k
*dbo:Film* *maybe* useful properties/resources:
- dct:subject*
- dbo:genre
- dbo:author
- dbo:creator
- dbo:starring*
- dbo:cinematography
- dbo:director*
- dbo:series
- dbo:portrayer
- dbo:basedOn
- dbo:previousWork
- dbo:subsequentWork
- dbo:notableWork
- dbo:chiefEditor
- dbo:producedBy
- dbo:producer
- dbo:publisher
- dbo:writer
- dbo:musicComposer 
- dbo:award
- dbo:description
- dbo:distributor
- dbo:influencedBy
- dbo:isPartOf
- dbo:show

After removing some properties that aren't used, the final query template obtained is:

```
    PREFIX dct:  <http://purl.org/dc/terms/>
    PREFIX dbo:  <http://dbpedia.org/ontology/>
    PREFIX dbr:  <http://dbpedia.org/resource/>
    PREFIX rdf:	 <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT
        ?abstract 
        (GROUP_CONCAT(DISTINCT ?producer; SEPARATOR="::") AS ?producer)
        (GROUP_CONCAT(DISTINCT ?distributor; SEPARATOR="::") AS ?distributor)
        (GROUP_CONCAT(DISTINCT ?writer; SEPARATOR="::") AS ?writer)
        (GROUP_CONCAT(DISTINCT ?cinematography; SEPARATOR="::") AS ?cinematography)
        (GROUP_CONCAT(DISTINCT ?subject; SEPARATOR="::") AS ?subject)
        (GROUP_CONCAT(DISTINCT ?starring; SEPARATOR="::") AS ?starring)
        (GROUP_CONCAT(DISTINCT ?director; SEPARATOR="::") AS ?director)
    WHERE {
        OPTIONAL { <$URI>   dct:subject         ?subject            }   .
        OPTIONAL { <$URI>   dbo:starring        ?starring           }   .
        OPTIONAL { <$URI>   dbo:director        ?director           }   .
        OPTIONAL { <$URI>   dbo:abstract        ?abstract           }   .
        OPTIONAL { <$URI>   dbo:producer        ?producer           }   .
        OPTIONAL { <$URI>   dbo:distributor     ?distributor        }   .
        OPTIONAL { <$URI>   dbo:writer          ?writer             }   .
        OPTIONAL { <$URI>   dbo:cinematography  ?cinematography     }   .

        FILTER(LANG(?abstract) = 'en')
    }
```