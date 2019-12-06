[DBPedia](https://wiki.dbpedia.org/) automatically extracts data from
Wikipedia and may contain links to the municipalities' websites.

The Portuguese language DBPedia extracts data from the Portuguese language
Wikipedia, while the English language DBPedia extracts data from the English
language Wikipedia. We are going to query them both.

## Portuguese language DBPedia

The Portuguese language DBPedia does not use the `dbo:country` property, so
getting Brazilian cities is a little tricky. Here we use having a link to
the wiki page "States of Brazil" as a filter for getting only cities located
in Brazil, instead.

The use of the `foaf:homepage` property is rare, so we have to resort to using
a `dbo:wikiPageExternalLink` property in addition to that. Keep in mind that
this will pollute the results to other pages which are not the official pages
of the municipality, so we need to filter them out somehow. The simplest way
of doing that is by using a SPARQL `FILTER` clause to get only containing
`.gov.br`. Unfortunately, some municipality websites do not conform to that
and will be missing in the query.

The following SPARQL query will extract links from the Portuguese language
DBPedia:

```sparql
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo:<http://dbpedia.org/ontology/>
PREFIX dbp:<http://dbpedia.org/property/>
PREFIX dbr:<http://dbpedia.org/resource/>

SELECT ?city, ?name, ?state, ?link WHERE {
    ?city a dbo:City ;
        dbo:wikiPageWikiLink dbr:States_of_Brazil ;
        dbo:wikiPageExternalLink|foaf:homepage ?link .
    FILTER REGEX(STR(?link), ".gov.br")
    OPTIONAL {?city rdfs:label ?name}
    OPTIONAL {?city dbp:estado ?state}
}
```

Results in
[HTML](http://pt.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+rdf%3A%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+dbo%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+dbp%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fproperty%2F%3E%0D%0APREFIX+dbr%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2F%3E%0D%0A%0D%0ASELECT+%3Fcity%2C+%3Fname%2C+%3Fstate%2C+%3Flink+WHERE+%7B%0D%0A++++%3Fcity+a+dbo%3ACity+%3B%0D%0A++++++++dbo%3AwikiPageWikiLink+dbr%3AStates_of_Brazil+%3B%0D%0A++++++++dbo%3AwikiPageExternalLink%7Cfoaf%3Ahomepage+%3Flink+.%0D%0A++++FILTER+REGEX%28STR%28%3Flink%29%2C+%22.gov.br%22%29%0D%0A++++OPTIONAL+%7B%3Fcity+rdfs%3Alabel+%3Fname%7D%0D%0A++++OPTIONAL+%7B%3Fcity+dbp%3Aestado+%3Fstate%7D%0D%0A%7D&should-sponge=&format=text%2Fhtml&timeout=0&debug=on)
and
[CSV](http://pt.dbpedia.org/sparql?default-graph-uri=&query=PREFIX+rdf%3A%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+dbo%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+dbp%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fproperty%2F%3E%0D%0APREFIX+dbr%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2F%3E%0D%0A%0D%0ASELECT+%3Fcity%2C+%3Fname%2C+%3Fstate%2C+%3Flink+WHERE+%7B%0D%0A++++%3Fcity+a+dbo%3ACity+%3B%0D%0A++++++++dbo%3AwikiPageWikiLink+dbr%3AStates_of_Brazil+%3B%0D%0A++++++++dbo%3AwikiPageExternalLink%7Cfoaf%3Ahomepage+%3Flink+.%0D%0A++++FILTER+REGEX%28STR%28%3Flink%29%2C+%22.gov.br%22%29%0D%0A++++OPTIONAL+%7B%3Fcity+rdfs%3Alabel+%3Fname%7D%0D%0A++++OPTIONAL+%7B%3Fcity+dbp%3Aestado+%3Fstate%7D%0D%0A%7D&should-sponge=&format=text%2Fcsv&timeout=0&debug=on).

## English language DBPedia

This is query is a little more complicated compared to the Portuguese language
DBPedia, because while the data is more structured, we cannot get
information about the state directly. Other cities have no state information
assigned.

At least for filtering by country we can simply use the
`dbo:country` property to determine that a city is located in Brazil.

```sparql
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbo:<http://dbpedia.org/ontology/>
PREFIX dbr:<http://dbpedia.org/resource/>
PREFIX dbp:<http://dbpedia.org/property/>
PREFIX yago:<http://dbpedia.org/class/yago/>

SELECT ?city, ?name, ?state_abbr, ?state_name, ?link, ?external_link WHERE {
    ?city a dbo:City ;
        dbo:country dbr:Brazil .
    OPTIONAL {
        ?city foaf:homepage ?link .
    }
    OPTIONAL {
        FILTER REGEX(STR(?external_link), ".gov.br")
        ?city dbo:wikiPageExternalLink ?external_link .
    }
    OPTIONAL {
        ?city rdfs:label ?name
        FILTER(LANG(?name) = "" || LANGMATCHES(LANG(?name), "pt"))
    }
    OPTIONAL {
        ?city dbo:isPartOf ?state .
        ?state a yago:WikicatStatesOfBrazil .
        ?state dbp:coordinatesRegion ?state_abbr .
    }
    OPTIONAL {
        ?city dbo:isPartOf ?state .
        ?state a yago:WikicatStatesOfBrazil .
        ?state rdfs:label ?state_name .
        FILTER(LANG(?state_name) = "" || LANGMATCHES(LANG(?state_name), "pt"))
    }
    OPTIONAL { # cities linked to a state whose URI has changed
        ?city dbo:isPartOf ?state_old_page .
        ?state_old_page dbo:wikiPageRedirects ?state .
        ?state a yago:WikicatStatesOfBrazil .
        ?state dbp:coordinatesRegion ?state_abbr .
    }
    OPTIONAL { # cities wrongfully linked to a city instead of state
        ?city dbo:isPartOf ?other_city .
        ?other_city dbo:isPartOf ?state .
        ?state a yago:WikicatStatesOfBrazil .
        ?state dbp:coordinatesRegion ?state_abbr .
    }
}
```

Results in
[HTML](http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=PREFIX+rdf%3A%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+dbo%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+dbr%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2F%3E%0D%0APREFIX+dbp%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fproperty%2F%3E%0D%0APREFIX+yago%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fclass%2Fyago%2F%3E%0D%0A%0D%0ASELECT+%3Fcity%2C+%3Fname%2C+%3Fstate_abbr%2C+%3Fstate_name%2C+%3Flink%2C+%3Fexternal_link+WHERE+%7B%0D%0A++++%3Fcity+a+dbo%3ACity+%3B%0D%0A++++++++dbo%3Acountry+dbr%3ABrazil+.%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+foaf%3Ahomepage+%3Flink+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++FILTER+REGEX%28STR%28%3Fexternal_link%29%2C+%22.gov.br%22%29%0D%0A++++++++%3Fcity+dbo%3AwikiPageExternalLink+%3Fexternal_link+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+rdfs%3Alabel+%3Fname%0D%0A++++++++FILTER%28LANG%28%3Fname%29+%3D+%22%22+%7C%7C+LANGMATCHES%28LANG%28%3Fname%29%2C+%22pt%22%29%29%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+dbp%3AcoordinatesRegion+%3Fstate_abbr+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+rdfs%3Alabel+%3Fstate_name+.%0D%0A++++++++FILTER%28LANG%28%3Fstate_name%29+%3D+%22%22+%7C%7C+LANGMATCHES%28LANG%28%3Fstate_name%29%2C+%22pt%22%29%29%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B+%23+cities+linked+to+a+state+whose+URI+has+changed%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fstate_old_page+.%0D%0A++++++++%3Fstate_old_page+dbo%3AwikiPageRedirects+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+dbp%3AcoordinatesRegion+%3Fstate_abbr+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B+%23+cities+wrongfully+linked+to+a+city+instead+of+state%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fother_city+.%0D%0A++++++++%3Fother_city+dbo%3AisPartOf+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+dbp%3AcoordinatesRegion+%3Fstate_abbr+.%0D%0A++++%7D%0D%0A%7D&format=text%2Fhtml&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+)
and
[CSV](http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=PREFIX+rdf%3A%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+dbo%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fontology%2F%3E%0D%0APREFIX+dbr%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2F%3E%0D%0APREFIX+dbp%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fproperty%2F%3E%0D%0APREFIX+yago%3A%3Chttp%3A%2F%2Fdbpedia.org%2Fclass%2Fyago%2F%3E%0D%0A%0D%0ASELECT+%3Fcity%2C+%3Fname%2C+%3Fstate_abbr%2C+%3Fstate_name%2C+%3Flink%2C+%3Fexternal_link+WHERE+%7B%0D%0A++++%3Fcity+a+dbo%3ACity+%3B%0D%0A++++++++dbo%3Acountry+dbr%3ABrazil+.%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+foaf%3Ahomepage+%3Flink+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++FILTER+REGEX%28STR%28%3Fexternal_link%29%2C+%22.gov.br%22%29%0D%0A++++++++%3Fcity+dbo%3AwikiPageExternalLink+%3Fexternal_link+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+rdfs%3Alabel+%3Fname%0D%0A++++++++FILTER%28LANG%28%3Fname%29+%3D+%22%22+%7C%7C+LANGMATCHES%28LANG%28%3Fname%29%2C+%22pt%22%29%29%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+dbp%3AcoordinatesRegion+%3Fstate_abbr+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+rdfs%3Alabel+%3Fstate_name+.%0D%0A++++++++FILTER%28LANG%28%3Fstate_name%29+%3D+%22%22+%7C%7C+LANGMATCHES%28LANG%28%3Fstate_name%29%2C+%22pt%22%29%29%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B+%23+cities+linked+to+a+state+whose+URI+has+changed%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fstate_old_page+.%0D%0A++++++++%3Fstate_old_page+dbo%3AwikiPageRedirects+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+dbp%3AcoordinatesRegion+%3Fstate_abbr+.%0D%0A++++%7D%0D%0A++++OPTIONAL+%7B+%23+cities+wrongfully+linked+to+a+city+instead+of+state%0D%0A++++++++%3Fcity+dbo%3AisPartOf+%3Fother_city+.%0D%0A++++++++%3Fother_city+dbo%3AisPartOf+%3Fstate+.%0D%0A++++++++%3Fstate+a+yago%3AWikicatStatesOfBrazil+.%0D%0A++++++++%3Fstate+dbp%3AcoordinatesRegion+%3Fstate_abbr+.%0D%0A++++%7D%0D%0A%7D&format=text%2Fcsv&CXML_redir_for_subjs=121&CXML_redir_for_hrefs=&timeout=30000&debug=on&run=+Run+Query+).
