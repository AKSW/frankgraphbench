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

Statistics report for MovieLens-100k:
- number of entities with the property abstract: 1453 (99.73%)
- number of entities with the property producer: 1120 (76.87%)
- number of entities with the property distributor: 1277 (87.65%)
- number of entities with the property writer: 1212 (83.18%)
- number of entities with the property cinematography: 1060 (72.75%)
- number of entities with the property subject: 1457 (100.00%)
- number of entities with the property starring: 1367 (93.82%)
- number of entities with the property director: 1358 (93.21%)

Statistics report for MovieLens-1m:
- number of entities with the property item_id: 3347 (100.00%)
- number of entities with the property abstract: 3342 (99.85%)
- number of entities with the property producer: 2513 (75.08%)
- number of entities with the property distributor: 2891 (86.38%)
- number of entities with the property writer: 2775 (82.91%)
- number of entities with the property cinematography: 2414 (72.12%)
- number of entities with the property subject: 3347 (100.00%)
- number of entities with the property starring: 3116 (93.10%)
- number of entities with the property director: 3120 (93.22%)
