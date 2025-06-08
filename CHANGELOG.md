# Changelog

All notable changes to this project will be documented in this file. See [commit-and-tag-version](https://github.com/absolute-version/commit-and-tag-version) for commit guidelines.

## [4.0.0](https://github.com/rubenrod18/flask_api/compare/v3.1.0...v4.0.0) (2025-06-08)


### ⚠ BREAKING CHANGES

* manager classes have been removed, use repository instead
* migrate from pip-tools to poetry

### Build System

* **npm:** update doc commands ([11dc8fe](https://github.com/rubenrod18/flask_api/commit/11dc8fe4c34241ee55f4ec5e9c2fffeede6de864))
* **pip:** add pylint as an extra python linter ([#105](https://github.com/rubenrod18/flask_api/issues/105)) ([eecb1d1](https://github.com/rubenrod18/flask_api/commit/eecb1d1bfb969c5317d899ee79d4a3980f940dd5))
* **pip:** bump coverage from 7.8.0 to 7.8.1 in /src ([#100](https://github.com/rubenrod18/flask_api/issues/100)) ([8bb0387](https://github.com/rubenrod18/flask_api/commit/8bb0387f6425596adc31158e2b0436b2922785d9))
* **pip:** bump coverage from 7.8.1 to 7.8.2 in /src ([#103](https://github.com/rubenrod18/flask_api/issues/103)) ([15acc2f](https://github.com/rubenrod18/flask_api/commit/15acc2f908072302851ee3a5de30986117265d22))
* **pip:** bump faker from 37.1.0 to 37.3.0 in /src ([#89](https://github.com/rubenrod18/flask_api/issues/89)) ([647cd8a](https://github.com/rubenrod18/flask_api/commit/647cd8a8a4c120fa86d771b3e861ba8f7807233c))
* **pip:** bump flask from 3.1.0 to 3.1.1 in /src ([#87](https://github.com/rubenrod18/flask_api/issues/87)) ([988e37e](https://github.com/rubenrod18/flask_api/commit/988e37e8dbf57df450d955c350d7c88a5386aff6))
* **pip:** bump flask-security-too from 5.6.1 to 5.6.2 in /src ([#82](https://github.com/rubenrod18/flask_api/issues/82)) ([f4dae5b](https://github.com/rubenrod18/flask_api/commit/f4dae5beb67f705a814c7db7378934fc0dd6d634))
* **pip:** bump freezegun from 1.5.1 to 1.5.2 in /src ([#102](https://github.com/rubenrod18/flask_api/issues/102)) ([2d16a1c](https://github.com/rubenrod18/flask_api/commit/2d16a1c908ac4a6fd2bce6d7398be51a9d195705))
* **pip:** bump pytest from 8.3.5 to 8.4.0 in /src ([#115](https://github.com/rubenrod18/flask_api/issues/115)) ([1ab1276](https://github.com/rubenrod18/flask_api/commit/1ab12765c5d442d3a068d9bff9baa897681f16cb))
* **pip:** bump pytest-xdist from 3.6.1 to 3.7.0 in /src ([#104](https://github.com/rubenrod18/flask_api/issues/104)) ([3ae5d00](https://github.com/rubenrod18/flask_api/commit/3ae5d00c0a72153860f18913edcc6680467125bf))
* **pip:** bump sqlalchemy from 2.0.40 to 2.0.41 in /src ([#88](https://github.com/rubenrod18/flask_api/issues/88)) ([26b7a56](https://github.com/rubenrod18/flask_api/commit/26b7a5682025a63e35776f27b2fd5cc5cd3e3bcc))
* **pip:** bump tornado from 6.4.2 to 6.5 ([#94](https://github.com/rubenrod18/flask_api/issues/94)) ([83dffce](https://github.com/rubenrod18/flask_api/commit/83dffcea13164e2316fd7d89023f18297111ee2c))
* **pre-commit:** add new argument in pylint hook ([add8c3b](https://github.com/rubenrod18/flask_api/commit/add8c3bb42d5637d81f34be97c2f21d81bf93823))
* replace pip-tools to poetry as python dependencies manager ([#109](https://github.com/rubenrod18/flask_api/issues/109)) ([6d4f4d5](https://github.com/rubenrod18/flask_api/commit/6d4f4d556375ee4b7ec648c5c3b6c84b453a86de))


### Features

* **repositories:** add new repository concept ([#83](https://github.com/rubenrod18/flask_api/issues/83)) ([a3886d7](https://github.com/rubenrod18/flask_api/commit/a3886d7ee3b1344909036b6131f9a8418c21129c))


### Bug Fixes

* verify user authentication and permissions before swagger models ([#85](https://github.com/rubenrod18/flask_api/issues/85)) ([9cc798c](https://github.com/rubenrod18/flask_api/commit/9cc798cfff209dbb666b07a89b701cd371af405d))


### Code Refactoring

* **auth-serializers:** change way to get user_repository in auth serializers ([b07ec42](https://github.com/rubenrod18/flask_api/commit/b07ec4288dfe0b75bcf88c1a10cc2c952040fb9c))
* **logging:** move logging config to a python module ([4f4063e](https://github.com/rubenrod18/flask_api/commit/4f4063e014ddd7a059ef53c604afdd15ea493528))
* move file_storage as an app layer component ([#111](https://github.com/rubenrod18/flask_api/issues/111)) ([22c59fd](https://github.com/rubenrod18/flask_api/commit/22c59fd87a716a06de6d8ab52a636c337c0df4a8))
* remove manager classes and migrate to repositories ([#118](https://github.com/rubenrod18/flask_api/issues/118)) ([84dff2a](https://github.com/rubenrod18/flask_api/commit/84dff2a0851452ec835e0036178bad80e82cf3c6))
* rename find method from base_service and base_manager ([#114](https://github.com/rubenrod18/flask_api/issues/114)) ([ea293dc](https://github.com/rubenrod18/flask_api/commit/ea293dce95e18ecaf65a6e6f08c6ee23970c4dd2))
* **serializers:** add ma.auto_field in user and role ([#84](https://github.com/rubenrod18/flask_api/issues/84)) ([55e8073](https://github.com/rubenrod18/flask_api/commit/55e8073059333c46c1802cb509654ed90cd4895a))
* **services:** split base service actions in abstract classes ([7e7838b](https://github.com/rubenrod18/flask_api/commit/7e7838b57b68a209fb89523eecf99c44666e6ada))

## [3.1.0](https://github.com/rubenrod18/flask_api/compare/v3.0.0...v3.1.0) (2025-05-02)


### Build System

* **docker-compose:** rename container and network names ([36c1deb](https://github.com/rubenrod18/flask_api/commit/36c1debdc4b091e1f5a62c11a820c9348d3797d2))
* **make:** update help command to show command descriptions ([#68](https://github.com/rubenrod18/flask_api/issues/68)) ([b9ad04c](https://github.com/rubenrod18/flask_api/commit/b9ad04cc93b9986f9c54ae2239970f89ddb14359))
* **npm:** replace standard-version to commit-and-tag-version package ([#80](https://github.com/rubenrod18/flask_api/issues/80)) ([309817b](https://github.com/rubenrod18/flask_api/commit/309817bc98acd1738982e87b7a4362d6feaa1886))
* **pip:** bump celery from 5.4.0 to 5.5.1 in /src ([#72](https://github.com/rubenrod18/flask_api/issues/72)) ([722ce59](https://github.com/rubenrod18/flask_api/commit/722ce59b8898cdcd39b6685dffff7cf62acb090c))
* **pip:** bump celery from 5.5.1 to 5.5.2 in /src ([#78](https://github.com/rubenrod18/flask_api/issues/78)) ([4f7c4e0](https://github.com/rubenrod18/flask_api/commit/4f7c4e083f23e491ec86d7a65c6ddbe2e5dc2bac))
* **pip:** bump coverage from 7.6.10 to 7.6.12 in /src ([#40](https://github.com/rubenrod18/flask_api/issues/40)) ([0a405f8](https://github.com/rubenrod18/flask_api/commit/0a405f819597750998bb794b5319804062a8c7ab))
* **pip:** bump coverage from 7.6.12 to 7.7.0 in /src ([#57](https://github.com/rubenrod18/flask_api/issues/57)) ([87e2152](https://github.com/rubenrod18/flask_api/commit/87e215295b83a1e5ddb1bf6814ce9a10e63f0cb8))
* **pip:** bump coverage from 7.7.0 to 7.7.1 in /src ([#63](https://github.com/rubenrod18/flask_api/issues/63)) ([b1cee59](https://github.com/rubenrod18/flask_api/commit/b1cee59b44274dce140f323bce9e1dd037432c93))
* **pip:** bump coverage from 7.7.1 to 7.8.0 in /src ([#67](https://github.com/rubenrod18/flask_api/issues/67)) ([ab291f4](https://github.com/rubenrod18/flask_api/commit/ab291f448768618f36793104381f34d1f09b9ab1))
* **pip:** bump dependency-injector from 4.45.0 to 4.46.0 in /src ([#38](https://github.com/rubenrod18/flask_api/issues/38)) ([5dd6a75](https://github.com/rubenrod18/flask_api/commit/5dd6a75d0307cac183826c7ec5898a18164511fb))
* **pip:** bump faker from 35.0.0 to 36.1.1 in /src ([#36](https://github.com/rubenrod18/flask_api/issues/36)) ([67ba2ea](https://github.com/rubenrod18/flask_api/commit/67ba2ea276ec78375116a9ccd195d43e2b0e5fe3))
* **pip:** bump faker from 36.1.1 to 36.2.2 in /src ([#51](https://github.com/rubenrod18/flask_api/issues/51)) ([8f4ef59](https://github.com/rubenrod18/flask_api/commit/8f4ef5964bce73d1850cf152abcf3d45e66f7c0a))
* **pip:** bump faker from 36.2.2 to 37.0.0 in /src ([#54](https://github.com/rubenrod18/flask_api/issues/54)) ([f2b7876](https://github.com/rubenrod18/flask_api/commit/f2b787658b89053258ccc472bb2332175936e8f1))
* **pip:** bump faker from 37.0.0 to 37.0.2 in /src ([#61](https://github.com/rubenrod18/flask_api/issues/61)) ([167de94](https://github.com/rubenrod18/flask_api/commit/167de944669c2ef7f41de59b78c4ac8c3dad4aac))
* **pip:** bump faker from 37.0.2 to 37.1.0 in /src ([#64](https://github.com/rubenrod18/flask_api/issues/64)) ([2e2b5e1](https://github.com/rubenrod18/flask_api/commit/2e2b5e1a5f7d3603fb03882e3a97f90ad0fbe2b8))
* **pip:** bump flask-security-too from 5.5.2 to 5.6.0 in /src ([#43](https://github.com/rubenrod18/flask_api/issues/43)) ([0c3dd34](https://github.com/rubenrod18/flask_api/commit/0c3dd34648b580b689758c70776ed96ebf1e7174))
* **pip:** bump flask-security-too from 5.6.0 to 5.6.1 in /src ([#60](https://github.com/rubenrod18/flask_api/issues/60)) ([ab90ccd](https://github.com/rubenrod18/flask_api/commit/ab90ccdc71ec7085145b863111ec93dc167d699a))
* **pip:** bump jinja2 from 3.1.5 to 3.1.6 in /src ([#52](https://github.com/rubenrod18/flask_api/issues/52)) ([6480e89](https://github.com/rubenrod18/flask_api/commit/6480e8942ed3589d14459dc2f47647f5fea03ada))
* **pip:** bump m2r2 from 0.3.3.post2 to 0.3.4 in /src ([#79](https://github.com/rubenrod18/flask_api/issues/79)) ([637d166](https://github.com/rubenrod18/flask_api/commit/637d166b299145dec4a116299707894bbd42501a))
* **pip:** bump marshmallow-sqlalchemy from 1.4.0 to 1.4.1 in /src ([#42](https://github.com/rubenrod18/flask_api/issues/42)) ([574ce85](https://github.com/rubenrod18/flask_api/commit/574ce85f8ecd40ffbc3d5b5770100474d5bbf4ea))
* **pip:** bump marshmallow-sqlalchemy from 1.4.1 to 1.4.2 in /src ([#73](https://github.com/rubenrod18/flask_api/issues/73)) ([3d17795](https://github.com/rubenrod18/flask_api/commit/3d17795a20853f2209a2ba078868956be3e8965a))
* **pip:** bump pre-commit from 4.1.0 to 4.2.0 in /src ([#59](https://github.com/rubenrod18/flask_api/issues/59)) ([8c9b350](https://github.com/rubenrod18/flask_api/commit/8c9b350da71215f7084fc102188e41fe31f5c26e))
* **pip:** bump pytest from 8.3.4 to 8.3.5 in /src ([#50](https://github.com/rubenrod18/flask_api/issues/50)) ([2fdd9b6](https://github.com/rubenrod18/flask_api/commit/2fdd9b61b9026226f3caf11c62a06b4707cb6999))
* **pip:** bump python-dotenv from 1.0.1 to 1.1.0 in /src ([#65](https://github.com/rubenrod18/flask_api/issues/65)) ([c5837a4](https://github.com/rubenrod18/flask_api/commit/c5837a434ee002fef902ff6d62cd61daec5b966d))
* **pip:** bump sphinx from 8.1.3 to 8.2.1 in /src ([#35](https://github.com/rubenrod18/flask_api/issues/35)) ([9ca9b0a](https://github.com/rubenrod18/flask_api/commit/9ca9b0aa844d8bad13f55fbc26d2b02dd4f1a098))
* **pip:** bump sphinx from 8.2.1 to 8.2.3 in /src ([#49](https://github.com/rubenrod18/flask_api/issues/49)) ([b20b0de](https://github.com/rubenrod18/flask_api/commit/b20b0de180b2d15bd9590c979e06938c2bd1d03e))
* **pip:** bump sqlalchemy from 2.0.37 to 2.0.38 in /src ([#41](https://github.com/rubenrod18/flask_api/issues/41)) ([b809dd6](https://github.com/rubenrod18/flask_api/commit/b809dd61bde0180a4f96bc42663f0b64eb3b5666))
* **pip:** bump sqlalchemy from 2.0.38 to 2.0.39 in /src ([#55](https://github.com/rubenrod18/flask_api/issues/55)) ([0aa0ce7](https://github.com/rubenrod18/flask_api/commit/0aa0ce7356334e6ac05792046d68669e00898668))
* **pip:** bump sqlalchemy from 2.0.39 to 2.0.40 in /src ([#66](https://github.com/rubenrod18/flask_api/issues/66)) ([ec338a3](https://github.com/rubenrod18/flask_api/commit/ec338a340d7da1b10da4af2d709c158e2f07ad64))
* **pip:** bump xlsxwriter from 3.2.1 to 3.2.2 in /src ([#37](https://github.com/rubenrod18/flask_api/issues/37)) ([6a222e5](https://github.com/rubenrod18/flask_api/commit/6a222e5e0398cfbe9930236e1700f2bc671fd764))
* **pip:** bump xlsxwriter from 3.2.2 to 3.2.3 in /src ([#75](https://github.com/rubenrod18/flask_api/issues/75)) ([b52545d](https://github.com/rubenrod18/flask_api/commit/b52545d3dc154d67c6fa99fae611c81dcfd0ca0c))


### Features

* **swagger:** add as_attachment field on /documents/<document_id> endpoint ([#47](https://github.com/rubenrod18/flask_api/issues/47)) ([61303d9](https://github.com/rubenrod18/flask_api/commit/61303d914323b363e0ab8df4693a593ca71178ac))
* **swagger:** add to_pdf field on /users/word_and_xlsx and /users/word endpoints ([#45](https://github.com/rubenrod18/flask_api/issues/45)) ([98aa497](https://github.com/rubenrod18/flask_api/commit/98aa497772528a9908670cc8968ea19633625e99))


### Bug Fixes

* **documents:** as_attachment field didn't work when was sent ([#46](https://github.com/rubenrod18/flask_api/issues/46)) ([9d282f0](https://github.com/rubenrod18/flask_api/commit/9d282f0d0207682d6ccaa6c16b708ef3576cc455))


### Code Refactoring

* **managers:** datetime fields are not required anymore in create method ([#69](https://github.com/rubenrod18/flask_api/issues/69)) ([a23dc0b](https://github.com/rubenrod18/flask_api/commit/a23dc0bd944e31cd657e435cf2abb21a623e24c0))

## [3.0.0](https://github.com/rubenrod18/flask_api/compare/v2.0.6...v3.0.0) (2025-02-27)


### ⚠ BREAKING CHANGES


* **docker:** previous application setup is not compatible.
* **db:** migrate to MySQL database.
* **orm:** migrate to SQLAlchemy.

### Features

* **celery:** add sqlalchemy integration on celery tasks ([5bba41c](https://github.com/rubenrod18/flask_api/commit/5bba41c03e4184b81bdd5526f7b52de90545556f))
* **celery:** define new celery queues to celery tasks ([acde9c1](https://github.com/rubenrod18/flask_api/commit/acde9c123562df010ca98218d0a1fb3801b950a9))
* **cli:** enable custom cli and update seed command ([ed77f5d](https://github.com/rubenrod18/flask_api/commit/ed77f5d7ca1931a739fe2ef0f3397896593d2a80))
* **db:** add script to create database ([048eb51](https://github.com/rubenrod18/flask_api/commit/048eb51334a9c5263ad6506be1afb0d68d05636a))
* **db:** replace mysql-connector-python to mysqlclient package ([9e50c19](https://github.com/rubenrod18/flask_api/commit/9e50c19f898bab455f403ca975d818b2a9d48aef))
* **jwt:** add flask-jwt-extended to manage json web tokens ([0feea80](https://github.com/rubenrod18/flask_api/commit/0feea801b150e268104d82946cee5e97227c74cc))
* **jwt:** add refresh token ([10df8b5](https://github.com/rubenrod18/flask_api/commit/10df8b58dc377309d7cfa59730580fc39d62894e))
* migrate to mysql, sqlalchemy and docker ([#26](https://github.com/rubenrod18/flask_api/issues/26)) ([e29f86e](https://github.com/rubenrod18/flask_api/commit/e29f86e42d643d24d46f1f170b5262cbf38c5961))
* **pre-commit:** add ruff and update config ([c7929be](https://github.com/rubenrod18/flask_api/commit/c7929be38be26fd17476b05626f13deff6d4ab7b))
* **request-query-op:** add sqlalchemy integration ([#31](https://github.com/rubenrod18/flask_api/issues/31)) ([0fc84b6](https://github.com/rubenrod18/flask_api/commit/0fc84b656b94d992ebfb937ae7459bd8d5b7681e))
* **serializers:** add ma.autofield in role and user datetime fields ([272d193](https://github.com/rubenrod18/flask_api/commit/272d1930c8994713981f49251836ab80da7f0640))
* **serializers:** add managermixin to import managers and update some fields ([bf97a20](https://github.com/rubenrod18/flask_api/commit/bf97a20f7a220faad2933f313c5a38db94f6524e))
* **swagger:** override swagger user interface ([2827d5b](https://github.com/rubenrod18/flask_api/commit/2827d5b3d7b693596940d59aaac4e35762b59adb))
* **task-status:** update endpoint to see the celery task statutes ([1c81521](https://github.com/rubenrod18/flask_api/commit/1c8152111b405162ee24c442a11ad3c4deabe7c2))
* **test:** add pytest-xdist python package to run the tests in parallel ([20d5251](https://github.com/rubenrod18/flask_api/commit/20d5251290eb3ad76f915c316065ba761e5c2caa))
* **tests:** add integration to sqlalchemy orm and mysql database ([#27](https://github.com/rubenrod18/flask_api/issues/27)) ([3d2bf7e](https://github.com/rubenrod18/flask_api/commit/3d2bf7eff86d15887e50bc53cb3c348072d4ffe8))
* **users:** send an email when an user is created ([37aebfb](https://github.com/rubenrod18/flask_api/commit/37aebfbca52df368f207f34c3f538b68c9ff6175))


### Code Refactoring

*  move serializers to blueprints ([#32](https://github.com/rubenrod18/flask_api/issues/32)) ([2f9bd41](https://github.com/rubenrod18/flask_api/commit/2f9bd41b98013ec585dafd2667483f09ce4225a1))
* **blueprints:** apply solid design principles ([9129a12](https://github.com/rubenrod18/flask_api/commit/9129a12a13318ee599bec0c782e912de6de2a897))
* **cli:** apply solid design principles ([8b5f574](https://github.com/rubenrod18/flask_api/commit/8b5f574c6222dee4c2e3abcbc37ac317e5e5aa01))
* **di-container:** rename container to ServiceDIContainer ([5d090a8](https://github.com/rubenrod18/flask_api/commit/5d090a80cfe188f362387ad9d243238059f7810d))
* **helpers:** remove helpers package because is not required anymore ([541459a](https://github.com/rubenrod18/flask_api/commit/541459a143360ae67709989ec32515b5d986828d))
* **managers:** apply solid design principles ([edc6fbd](https://github.com/rubenrod18/flask_api/commit/edc6fbd6c224e31a6c7adb83fe381c71ff1635e9))
* **middleware:** apply solid design principles ([1300b79](https://github.com/rubenrod18/flask_api/commit/1300b791d354654e3b3b4ed1d87d06f90ce71f62))
* **request-query-operator:** apply solid design principles ([97dcea2](https://github.com/rubenrod18/flask_api/commit/97dcea29d9624bdadbf2f7b33dfa77164fca9599))
* **request-query-operator:** move query operators to constants ([d9c3b8c](https://github.com/rubenrod18/flask_api/commit/d9c3b8c6a7cfacf802117dfb00b535a3bd24d0d3))
* **request-query-operator:** rename its classes and the module name ([7ee669c](https://github.com/rubenrod18/flask_api/commit/7ee669c955f29233f31ef1411eaef2d140c22d70))
* **resource:** add serializermixin to create several serializers ([e35a97a](https://github.com/rubenrod18/flask_api/commit/e35a97a1c2420a0dcfa66a89a4297e1b40df0094))
* **roles:** unify all role name declarations in role model ([45ac5c9](https://github.com/rubenrod18/flask_api/commit/45ac5c904e58ae605b354c737d6fdf9322fd9b03))
* **seeders:** apply some solid principles and update way to import them in seed command ([341ed74](https://github.com/rubenrod18/flask_api/commit/341ed744be6934ee740c22d1a16b2201806b1793))
* **services:** apply solid design principles ([88d407d](https://github.com/rubenrod18/flask_api/commit/88d407dff06ba3962ca2fd50683653f1e1deaa46))
* **task:** remove task service ([2e3eadb](https://github.com/rubenrod18/flask_api/commit/2e3eadbb7da3a27192a105b82a68fd71ab4b92b3))
* **utils:** add pos_to_char function in excel task ([ff18d9a](https://github.com/rubenrod18/flask_api/commit/ff18d9aa47c79e5ffa741ab73eb587e5bf550459))


### Build System

* **docker-compose:** add mailpit docker image ([b7fe5b7](https://github.com/rubenrod18/flask_api/commit/b7fe5b74ad11fc909b405635f07e58d4de2ac214))
* **docker-compose:** rename mailpit container name ([f84a985](https://github.com/rubenrod18/flask_api/commit/f84a985a2dc2c409558e6ad6d9f3991f6842b798))
* **docker-compose:** update way to build the docker images ([9fdbdcc](https://github.com/rubenrod18/flask_api/commit/9fdbdccc0da3df63f923ca7b24f1068c732d809d))
* **docker:** add Docker integration ([f2035f5](https://github.com/rubenrod18/flask_api/commit/f2035f58ea1454c8ae2b4314b08ff4fe912eb1ca))
* **docker:** add files to init the application ([ddef07c](https://github.com/rubenrod18/flask_api/commit/ddef07c74c78523462faf28b9b84700730158f91))
* **docker:** add libreoffice-writer package ([bbd3834](https://github.com/rubenrod18/flask_api/commit/bbd38341d80ed1a0666b967c4575450605e90905))
* **docker:** update docker to python 3.13 ([#24](https://github.com/rubenrod18/flask_api/issues/24)) ([0641849](https://github.com/rubenrod18/flask_api/commit/0641849df3c2b6067e3594478bfdb4d66e5028b1))
* **docker:** update pythonpath environment var ([7c9d8e6](https://github.com/rubenrod18/flask_api/commit/7c9d8e64a8975cc510bfdc8373a6412dc918d99d))
* **helpers:** create new package and move some modules ([4180481](https://github.com/rubenrod18/flask_api/commit/41804818ef5553cfa1e1f86851b935757596c522))
* **npm:** update node package versions ([#39](https://github.com/rubenrod18/flask_api/issues/39)) ([fad9102](https://github.com/rubenrod18/flask_api/commit/fad910200ca564277c2eb4350e82cbe39f6e79ef))
* **pip:** add new celery config ([3915979](https://github.com/rubenrod18/flask_api/commit/3915979c6d9d189fb3ce2a6cc7d7e0b8b607d3da))
* **pip:** remove peewee package ([e668e37](https://github.com/rubenrod18/flask_api/commit/e668e37941f5b5981bd423614a47db51f6cac637))
* **pip:** update all python packages to latest versions ([#23](https://github.com/rubenrod18/flask_api/issues/23)) ([662b2d2](https://github.com/rubenrod18/flask_api/commit/662b2d2b7bac5766895760602c716adb820c202b))
* **pre-commit:** add git hooks integration ([7d8cb36](https://github.com/rubenrod18/flask_api/commit/7d8cb36e52ace0ce2406dadef5db922ee3dec71f))
* **utils:** move some code specific modules ([e436a6a](https://github.com/rubenrod18/flask_api/commit/e436a6af9a4a1dce822c3047c1461df036f4ff1c))

### [2.0.6](https://github.com/rubenrod18/flask_api/compare/v2.0.5...v2.0.6) (2021-12-28)


### Bug Fixes

* **pip:** upgrade package versions ([75aff3b](https://github.com/rubenrod18/flask_api/commit/75aff3bac8e458b109e4677c40ace78b65057102))

### [2.0.5](https://github.com/rubenrod18/flask_api/compare/v2.0.4...v2.0.5) (2021-12-27)


### Bug Fixes

* **npm:** upgrade package versions ([f62f335](https://github.com/rubenrod18/flask_api/commit/f62f3356f0c7c66c90370678c89394f74442c15f))

## [2.0.4](https://github.com/rubenrod18/flask_api/compare/v2.0.3...v2.0.4) (2021-02-19)


### Bug Fixes

* **users:** add new fs_uniquifier column on users table ([a28be38](https://github.com/rubenrod18/flask_api/commit/a28be38572ba25906aa10e74293040c65dba1fbe))


### Build System

* **npm:** update node package versions ([6314da3](https://github.com/rubenrod18/flask_api/commit/6314da35c80c9994b4ca2f9f99428475f8fb8608))
* **pip:** update flask-security-too version to 4.0.0 ([698acb6](https://github.com/rubenrod18/flask_api/commit/698acb6015579e1f740240edec9350464868adbc))
* **pip:** update python package versions ([09755c8](https://github.com/rubenrod18/flask_api/commit/09755c82f2b01af60bf361c3569c4e8d08567ab1))

## [2.0.3](https://github.com/rubenrod18/flask_api/compare/v2.0.2...v2.0.3) (2021-02-05)


### Bug Fixes

* **celery:** task fields are saving on database when the task is finished ([bc93505](https://github.com/rubenrod18/flask_api/commit/bc935055259b68b54775f1afe5c528d9cf170bf9))


### Code Refactoring

* add new mockups directory in storage directory ([91e642e](https://github.com/rubenrod18/flask_api/commit/91e642e3fc75a7f29c98be12f85af1773f23136c))
* tls and ssl flask mail are getting from environment file ([e548d57](https://github.com/rubenrod18/flask_api/commit/e548d579424ae99257ee4082986929ffc17a325a))

## [2.0.2](https://github.com/rubenrod18/flask_api/compare/v2.0.1...v2.0.2) (2021-01-23)


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
