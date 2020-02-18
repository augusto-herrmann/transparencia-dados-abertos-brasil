Para uma descrição em português, veja o arquivo 🇧🇷[LEIAME.md](LEIAME.md).

[![goodtables.io](https://goodtables.io/badge/github/augusto-herrmann/transparencia-dados-abertos-brasil.svg)](https://goodtables.io/github/augusto-herrmann/transparencia-dados-abertos-brasil)

## Transparency and Open Data Portals of Brazilian states and municipalities

Obtaining a list of transparency and open data portals of all of the 27
Brazilian states and 5,570 municipalities can be a daunting task. This
project has the goal of consolidating and keeping up to date all of that
reference information.

Besides, each state and municipality has executive and legislative branches,
which effectively doubles the work required.

### Steps of data discovery

We take many steps to find the actual transparency and open data portals.
First, we need to find out the institutional websites of city councils and
city halls in Brazil.

#### Finding the websites of city councils and city halls

One would expect for a database containing the official websites of all
city councils and all city halls in Brazil to already exist. But alas, it
does not. So we try to obtain possible links from several sources.

These data sources are in the [sources](sources) directory. Check each
individual data source directory for more information. Some examples of
sources that are already implemented are:

* [tables 31 and 32](sources/research/klein-2017) from the PhD thesis of Rodrigo Klein (2017)/tede/7724)
* [DBPedia](sources/dbpedia), the semantic web tool that extracts structured
  data from [Wikipedia](https://www.wikipedia.org/)

The actual scripts that do the importing are in the
[tools/import](tools/import) directory. They output data that contains
possible links to the websites of city administration, which is stored
in the [data/unverified](data/unverified) directory. Data stored here is
expected to still contain a lot of garbage and **should not be committed
to the repository**.

The next step is link validation. This is done automatically, by a bot, and
manually, with the help of a script. The code for those are in the
[tools/validation](tools/validation) directory. The output, with validated
data, goes to the [data/valid](data/valid) directory.

#### Finding transparency and open data portals in institutional websites

Once we have the links to the official website for city councils and city
halls, we can analyze the content of the pages to look for the presence
of links to transparency and open data portals.

This step is not yet implemented.

### Goals

The goal of this project is to build a reference database of Brazilian
states and municipalities, contemplating the legislative and executive
branches, containing the following data on each one of them:

* official website
* transparency portal
* open data portal

We also intend to collaborate on the monitoring of transparency of Brazilian
states and municipalities in projects such as
[Colaboradados](http://colaboradados.github.io/) and the [list of open data
catalogs in Brazil](https://github.com/dadosgovbr/catalogos-dados-brasil).

