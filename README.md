A survey of Brazilian states' and municipalities' transparency and open data portals, as well as institutional websites, obtained from several public data sources.

Este texto também está disponível em português: 🇧🇷[LEIAME.md](LEIAME.md).

[![Frictionless-repository](https://github.com/augusto-herrmann/transparencia-dados-abertos-brasil/actions/workflows/frictionless.yaml/badge.svg)](https://repository.frictionlessdata.io/report?user=augusto-herrmann&repo=transparencia-dados-abertos-brasil&flow=frictionless)

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

* [tables 31 and 32](sources/research/klein-2017) from the PhD thesis of
  Rodrigo Klein (2017)
* [DBPedia](sources/dbpedia), the semantic web tool that extracts structured
  data from [Wikipedia](https://www.wikipedia.org/)

The actual scripts that do the importing are in the
[tools/import](tools/import) directory. They output data that contains
possible links to the websites of city administration, which is stored
in the [data/unverified](data/unverified) directory. Data stored here is
expected to still contain a lot of garbage and **should not be committed
to the repository**.

##### Validation

The next step is link validation. This is done automatically, by a bot, and
manually, with the help of a script. The code for those are in the
[tools/validation](tools/validation) directory. The output, with validated
data, goes to the [data/valid](data/valid) directory.

We also apply the concept of
[continuous data integration](http://okfnlabs.org/blog/2016/05/17/automated-data-validation.html)
to keep the integrity of data already validated. It's like
[continuous integration](https://en.wikipedia.org/wiki/Continuous_integration),
but for data instead of software. It helps keep the incorrect data out of the
repository, as every commit and pull request gets automatically verified,
thanks to a workflow on Github Actions that calls the
[Frictionless Repository](https://repository.frictionlessdata.io/) validation service.

Metadata is maintained using the
[Data Package specification](https://frictionlessdata.io/specs/data-package/),
which also removes the friction out of the process of reusing the data. For
more information, see the [Frictionless Data](https://frictionlessdata.io/)
website.

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

### Contributing

We welcome contributions to the project. If you have an idea or want to
improve something, please check out the [contributing guide](CONTRIBUTING.md).

We also intend to collaborate on the monitoring of transparency of Brazilian
states and municipalities in projects such as
[Colaboradados](http://colaboradados.github.io/) and the [list of open data
catalogs in Brazil](https://github.com/dadosgovbr/catalogos-dados-brasil).

