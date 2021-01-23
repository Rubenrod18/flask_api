# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [2.0.2](https://github.com/rubenrod18/flask_api/compare/v2.0.1...v2.0.2) (2021-01-23)


### Bug Fixes

* **celery:** new settings name are not applies on celery 4.4.7 ([f1a0bff](https://github.com/rubenrod18/flask_api/commit/f1a0bffda260b1bb647037c8f708541523fc600c))
* **middleware:** correct middleware for allowing to let in Swagger ([441b077](https://github.com/rubenrod18/flask_api/commit/441b077e963fda836258ce9fc1550543486f61dc))
* **tasks:** correct task for sending an email with attachments ([43d516c](https://github.com/rubenrod18/flask_api/commit/43d516cd2a4472fb222aeba62eab1bef87739496))


### Build System

* **pip:** update python dependencies ([8964eed](https://github.com/rubenrod18/flask_api/commit/8964eed7f12870b70ae410d9633e47faabafc679))


### Code Refactoring

* **blueprints:** update way to register all blueprints ([b7692b2](https://github.com/rubenrod18/flask_api/commit/b7692b238679c85f90b7a5120f9297392d6b03ce))
* update way to test Celery tasks ([eb3f72d](https://github.com/rubenrod18/flask_api/commit/eb3f72d39db808f5932b3c2aea6dc4c35a01a83a))
* **celery:** update way to run Celery ([dee133d](https://github.com/rubenrod18/flask_api/commit/dee133d02cec4650c3203567589cf77f1f0bc761))
* **factories:** update way to create a model instance from a factory ([ddfcb7d](https://github.com/rubenrod18/flask_api/commit/ddfcb7d81784d57685f0daac7ee51d7fd127ddd9))
* **swagger:** update order field format ([ccbfcda](https://github.com/rubenrod18/flask_api/commit/ccbfcdab4ffa9b26fa26bf3ada06f4b09739741b))
* **tasks:** exclude internal_filename in Celery tasks ([53dcf6d](https://github.com/rubenrod18/flask_api/commit/53dcf6d2b6db728f71d060b2da838472111a1c23))

## [2.0.1](https://github.com/rubenrod18/flask_api/compare/v2.0.0...v2.0.1) (2021-01-05)


### Bug Fixes

* **tasks:** correct output data on serializers and swagger ([d5c050a](https://github.com/rubenrod18/flask_api/commit/d5c050af9f087290112a5b8c08d3f8ec1baf33a0))


### Build System

* **npm:** update npm dependencies for fixing a vulnerability found ([15ee5de](https://github.com/rubenrod18/flask_api/commit/15ee5de92b126bf6ceb5216cb533b9832b4f00d4))
* **pip:** update Python packages ([11676b6](https://github.com/rubenrod18/flask_api/commit/11676b65ce6c1f06f4478640c2aece33bcd984f6))


### Code Refactoring

* **blueprints:** import dynamic way ([30ee0a0](https://github.com/rubenrod18/flask_api/commit/30ee0a00940eb4c9eb555b74e162bd6e9179116c))
* **blueprints:** remove logging module from all blueprints ([a51709e](https://github.com/rubenrod18/flask_api/commit/a51709eacd07f8f58e2550d9b8ddbe5506a8b7f2))
* **db:** models available could be import from init module ([2361e0e](https://github.com/rubenrod18/flask_api/commit/2361e0e0641ae66e95d9f9226a59052893de2e1e))
* **db:** move user_roles model to its own module ([650eb39](https://github.com/rubenrod18/flask_api/commit/650eb3978a5b0c55fab42c54a835556b7e812b52))
* **exceptions:**  add error handler to marshmallow validation error class ([10bb664](https://github.com/rubenrod18/flask_api/commit/10bb6649017c3fafc3f504adc5cd9606f238fc57))
* **exceptions:** correct error handler to marshmallow validation error class ([ba30805](https://github.com/rubenrod18/flask_api/commit/ba308058379b7942d86d7b8affe3093833590151))
* **managers:** add new logic for managing database queries through database models ([758e077](https://github.com/rubenrod18/flask_api/commit/758e077e66812934d9843425a7acf18a855ff747))
* **serializers:** correct user email validation ([2d733cf](https://github.com/rubenrod18/flask_api/commit/2d733cf4148d804a7e1f2f344b28dde96ea322e6))
* **serializers:** move app.marshmallow_schema.py to serializers package ([47f75e1](https://github.com/rubenrod18/flask_api/commit/47f75e13832fa67b64ad013187e6ad3a589b3e5f))
* **serializers:** upgrade validation fields ([24ac198](https://github.com/rubenrod18/flask_api/commit/24ac198caa6efa92ab87848644f0db0729ff7010))
* **services:** add new logic for managing business logic to auth ([3c969b5](https://github.com/rubenrod18/flask_api/commit/3c969b559f155d10ce255c85b083d2b9d83ffc6b))
* **services:** add new logic for managing business logic to documents ([1ce7b96](https://github.com/rubenrod18/flask_api/commit/1ce7b9666224c71e9988e1091f2e7cae9ca94934))
* **services:** add new logic for managing business logic to roles ([7fff4c1](https://github.com/rubenrod18/flask_api/commit/7fff4c1acbbe1233e006d5764565fe7a3c9f65fc))
* **services:** add new logic for managing business logic to tasks ([079741d](https://github.com/rubenrod18/flask_api/commit/079741d0be83a191fea63679a084f905e40a5214))
* **services:** add new logic for managing business logic to users ([572f37f](https://github.com/rubenrod18/flask_api/commit/572f37f24a6abaff7055def28bfb1179a9cc5b6d))
* **swagger:** move app.utils.swagger_models to app.swagger package ([ef4dd87](https://github.com/rubenrod18/flask_api/commit/ef4dd874fde42da66b7a8dc650457d514d457963))
* **swagger:** update document swagger models ([7015c61](https://github.com/rubenrod18/flask_api/commit/7015c61d5e2eb69d334b137b3ed692d6a1950249))
* **swagger:** update role swagger models ([d618021](https://github.com/rubenrod18/flask_api/commit/d618021f93839bb5989cbb39191f38fad82ca2d7))
* **swagger:** update user swagger models ([766e697](https://github.com/rubenrod18/flask_api/commit/766e697ab72b86f4ae4d3827d85faf16298bbbc9))
* **tasks:** add suffix to task names ([998a56d](https://github.com/rubenrod18/flask_api/commit/998a56dc4c88c94ba43b6d512364f0b9177fe52d))
* **utils:** create new modules to constants and request query operators ([cbf12c9](https://github.com/rubenrod18/flask_api/commit/cbf12c98008c69ffe5ae3af9a6a6eabebeda93ad))

## [2.0.0](https://github.com/rubenrod18/flask_api/compare/v1.4.1...v2.0.0) (2020-10-27)


### ⚠ BREAKING CHANGES

* order field in search requests is a list of dicts.

### Features

* **factories:** add prevent code for checking if a given model is registered as factory ([1605a01](https://github.com/rubenrod18/flask_api/commit/1605a019833cec770e2b99e1ed05e92d4d65e32d))
* **shell:** import Factory class to Flask interactive shell ([8cf9c8e](https://github.com/rubenrod18/flask_api/commit/8cf9c8ef6a60b3ed24a30ec91ec6a6cfe3f5cf30))


### Code Refactoring

* replace cerberus to flask-mashmallow validation ([7552d5c](https://github.com/rubenrod18/flask_api/commit/7552d5c6ab11d8c32c8f5f29729981154e680b82))
* **celery:** replace old Celery setting names with new ones ([15e0c03](https://github.com/rubenrod18/flask_api/commit/15e0c0359f07521c4d73c9cb7a3bf0c41240cd63))
* **celery:** update way to set FLASK_CONFIG value on Flask command ([a865548](https://github.com/rubenrod18/flask_api/commit/a86554852a20a2bc625e5f289e20c5cf624178ec))


### Build System

* add .versionrc that shows build/perf/refactor/revert ([0017d66](https://github.com/rubenrod18/flask_api/commit/0017d661d0e8861e40690ef50e454af55aafd785))
* add sphinx-click configuration to Sphinx and create new file for showing Click documentation ([bb41b7b](https://github.com/rubenrod18/flask_api/commit/bb41b7b587e9919d731cd78fa5ad1e6afac9f91a))
* add sphinx-click for showing Click documentation in Sphinx ([c0a8f55](https://github.com/rubenrod18/flask_api/commit/c0a8f5501ec2604885b30b9b336c55d4584ff5b8))
* **pip:** remove cerberus package ([4a4fe72](https://github.com/rubenrod18/flask_api/commit/4a4fe7265b84857581480b4c0ddd464d852bf6b2))
* **pip:** split python packages in two requirements local and production ([f39a2a5](https://github.com/rubenrod18/flask_api/commit/f39a2a5f8c89aa9f0ff1f25150d0315274d527ba))

## [1.4.1](https://github.com/rubenrod18/flask-api/compare/v1.4.0...v1.4.1) (2020-10-07)


### Bug Fixes

* **celery:** correct problem when start Celery ([52ad2fb](https://github.com/rubenrod18/flask-api/commit/52ad2fb572de31950dea3cad7ff88ddf209a187f)), closes [#3](https://github.com/rubenrod18/flask-api/issues/3)

## [1.4.0](https://github.com/rubenrod18/flask-api/compare/v1.3.0...v1.4.0) (2020-10-04)


### Features

* **celery:** add task for exporting several files ([ca8355f](https://github.com/rubenrod18/flask-api/commit/ca8355fce92085d581b3b52c4431afb797004172))
* **documentation:** add sphinx integration ([8c313fd](https://github.com/rubenrod18/flask-api/commit/8c313fd66e1503a7a95593226343a3033fdffa7b))

## [1.3.0](https://github.com/rubenrod18/flask-api/compare/v1.2.0...v1.3.0) (2020-09-20)


### Features

* **swagger:** add Swagger full integration ([1eaf8d8](https://github.com/rubenrod18/flask-api/commit/1eaf8d8fda1af6efdaae7430ef042081f0c924b0))

## [1.2.0](https://github.com/rubenrod18/flask-api/compare/v1.1.0...v1.2.0) (2020-09-18)


### ⚠ BREAKING CHANGES

* install/update Node.js and Python libraries

### build

* update Node.js and Python packages ([b7416cc](https://github.com/rubenrod18/flask-api/commit/b7416ccae2e6f2ddcf903417a2ffe54f73891604))

## [1.1.0](https://github.com/rubenrod18/flask-api/compare/v1.0.0...v1.1.0) (2020-05-31)


### Features

* **security:** add role-based authorization ([345b57e](https://github.com/rubenrod18/flask-api/commit/345b57e2168f0139e9670f8a8b7fccb4072d7b36))
* add advanced search in documents, roles and users ([8fce3e3](https://github.com/rubenrod18/flask-api/commit/8fce3e36c3231357f49e663706b30b0af8938c8e))
* add marshmallow package integration ([a8b647e](https://github.com/rubenrod18/flask-api/commit/a8b647e409e246407f04482020395b873ac5547f))
* add Swagger integration ([dc6ace4](https://github.com/rubenrod18/flask-api/commit/dc6ace43c9dfde3358ec4775fff8fca4ff02248a))


### Refactor

* replace HTTP exceptions to Werkzeug HTTP Exceptions ([31e5606](https://github.com/rubenrod18/flask-api/commit/31e5606116f32a10137c9d16d5bec47b886739f1))
* move Word and Excel celery tasks to them own modules ([00e42e5](https://github.com/rubenrod18/flask-api/commit/00e42e59dba6508119fb69507a1e004975adc939))


### Docs

* docs: add installation project guide ([b915d31](https://github.com/rubenrod18/flask-api/commit/b915d3124c717f727441e555e42b7cd483e26410))

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


## 0.6.1 (2020-04-23)


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
