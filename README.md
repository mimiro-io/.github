
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

### example policy

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
                "secretsmanager:GetSecretValue",
                "ssm:GetParametersByPath",
                "ssm:GetParameters",
                "ssm:GetParameter",
                "ssm:DeleteParameters"
            ],
            "Resource": [
                "arn:aws:ssm:eu-west-1:${AWS_ACCOUNT_ID}:parameter/shared/*",
                "arn:aws:ssm:eu-west-1:${AWS_ACCOUNT_ID}:parameter/application/my-app/*",
                "arn:aws:secretsmanager:eu-west-1:${AWS_ACCOUNT_ID}:secret:/application/my-app/db-user",
                "arn:aws:secretsmanager:eu-west-1:${AWS_ACCOUNT_ID}:secret:/application/my-app/dbpass"
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
      image: ${{ github.event.repository.name }}  # Name of the Docker Image (without tags and registery name)
      trivy_exit_code : 0
```
