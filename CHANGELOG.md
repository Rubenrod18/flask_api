# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.0.0](https://github.com/rubenrod18/flask-api/compare/v0.8.0...v1.0.0) (2020-05-17)


### ⚠ BREAKING CHANGES

* **pip:** update Python dependencies

### Features

* **celery:** add basic installation ([147dd2c](https://github.com/rubenrod18/flask-api/commit/147dd2c90ea0c378de9b99fa272d906afff943d5))
* **db:** add pewee migrations ([231696c](https://github.com/rubenrod18/flask-api/commit/231696c69096174e94526623e3cda31b0987789f))
* **documents:** add document logic ([1eb7ec1](https://github.com/rubenrod18/flask-api/commit/1eb7ec191031f6479af5aefe37e77d3a56cb71bf))
* **emails:** add send emails after creation an user ([7c2cfe0](https://github.com/rubenrod18/flask-api/commit/7c2cfe0a127c5278f15d155d29bac485f1bfceff))
* **log:** add support for logrotate ([09925e1](https://github.com/rubenrod18/flask-api/commit/09925e134e424e507cb46da9d8b391203c8c2fd3))
* **users:** add created_by column in user model ([8a3d013](https://github.com/rubenrod18/flask-api/commit/8a3d013ad774bc119bf12e9d1badcd3a0d4fc447))
* **users:** add Excel and PDF users export to background processes ([781e091](https://github.com/rubenrod18/flask-api/commit/781e09180ec30286295dfa9fd76b8053934e0d45))
* **users:** add recovery password feature ([e1e916e](https://github.com/rubenrod18/flask-api/commit/e1e916e925c3bdb8606d3f45548cd6b423760a6f))


### Build

* **pip:** update requirements.txt ([6193153](https://github.com/rubenrod18/flask-api/commit/6193153fb30dfe3af911a0f4c7e999c4ad6d0d8e))

## [0.8.0](https://github.com/rubenrod18/flask-api/compare/v0.7.0...v0.8.0) (2020-04-29)


### Features

* **roles:** add role logic ([d7a0535](https://github.com/rubenrod18/flask-api/commit/d7a05359667af549fe079d3dcd4e7b63c44fcf56))
* **security:** add jwt authentication ([fb51089](https://github.com/rubenrod18/flask-api/commit/fb51089de828d14887bad0f3417ce08d1f120f3d))
* **users:** add role model integration to user model ([69bc124](https://github.com/rubenrod18/flask-api/commit/69bc12491a3b60ca28b5be05dde0176fbc1be7ae))
* **users:** add user get endpoint ([018b965](https://github.com/rubenrod18/flask-api/commit/018b965f29b3eed8eaaa9bb886d309a963f46573))

## [0.7.0](https://github.com/rubenrod18/flask-api/compare/v0.6.1...v0.7.0) (2020-04-23)

### Features

* **doc:** add standard-version NodeJS package ([c1b2cb3](https://github.com/rubenrod18/flask-api/commit/c1b2cb37702040843c854a9137249273d0793a6b))


### 0.6.1 (2020-04-23)


### ⚠ BREAKING CHANGES

* update python dependencies

### Features

* **db:** added script for creating database tables ([c14b566](https://github.com/rubenrod18/flask-api/commit/c14b566af311335288291386827d036f923160fb))
* **logging:** added logging configuration ([297b9c3](https://github.com/rubenrod18/flask-api/commit/297b9c320b2da008583f269ed2ff2b304fe31e52))
* **seeders:** added user seeder ([e78b4c4](https://github.com/rubenrod18/flask-api/commit/e78b4c4a0b657c9ccb47b67cdcf5139bc6f1e23a))
* **tests:** add tests and code coverage ([17317b7](https://github.com/rubenrod18/flask-api/commit/17317b77154cf03bd48f7f0fb3fd6d4a9619cdf5))
* **validation-requests:** add validation requests with cerberus ([a5beed6](https://github.com/rubenrod18/flask-api/commit/a5beed605ea8d96012d30ce14e98cc84f9d839b4))


### Bug Fixes

* **commitizen:** fixed problem with the process of commitizen tags ([1d3677d](https://github.com/rubenrod18/flask-api/commit/1d3677d9d0a38747542e3aa96e1f186038eb1f6f))
* **docs_to_pdf:** fixed problem about convert a docx file to a pdf file with uWSGI ([aabbc2d](https://github.com/rubenrod18/flask-api/commit/aabbc2d53129078a8e193e05099e7a90c8605757))
* **peewee:** fixed problem about a connection already opened error ([6279470](https://github.com/rubenrod18/flask-api/commit/62794701e01b3dd3ba1482f769f9ec635392e16b))
* **peewee:** problem with database connection already opened ([e6c07c9](https://github.com/rubenrod18/flask-api/commit/e6c07c952820a67b6420431a4c3c9bb5e32dab6a))
* **users:** update user endpoint cannot update data ([9dfc4cc](https://github.com/rubenrod18/flask-api/commit/9dfc4ccdc5d3b60a004efe79b250c4692e9a325c))
* request search fields in search users, export PDF and export Excel endpoints ([2ae7ab7](https://github.com/rubenrod18/flask-api/commit/2ae7ab770499ed62d862506f4356a7c46c3c7b81))


### Build

* update requirements.txt ([f783e78](https://github.com/rubenrod18/flask-api/commit/f783e7848beaf13e5cc1fb67a7ddd42d55d572af))
* update requirements.txt ([b6378ba](https://github.com/rubenrod18/flask-api/commit/b6378ba72f88289b811fa494893e21031338f22f))
