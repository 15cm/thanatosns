# Thanatosns
An SNS data management system.

[![Build Status](https://drone.15cm.net/api/badges/15cm/thanatosns/status.svg)](https://drone.15cm.net/15cm/thanatosns)

## Features
* Simple CMS of SNS posts.
* Export SNS medias to files, with EXIF metadata from the SNS posts attached.

All interactions with the system are supposed to made through REST APIs or Django Admin. Interfaces:
* <web_host>/api/docs => Swagger UI
* <web_host>/admin => Django Admin UI
* <flower_host> => Flower UI to monitor Celery tasks (for exporting tasks)

## Use Cases

![Use case 1](./docs/use-case-1.svg)
