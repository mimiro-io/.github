
# Common & Reusable GitHub Actions Workflows

![Github Actions](https://avatars.githubusercontent.com/u/44036562?s=200&v=4)

# Reusable WorkFlows

## 1. Docker CI

This workflow uses your Dockerfile and build the image and pushes it to AWS ECR.
If you wish to use this workflow, just create a tiny yaml in your repo (i.e. `.github/workflows/ci.yaml`)and paste below content.

```yaml
name: K8S-CI
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  release:
    types:
      - published
jobs:
  K8S:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    secrets:
      ECR_REPO_POLICY: ${{ secrets.ECR_REPO_POLICY }}
```

### Add a workflow status badge to you repo

Add the following to your repo's README.md (replace `repo-name` with the actual repo name):

```sh
[![CI](https://github.com/mimiro-io/repo-name/actions/workflows/ci.yaml/badge.svg)](https://github.com/mimiro-io/repo-name/actions/workflows/ci.yaml)
```

### Ignore Trivy Scan errors

Its not recommended to ignore trive vulnerability scan, but if its not possible to fix
certain vulnerabilities, then you can skip this check by supplying `trivy_exit_code : 0`. 
This is an optional attribute. By default its always set to `1`. 

Example usage:  

```yaml
jobs:
  DockerBuildPush:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      image: ${{ github.event.repository.name }}  # Name of the Docker Image (without tags and registery name)
      trivy_exit_code : 0
```
