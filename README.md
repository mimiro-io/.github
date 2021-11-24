
# Common & Reusable GitHub Actions Workflows

![Github Actions](https://avatars.githubusercontent.com/u/44036562?s=200&v=4)

# Reusable WorkFlows

## 1. Docker CI

This workflow uses your Dockerfile and build the image and pushes it to AWS ECR.
Also configures ![IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

If you wish to use this workflow, just create a tiny yaml file in your repo (i.e. `.github/workflows/ci.yaml`)and paste below content.

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

### Add a custom IAM policy to your application

If your app/service needs access to any AWS Service, for example S3, SSM Parameter store, just have all your permissions in `./ci/policies.json` file.

https://awspolicygen.s3.amazonaws.com/policygen.html can be used to create IAM polices.

> Make sure, never mention account number in policies stored in GitHub. Just use `${AWS_ACCOUNT_ID}` variable. This CI workflow will populate it for you while deploying. 

### example IAM policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-s3-bucket",
                "arn:aws:s3:::my-s3-bucket/*"
            ]
        },
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
        }
    ]
}

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
      trivy_exit_code : 0
```

### Custom Name for App & Image Repository

By default, your github repo name is used everywhere for naming resources.  

However, if you wish to have a custom name for your project then you can override this by using `name` parameter.

Example usage:  

```yaml
jobs:
  DockerBuildPush:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      name : "my-app"
```

### Skip IRSA or Docker ECR

By default all the jobs in this workflow are executed. In case you wish to skip any or all of the jobs, it can be done by providing `true` to `skip_irsa` and/or `skip_ecr` when calling to this common workflow.

Example usage:  

```yaml
jobs:
  DockerBuildPush:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      skip_ecr : true
```

### Custom Path/File name for IRSA's IAM Policy Json

By default,IAM Policy Json file is reffered from ci/policies.json. It possible to provide custom path/file name by using the `iam_policies_json_file`. Pls provide the absoulte path of this file from the root of your git repository.

Example usage:  

```yaml
jobs:
  DockerBuildPush:
    uses: mimiro-io/.github/.github/workflows/docker.yaml@main
    with:
      iam_policies_json_file : iam/json/my-iam.json
```
