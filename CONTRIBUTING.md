How to contribute to this project.

Este texto também está disponível em português: 🇧🇷[CONTRIBUIR.md](CONTRIBUIR.md).

## Intro

Thank you for your interest in contributing to this project. In order for us
to keep everyone's contributions organised, please follow these guidelines
before you start hacking away.

## Language

This is a bilingual project. In order to keep the pool of possible
contributors as diverse as possible and to be inclusive, write your
contributions in both Portuguese and English if you can. If you aren't
fluent in both languages, we accept contributions in just one of them.
If you are fluent, however, please help by translating parts of the
project that aren't yet bilingual.

## Workflow

We follow a workflow that is pretty common to other open source projects.

1. Start by creating your own fork. There is a button in Github just for that,
   on the upper right corner.
2. Clone your fork to your local machine. It is possible to edit files
   directly in Github's interface, but by cloning the project into your own
   computer gives a lot more flexibility. To clone, type:
   
   `$ git clone http://github.com/<YOUR-GITHUB-USERNAME>/transparencia-dados-abertos-brasil.git`
3. Start a new branch:
   
   `$ git checkout -b issue-nn`
   
   If there is already an issue on the repository about the changes you
   intend to make, please name the branch `issue-nn`, where `nn` is the
   issue number in the repository. That helps us keep track of what it
   is all about, and also gives people a place to comment on if necessary.
4. Do your stuff
   
   Create or change the files to implement your big or small idea that
   will help the project.
5. Add and commit your changes

   ```
   $ git add files-I-changed
   $ git commit -m 'My nifty contribution'
   ```
   
   Use verbs in the infinitive tense and write your commit message in English
   if you can. Try to keep the message descriptive, but succinct, representing
   what you did.
6. Push your changes to your fork

   `$ git push --set-upstream origin issue-nn`
7. Create a new Pull Request

   From your fork page, after detecting your push, Github will offer a button
   to open a new pull request to offer your code for review before being
   incorporated back into the main repository.
   
   Make sure to add a meaningful title and description.

## Types of contributions

You can contribute to any files contained in the repository, but here are some
ideas of contributions that could be useful.

### Data

There are a few kinds of data in the repository:

* valid – the main data of the repository that has been verified in some way.
* auxiliary – data that is not the main objective of the repository, but is
  pretty useful to have around nearby, anyway. Only verified data should go
  here.
* archive – data that is no longer used by the project, but is kept for
  archival purposes. Old data here should never change.
* unverified – unverified data should be kept out of the repository. Store
  here only temporary data and never commit it. `.gitignore` is configured
  to automatically exclude files in this directory.

Make sure you run

```
$ goodtables data/.../datapackage.json
```

on the data you're working on, before committing to the repository. That
ensures that only valid data comes in.

Make sure you have `goodtables` command available on your command line, by
following the instructions on our [README](README.md) or Goodtable's own
[installation instructions](https://github.com/frictionlessdata/goodtables-py#installing).

### Code

This repository contains not only data, but also the scripts required to move
data around and validate it. Scripts live in the [tools](tools/) directory.

When adding a new script, make sure you include also proper documentation (a
README.md file is enough), with instructions on how to use it. Also include
any setup required, such as a registry of dependencies. If it's a Python
script, include a `requirements.txt` file pinning the version numbers of
libraries used.

#### Import scripts

[These](tools/import/) are scripts that import data from external
[sources](#sources) into the project. Data output from import scripts usually
goes into the [data/unverified](data/unverified/) directory.

#### Export scripts

[These](tools/export/) are scripts that export data from this project to other
projects that we contribute to.

#### Validation scripts

[These](tools/export/) scripts do validation of data in the
[data/unverified](data/unverified/) directory and output to
[data/valid](data/valid/). Data can be validated either automatically or
manually. In that case, it's usually a script that take input from the user in
order to help them manually validate data in a way.

### Sources

Documentation on data sources. Use text in markdown and
[data packages](https://frictionlessdata.io/specs/data-package/) to do it.

### Documentation

Markdown files such as this one that document the overall project. Improvement
proposals on those are also quite welcome.

### Issues

If you have an idea on how to improve something, but are not quite sure on how
to implement it, or want to discuss it beforehand, please open an
[issue](https://github.com/augusto-herrmann/transparencia-dados-abertos-brasil/issues) about it.

