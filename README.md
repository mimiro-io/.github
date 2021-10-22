
# Common & Reusable GitHub Actions Workflows

![Github Actions](https://avatars.githubusercontent.com/u/44036562?s=200&v=4)

# Reusable WorkFlows:

## 1. Docker CI

This workflow uses your Dockerfile and build the image and pushes it to AWS ECR.
If you wish to use this workflow, just create a tiny yaml in your repo (i.e. `.github/workflows/ci.yaml`)and paste below content.
```
name: Docker CI

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  release:
    types:
      - published

jobs:
  DockerBuildPush:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      image: ${{ github.event.repository.name }}  # Name of the Docker Image (without tags and registery name)
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY_ID_WITH_ECR_PUSH_PERMISSION }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_KEY_SECRET_WITH_ECR_PUSH_PERMISSION }}

```