# dbt Cloud Webhooks - Datadog

## Overview

This repo contains code to send data retreived from dbt Cloud's [Metadata API](https://docs.getdbt.com/docs/dbt-cloud-apis/metadata-api) and submit it as logs to datadog after receiving a webhook from dbt Cloud indicating run completion.  

## Requirements

Python 3.7+

- [datadog-api-client](https://github.com/DataDog/datadog-api-client-python) - Python API client for the [Datadog API](Datadog API)
- [dbtc](https://dbtc.dpguthrie.com) - Unofficial python interface to dbt Cloud APIs
- [FastAPI](https://fastapi.tiangolo.com) - Modern, fast, web framework for building APIs with Python 3.7+
- [uvicorn](https://uvicorn.org) - ASGI web server implementation for Python 

## Getting Started

Clone this repo

```bash
git clone https://github.com/dpguthrie/dbt-cloud-webhooks-datadog.git
```

## Deploy on fly.io (Optional)

[fly.io](https://fly.io) is a platform for running full stack apps and databases close to your users.

### Install

Directions to install [here](https://fly.io/docs/hands-on/install-flyctl/)

Once installed, sign up for fly.io

```bash
flyctl auth signup
```

Now sign in

```bash
flyctl auth login
```

Launch your app!

```bash
flyctl launch
```

### Secrets

The following secrets need to be configured to your runtime environment for your application to work properly.

- `DBT_CLOUD_AUTH_TOKEN` - This is the secret key that's shown after initailly creating your webhook subscription in dbt Cloud
- `DBT_CLOUD_SERVICE_TOKEN` - Generate a [service token](https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens#generating-service-account-tokens) in dbt Cloud.  Ensure that it has at least the `Metadata Only` permission as we will be making requests against the Metadata API.
- `DD_API_KEY` - [Datadog API Key](https://docs.datadoghq.com/account_management/api-app-keys/)
- `DD_SITE` - This is the datadog site (e.g. `datadoghq.com`)

To set a secret in your fly.io app, do the following:

```bash
flyctl secrets set DBT_CLOUD_AUTH_TOKEN=***
```

Or set them all at once:

```bash
flyctl secrets set DBT_CLOUD_AUTH_TOKEN=*** DBT_CLOUD_SERVICE_TOKEN=*** DD_API_KEY=*** DD_SITE=***
```

### Other Helpful Commands

Check the secrets set in your app

```bash
flyctl secrets list
```

Monitor your app

```bash
flyctl monitor
```

Open browser to currently deployed app

```bash
flyctl open
```

## Other Deploy Options

- [AWS Lambda Example](https://adem.sh/blog/tutorial-fastapi-aws-lambda-serverless)
- [Google Cloud Run Example](https://github.com/sekR4/FastAPI-on-Google-Cloud-Run)
