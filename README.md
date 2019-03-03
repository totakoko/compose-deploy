# Compose Deploy

> Compose Deploy helps you deploy a [Docker Compose](https://docs.docker.com/compose/overview/)-based infrastructure.

Take a look at [totakoko-infrastructure](https://github.com/totakoko/totakoko-infrastructure) to see a running example.


## Features

- Public infrastructure: help the community learn how you deploy and handle your infrastructure
- Declarative infrastructure: Compose Deploy leverages the declarative nature of Docker Compose files
- Easy integration: easy to integrate in your CI system using the Docker image
- Security: sensitive data can be passed throught environment variables defined in your CI system and don't have to be committed to the repository
- Custom module deployments using ansible tasks
- Deployment diffs: services will be automatically recreated when the configuration inside a module changes (docker-compose.yml, config file, etc). Modules that are not updated won't have their services restarted


## Getting started

### Infrastructure Overview

Compose Deploy can deploy as many docker-compose files as you want.
The layout of your infrastructure repository should be as follows.

```sh
└── module1 # root of the Compose project module1
    ├── docker-compose.yml # classic docker-compose file (required)
    ├── pre.yml # contains module-specific ansible tasks (optional)
    └── ...
...
```

### Requirements

- You must possess a *Debian 9* server (e.g. a dedicated server from [Online](https://www.online.net) or [OVH](https://www.ovh.com)).
- You must access your server using the *root* account by SSH with private key authentication


### Installation Steps

- Create a git repository based on the [base infrastructure project](https://github.com/totakoko/base-compose-deploy-infrastructure)
- Change the configuration according to your needs, add new modules
- [Configure your CI system](#ci-setup)

Take a look at [totakoko-infrastructure](https://github.com/totakoko/totakoko-infrastructure) for a running example.


### CI Setup

Although you could deploy your infrastructure directly from your computer, it's recommended that you execute deployments from a [CI](https://en.wikipedia.org/wiki/Continuous_integration) environment.
Depending on your CI system, you will have to execute the following command for push events:

```sh
docker run -it --rm \
  -v "$PWD:/modules:ro" \
  -e SSH_HOST=... \
  -e SSH_FINGERPRINT=... \
  -e SSH_PRIVATE_KEY=... \
  totakoko/compose-deploy
```

And you have to add the following environment variables:
- SSH_FINGERPRINT: can be retrieved by running `ssh-keyscan -H <server>`
- SSH_PRIVATE_KEY_BASE64: can be retrieved by running `cat ~/.ssh/<your_private_key>`

You can also encode the values using base64 into *SSH_FINGERPRINT_BASE64* and *SSH_PRIVATE_KEY_BASE64*.
Do so by adding `| base64` after the command.


#### GitLab

- Add the environment variables in Settings > CI / CD > Variables.
- Add the following job into your `.gitlab-ci.yml`:

```yaml
deploy:
  stage: deploy
  image:
    name: totakoko/compose-deploy
    entrypoint: ['']
  script:
    - MODULES_ROOT=$PWD compose-deploy deploy
  only:
    - master
```


#### CircleCI

- Because CircleCI can't deal with [multi-line environment variables](https://circleci.com/docs/2.0/env-vars/#encoding-multi-line-environment-variables), you will have to encode your SSH private key the the server fingerprint in base64.
This will probably be an issue for SSH_PRIVATE_KEY and maybe SSH_FINGERPRINT.
For these variables, encode them into base64 and add the *_BASE64* suffix in the environment variable name.
```sh
SSH_PRIVATE_KEY_BASE64=(cat <private_key> | base64)
SSH_FINGERPRINT_BASE64=(ssh-keyscan -H <host> | base64)
```

- Add the environment variables in Settings > Environment Variables.
- Add the following job into your `.circleci/config.yml`:
```yaml
version: 2

jobs:
  deploy:
    docker:
      - image: totakoko/compose-deploy
    steps:
      - checkout
      - run:
          command: compose-deploy deploy
          environment:
            MODULES_ROOT: /root/project

workflows:
  version: 2
  commit:
    jobs:
      - deploy:
          requires: []
          filters:
            branches:
              only:
                - master
```


## Daily usage

### Handling secret variables

Say you want to configure an API key for one of your services.
That API key should not be publicly visible so it can't be part of the `docker-compose.yml`.

Luckily, Compose Deploy contains a useful script that will map some well-crafted environment variables to the filesystem, which can then be read by Docker Compose.
The pattern is `cd_<path>_<with>_<file>__<env_variable>`.
Note the double underscore to separate the path from the variable name.

There are several strategies for passing environment variables to your services.

#### Using <module>.env

`cd_yourmodule_api.env__API_KEY=abc123`: will put `API_KEY=abc123` in `yourmodule/api.env` which can be read afterwards provided you add `env_file: api.env` to your service called `api`.

```yaml
services:
  api:
    ...
    env_file: api.env
    ...
```

#### Using .env

`cd_yourmodule_.env__API_KEY=abc123`: will put `API_KEY=abc123` in `yourmodule/.env`. This file is [automatically sourced by Compose](https://docs.docker.com/compose/environment-variables/#the-env-file), but you must explicitly add each variable to the services using it.

```yaml
services:
  api:
    ...
    environment:
      ...
      - API_KEY
    ...
```


### Updating images

After your infrastructure is deployed, you will presumably want to update the images on a regular basis.
Compose Deploy contains a command to help your with that task.

The `update-module` command will pull, stop and "up" the images of a module:

```sh
compose-deploy update-module <module>`
```

You can update a subset of services:

```sh
compose-deploy update-module <module> <services>...`
```

**Note that there is currently no checks for the container health.**


### One-off commands

Often, you will need to execute commands on the server.
While you can do so via SSH, Compose Deploy provides a way to execute a command on the server.

e.g.:
```sh
compose-deploy exec 'cat /srv/data/traefik/acme.json'
compose-deploy exec 'apt update; apt list --upgradable'
```


## Development

See the [development guide](./DEVELOPMENT.md).


## Roadmap

- Provide a way to backup and restore containers data [restic](https://github.com/restic/restic)


## Rationale

As a developer, I have managed services on a private server for several years and I have come to the following conclusions:
- Bare metal servers are cheap
- Docker and containers made it super easy to package applications into platform-agnostic images
- Docker and Docker Hub made it super easy to distribute applications
- Docker Compose configuration files are an effective way to view all your services at a glance
- Kubernetes is overkill (although really nice with [helm](https://github.com/helm/helm)) for simple projects or for managing a single server
- Most services can afford a downtime of several minutes per day

These conclusions led me to deploy Compose-based services on my server.
At first, the synchronization was manual using rsync and restarting the services was done manually with SSH.

Using Docker offers several advantages:
- Putting services and their dependencies inside Docker containers keeps your server clean
- Docker containers are easy to update (provided they are well designed)
- Host server updates are minimal as there are only a few dependencies, mainly the Docker engine
- Mapping data volumes into /srv/data allows to backup the data effortlessly

This project is the evolution of my rsync + ssh workflow.


## License

[MIT](./LICENSE)
