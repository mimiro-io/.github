# Reusable GitHub Actions Workflows
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Docker CI + IRSA](#docker-ci--irsa)
  - [Add a workflow status badge to you repo](#add-a-workflow-status-badge-to-you-repo)
  - [Add a custom IAM policy for your application](#add-a-custom-iam-policy-for-your-application)
    - [Example IAM policy JSON](#example-iam-policy-json)
  - [Ignore Trivy Scan errors](#ignore-trivy-scan-errors)
  - [Set build-time variables (similar to `docker build --build-arg`)](#set-build-time-variables-similar-to-docker-build---build-arg)
  - [Custom name for app and image repository](#custom-name-for-app-and-image-repository)
  - [Skip IRSA creation or Docker (ECR) jobs](#skip-irsa-creation-or-docker-ecr-jobs)
  - [Custom path/file name for IRSA's IAM policy JSON](#custom-pathfile-name-for-irsas-iam-policy-json)
- [Flyway](#flyway)
  - [Add a workflow to run Flyway manually](#add-a-workflow-to-run-flyway-manually)
  - [Add a workflow to run Flyway automatically](#add-a-workflow-to-run-flyway-automatically)
- [Terraform](#terraform)
  - [Input Parameters](#input-parameters)
  - [Example Usage: This workflow can be used in three ways-](#example-usage--this-workflow-can-be-used-in-three-ways-)
    - [1. Use in regular terraform CI. (Automatic apply to non-prod when there is a commit to master/main)](#1-use-in-regular-terraform-ci-automatic-apply-to-non-prod-when-there-is-a-commit-to-mastermain)
    - [2. Use for PR Checks (run terraform `plan` in multiple environment whenever a PR is raised towards master/main)](#2-use-for-pr-checks-run-terraform-plan-in-multiple-environment-whenever-a-pr-is-raised-towards-mastermain)
    - [3. Use for Manual Terraform Operations. (e.g Apply in Prod, Destroy Dev etc.)](#3-use-for-manual-terraform-operations-eg-apply-in-prod-destroy-dev-etc)
- [Docker Hub](#docker-hub)
  - [Custom name for the Docker Hub image repository](#custom-name-for-the-docker-hub-image-repository)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Docker CI + IRSA

This workflow uses your Dockerfile to build a Docker image and push it to AWS ECR.
It also configures [IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

If you wish to use this workflow, just create a tiny yaml file in your repo named `.github/workflows/ci.yaml` and paste below content.

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
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    secrets:
      ECR_REPO_POLICY: ${{ secrets.ECR_REPO_POLICY }}
```

### Add a workflow status badge to you repo

Add the following to your repo's README.md (replace `repo-name` with the actual repo name):

```sh
[![CI](https://github.com/mimiro-io/repo-name/actions/workflows/ci.yaml/badge.svg)](https://github.com/mimiro-io/repo-name/actions/workflows/ci.yaml)
```

### Add a custom IAM policy for your application

If your app/service needs access to any AWS Service, for example S3, SSM Parameter store, create a `./ci/policies.json` file with the neccessary permissions.

https://awspolicygen.s3.amazonaws.com/policygen.html can be used to create IAM polices.

> Make sure to never mention account number in policies stored in GitHub. Just use a `${AWS_ACCOUNT_ID}` variable instead. This CI workflow will populate it for you while deploying.

#### Example IAM policy JSON

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:PutParameter",
                "ssm:GetParametersByPath",
                "ssm:GetParameters",
                "ssm:GetParameter",
                "ssm:DeleteParameters"
            ],
            "Resource": [
                "arn:aws:ssm:eu-west-1:${AWS_ACCOUNT_ID}:parameter/application/app-name/*",
                "arn:aws:ssm:eu-west-1:${AWS_ACCOUNT_ID}:parameter/application/shared/*",
                "arn:aws:ssm:eu-west-1:${AWS_ACCOUNT_ID}:parameter/shared/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-s3-bucket",
                "arn:aws:s3:::my-s3-bucket/*"
            ]
        }
    ]
}

```

### Ignore Trivy Scan errors

Its not recommended to ignore trive vulnerability scan, but if its not possible to fix
certain vulnerabilities, then you can skip this check by supplying `trivy_exit_code: 0`.
This is an optional attribute. By default its always set to `1`.

Example usage:

```yaml
jobs:
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      trivy_exit_code: 0
```

### Set build-time variables (similar to `docker build --build-arg`)

If you wish you can set docker build time variables by supplying a
list of key value pairs to `docker_build_args:`.

if your Dockerfile is using `ARG` then you can overwrite the default values of ARG with this option.
for example -

```Dockerfile
FROM busybox
ARG KEY1
RUN echo "Hei! $KEY1"
ARG KEY2
RUN echo "Hei! $KEY2"
```

```yaml
jobs:
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      docker_build_args: |
        KEY1=VAL1
        KEY2=VAL2
```

### Custom name for app and image repository

By default, your github repo name is used everywhere for naming resources.

However, if you wish to have a custom name for your project then you can override this by using `name` parameter.

Example usage:

```yaml
jobs:
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      name: "my-app"
```

### Custom namespace for app in kubernetes cluster

By default, all apps will be deployed to default namespace `mimiro`.

However, if you wish to have a custom namespace for your app then you can override this by using `k8s_namespace` parameter.

Example usage:

```yaml
jobs:
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      k8s_namespace: "my-namespace"
```

### Skip IRSA creation or Docker (ECR) jobs

By default all the jobs in this workflow are executed. In case you wish to skip any or all of the jobs, it can be done by providing `true` to `skip_irsa` and/or `skip_docker` when calling to this common workflow.

Example usage:

```yaml
jobs:
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      skip_docker: true
```

### Custom path/file name for IRSA's IAM policy JSON

By default,IAM Policy Json file is referred from ci/policies.json. It possible to provide custom path/file name by using the `iam_policies_json_file`. Pls provide the absoulte path of this file from the root of your git repository.

Example usage:

```yaml
jobs:
  AWS:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      iam_policies_json_file: iam/json/my-iam.json
```

## Flyway

This workflow runs Flyway migrations if your app/service is configured with that.

For this to work, your repository needs the following Flyway directory structure and configuration file:

```sh
.
├── migration
│   ├── conf
│   │   └── flyway.conf
│   └── sql
│       ├──V1_001__create_tables_and_indexes.sql
|       └──...
```

The database proctocol and name is taken automatically from the `flyway.conf` file, so make sure to use the same name both locally and in the different environments.

### Add a workflow to run Flyway manually

This workflow lets you manually choose environment and if Flyway should `validate` or `migrate`.

Create a `.github/workflows/flyway.yaml` file and paste the below content.
Make sure that the branch name is correct and update the values of `ssm_db_host`, `ssm_db_user`, `ssm_db_pass` to match the actual paths used in AWS SSM Parameter Store.

```yaml
name: Flyway
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        description: Environment
        options:
        - dev
        - prod
      command:
        type: choice
        description: Flyway command
        options:
        - validate
        - migrate
  pull_request:
    branches: [ master ]

jobs:
  Flyway:
    uses: mimiro-io/.github/.github/workflows/flyway.yaml@main
    with:
      environment: ${{ github.event.inputs.environment }}
      command: ${{ github.event.inputs.command }}
      ssm_db_host: /ssm/parameter/path/host
      ssm_db_user: /ssm/parameter/path/user
      ssm_db_pass: /ssm/parameter/path/pass
```

### Add a workflow to run Flyway automatically

This workflow runs automatically, and in the example below *before* the [Docker CI + IRSA](#docker-ci--irsa) workflow.

- Creating a Pull Request against master runs `flyway validate` in the dev environment
- Pushing to master runs `flyway migrate` in the dev environment
- Creating a GitHub release runs `flyway migrate` in the prod environment

Create a `.github/workflows/ci.yaml` file and paste the below content.
Make sure that the branch name is correct and update the values of `ssm_db_host`, `ssm_db_user`, `ssm_db_pass` to match the actual paths used in AWS SSM Parameter Store.

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
  Flyway:
    uses: mimiro-io/.github/.github/workflows/flyway.yaml@main
    with:
      environment: ${{ github.event_name == 'release' && 'prod' || 'dev' }}
      command: ${{ github.event_name == 'pull_request' && 'validate' || 'migrate' }}
      ssm_db_host: /ssm/parameter/path/host
      ssm_db_user: /ssm/parameter/path/user
      ssm_db_pass: /ssm/parameter/path/pass
  AWS:
    needs: Flyway
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    secrets:
      ECR_REPO_POLICY: ${{ secrets.ECR_REPO_POLICY }}
```

## Terraform

Reusable workflow for your terraform configuration. Can be used to perform common terraform operations.

### Input Parameters

Any or all of the below input parameters can be used by using `with:`.

[find example usage here](#example-usage--this-workflow-can-be-used-in-three-ways-)

```yaml
    inputs:
      command:
        description: "Terraform command (Default is plan)"
        required: false
        type: string
        default: 'plan'
      environment:
        description: "Environment name (Default is dev)"
        required: false
        type: string
        default: 'dev'
      name:
        description: "Infra Name (Default is the github repo name)"
        required: false
        type: string
        default: ${{ github.event.repository.name }}
      aws_region:
        description: "AWS Region Name (Default is eu-west-1)"
        required: false
        type: string
        default: 'eu-west-1'
      terraform_version:
        description: "Terraform CLI Version (Default 1.1.3)"
        required: false
        type: string
        default: '1.1.3'
      terraform_working_dir:
        description: "Terraform dir path in repo. (Default is ./terraform)"
        required: false
        type: string
        default: './terraform'
      terraform_backend_bucket:
        description: "Terraform remote backend S3 bucket name to store the terraform state"
        required: true
        type: string
      terraform_backend_dynamodb:
        description: "Terraform remote backend dynamodbTable name to acquire state lock"
        required: true
        type: string

```

### Example Usage: This workflow can be used in three ways-

#### 1. Use in regular terraform CI. (Automatic apply to non-prod when there is a commit to master/main)

Create a `.github/workflows/terraform-ci.yaml` file and paste the below content.

```yaml
---
# CI - Continuous Integration
# Terraform auto apply in dev when push to master
name: terraform-CI
on:
 push:
   branches: [ master ]

jobs:
  terraform:
    uses: mimiro-io/.github/.github/workflows/terraform.yaml@main
    with:
      environment: dev
      command: apply
      terraform_backend_bucket: S3 bucket name to store the terraform state
      terraform_backend_dynamodb: dynamoDB table name for state locking
```

#### 2. Use for PR Checks (run terraform `plan` in multiple environment whenever a PR is raised towards master/main)

Create a `.github/workflows/terraform-pr.yaml` file and paste the below content.

```yaml
---
# PR - Pull Request checks
# Terraform plan for dev and prod, when PR is raised to master
name: terraform-PR
on:
 pull_request:
   branches: [ master ]

jobs:

  terraform-dev:
    uses: mimiro-io/.github/.github/workflows/terraform.yaml@main
    with:
      environment: dev
      command: plan
      terraform_backend_bucket: S3 bucket name to store the terraform state
      terraform_backend_dynamodb: dynamoDB table name for state locking

  terraform-prod:
    uses: mimiro-io/.github/.github/workflows/terraform.yaml@main
    with:
      environment: prod
      command: plan
      terraform_backend_bucket: S3 bucket name to store the terraform state
      terraform_backend_dynamodb: dynamoDB table name for state locking

```

#### 3. Use for Manual Terraform Operations. (e.g Apply in Prod, Destroy Dev etc.)

Create a `.github/workflows/terraform-wd.yaml` file and paste the below content.

```yaml
---
# WD - workflow_dispatch.  Manual trigger of terraform commands.
# Run various terraform commands in any of the dev/prod environment. (eg. apply in prod)
name: terraform-WD
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        description: Environment
        options:
          - dev
          - prod
      command:
        type: choice
        description: terraform command to be executed
        options:
          - plan
          - apply
          - destroy-plan
          - destroy


jobs:
  terraform:
    uses: mimiro-io/.github/.github/workflows/terraform.yaml@main
    with:
      environment: ${{ github.event.inputs.environment }}
      command: ${{ github.event.inputs.command }}
      terraform_backend_bucket: S3 bucket name to store the terraform state
      terraform_backend_dynamodb: dynamoDB table name for state locking

```

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
