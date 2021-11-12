import json
import boto3
import os
from botocore.exceptions import ClientError

#IRSA = IAM Role for Service Account
def get_eks_oidc():
    eks_client = boto3.client('eks')
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

def get_assume_role_policy(account_id,app_name,k8s_namespace):
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
                ""+oidc_issuer_url+":sub": "system:serviceaccount:"+k8s_namespace+":"+app_name+"",
                ""+oidc_issuer_url+":aud": "sts.amazonaws.com"
                }
            }
            }
        ]
    }
    return json.dumps(trust_relationship_policy)

def main():
    if 'APP' not in os.environ:
        print ("Error! Could not fetch `APP` environment variable, exiting.. ")
        exit(1)
    else:
        app_name = os.environ.get('APP')

    role_name = "mimiro-k8s-"+app_name+"-role" ## TODO- Get prefix from eks cluster name
    k8s_namespace = 'mimiro' #TODO remove hardcoding

    account_id = boto3.client('sts').get_caller_identity().get('Account')
    
    print('IRSA:',role_name, ':Setup IAM Role & Policy for the k8s service account.',
        'AWS Account :',account_id)
    iam_client = boto3.client('iam')
    assume_role_policy=get_assume_role_policy(account_id,app_name,k8s_namespace)

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
                AssumeRolePolicyDocument=assume_role_policy,
                Description=role_name,
                #TODO Add more tags
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

if __name__ == '__main__':
    main()