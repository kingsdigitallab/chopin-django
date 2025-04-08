# Chopin Online

Repository for the [Chopin Online portal](http://www.chopinonline.ac.uk/).

## Overview

Chopin Online comprises three major resources dedicated to the music of Fryderyk Chopin and developed over two decades by John Rink, Christophe Grabowski and other experts working in collaboration with leading libraries and private collectors from around the world. The projects were developed first at the [Department of Digital Humanities](https://www.kcl.ac.uk/ddh) and then [King's Digital Lab](https://kdl.kcl.ac.uk/,) led by Elliott Hall, Miguel Vieira, and Ginestra Ferraro. For full details, see the [participants](https://chopinonline.ac.uk/ocve/about/participants/) section of the Chopin online website.

## Technology

1. Django 3.2.5
2. Javascript: JQuery for the UI.  OpenLayers and Openseadragon are used to display the manuscript images, and the bar level annotations in OCVE.
3. Postgres 9.6
4. django-haystack 3.1.1
5. Elasticsearch 7.1.

## Containers:

- [nginx-proxy](https://hub.docker.com/r/nginxproxy/nginx-proxy): This is the primary entry point for the stack, running on 80. It automatically builds a proxy to other containers.
- [django 3.2](https://hub.docker.com/layers/library/python/3.6-slim-buster/images/sha256-5dd134d6d97c67dd02e4642ab24ecbb9d23059ea018a8b5185784d29dce2f37a?context=explore): The main container for the project (see more detailed description below.)
- [nginx](https://hub.docker.com/_/nginx): This is the static data container, serving Django's static content.
- db: The database container for Django above, running a legacy version of Postgres (9.6).
- elasticsearch [7.10](https://hub.docker.com/_/elasticsearch): The indexing container, used by Haystack 3.2.1. (Pre-migration, Haystack 2 was using Solr 6.)

## ENV file

The compose file will look for deployment variables in a compose/.env file. Below is a sample file:

```
# Django
# ------------------------------------------------------------------------------
DJANGO_READ_DOT_ENV_FILE=True
DJANGO_ALLOWED_HOSTS = www.chopinonline.ac.uk, chopinonline.ac.uk,localhost,127.0.0.1
DJANGO_SECRET_KEY = ''




# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DATABASE=app_ocve4_liv
POSTGRES_USER=
POSTGRES_PASSWORD=

# Elasticsearch
# ------------------------------------------------------------------------------
discovery.type=single-node

```

Fill in the database credentials and Django variables. If deploying via a CI pipeline such as Gitlab, this file will need to be included in its variables (in the KDL setup, we encode this in base64 and add it to the CI/CD variables in the repository settings.)

## Getting started

1. Enter the project directory: `cd chopin-django`
2. Build and run the docker containers `docker compose -f compose/docker-compose.yml up -d --build`
3. Copy sql data into the db container and ingest it via the command line if necessary.
4. **Haystack indexes are not buit during the build process**. To build the Haystack search indexes, first log into the django container
   `docker compose -f compose/docker-compose.yml exec django bash`. Then run the update_index management command: `python manage.py update_index`



