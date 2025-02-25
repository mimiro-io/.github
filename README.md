# Docker Hub

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

## Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `name` | Custom Docker Hub repository name | GitHub repo name | No |
| `platforms` | Comma-separated list of platforms | `linux/amd64,linux/arm64` | No |

### Example with Custom Inputs

```yaml
jobs:
  DockerHub:
    uses: mimiro-io/.github/.github/workflows/dockerhub.yaml@main
    with:
      name: "some-other-name"
      platforms: "linux/amd64"
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```