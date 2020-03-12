## Intro

Thank you for your interest in contributing to this project. In order for us
to keep everyone's contributions organized, please follow these guidelines
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
   
   `$ git clone http://github.com/<YOUR-GITHUB-USERNAME>/brasil.io.git`
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
   $ git commit -am 'My nifty contribution'
   ```
6. Push your changes to your fork

   `$ git push --set-upstream origin issue-nn`
7. Create a new Pull Request

   From your fork page, after detecting your push, Github will offer a button
   to open a new pull request to offer your code for review before being
   incorporated back into the main repository.
   
   Make sure to add a meaningul title and description.

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

### Code

Scripts to move data around and validate it.

### Sources

Documentation on data sources.

### Documentation

Markdown files such as this one that document the project.

