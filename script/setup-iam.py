import json
import boto3
import os
from botocore.exceptions import ClientError

#IRSA = IAM Role for Service Account
def get_eks_oidc():
    try:
        response = eks_client.list_clusters(maxResults=1)
        no_of_clusters = len(response['clusters'])
        if no_of_clusters != 1:
            print ('Script supports only if there is only one eks cluster. Expected : 1 Got:', no_of_clusters)
            print ('Not able to create/update IRSA. Pls try again.')
            exit(1)
        response = eks_client.describe_cluster(name=(response['clusters'])[0])
        cluster_details=(response['cluster'])
        oidc_issuer=((cluster_details["identity"])["oidc"])["issuer"]
        return oidc_issuer.replace("https://","") 
    except ClientError as error:
            return 'Unexpected error occurred while fetching cluster details', error

def get_assume_role_policy():
    oidc_issuer_url=get_eks_oidc()
    trust_relationship_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::"+account_id+":oidc-provider/"+oidc_issuer_url
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                ""+oidc_issuer_url+":sub": "system:serviceaccount:mimiro:mimiro-web-auth",
                ""+oidc_issuer_url+":aud": "sts.amazonaws.com"
                }
            }
            }
        ]
    }
    return json.dumps(trust_relationship_policy)
role_name = "mimiro-k8s-"+os.environ.get('APP')+"-role" #TODO- Get prefix from eks cluster name
print('IRSA:',role_name, ': Setting up IAM Roles & Policy for the service account')
iam_client = boto3.client('iam')
eks_client = boto3.client('eks')
sts_client = boto3.client('sts')
account_id = sts_client.get_caller_identity().get('Account')
assume_role_policy=get_assume_role_policy()

try:
    response = iam_client.get_role(RoleName=role_name)
    print ('IRSA:',role_name,': Role exists! updating existing role and policy')
    try:
        response = iam_client.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=assume_role_policy
        )
    except ClientError as error:
        print('IRSA:',role_name, ': Unexpected error occurred... Role could not be updated', error)
        exit(1)
    print('IRSA:',role_name, ': Role successfully updated')
except ClientError as error:
    if error.response['Error']['Code'] == 'NoSuchEntity':
        print ('IRSA:',role_name,': Role does not exist.Creating new role and policy')
        try:
            create_role_res = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=get_assume_role_policy(),
            Description=role_name,
            Tags=[
                {
                    'Key': 'CreatedBy',
                    'Value': 'ReusableGithubActions'
                }
            ]
        )
        except ClientError as error:
            print('IRSA:',role_name, ': Unexpected error occurred... Role could not be created', error)
            exit(1)
        print('IRSA:',role_name, ': Role Successfully Created')

