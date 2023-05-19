# Reusable GitHub Actions Workflows
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Docker Hub](#docker-hub)
  - [Custom name for the Docker Hub image repository](#custom-name-for-the-docker-hub-image-repository)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Docker Hub

This workflow uses your Dockerfile to build and push a Docker image to Docker Hub.

To use this workflow, create a yaml file in your repo named `.github/workflows/ci.yaml` and paste the below content.

```yaml
name: CI
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  release:
    types:
      - published
jobs:
  DockerHub:
    uses: mimiro-io/.github/.github/workflows/dockerhub.yaml@main
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

### Custom name for the Docker Hub image repository

By default, the GitHub repo name is used as the Docker Hub repository name.

If you wish to use a custom name for the repository then you can override this by using the `name` parameter.

Example usage:

```yaml
jobs:
  DockerHub:
    uses: mimiro-io/.github/.github/workflows/dockerhub.yaml@main
    with:
      name: "some-other-name"
```
