import json, boto3
from botocore.exceptions import ClientError

#IRSA = IAM Role for Service Account
def get_eks_oidc():
    eks_client = boto3.client('eks')
    response = eks_client.list_clusters(maxResults=1)
    response = eks_client.describe_cluster(name=(response['clusters'])[0])
    cluster_details=(response['cluster'])
    oidc_issuer=((cluster_details["identity"])["oidc"])["issuer"]
    print(oidc_issuer)
    # #print(response.clusters)
    # response = eks_client.describe_cluster(
    #     name='mimiro-k8s'
    # )   
    # print(response['cluster'])

    # for i in response['cluster']:
    #     print(i.name)

    # #print (response.keys)
    # #return "OK"
    #client = boto3.client('ecs')
    #response = client.list_services(cluster="Fargate",maxResults=100)
    #print(response)
    #servicearns = (response['serviceArns'])
    #print(servicearns)

def create_role():
    iam_client = boto3.client('iam')
    role_name = "k8s-temp-tbd"
    account_id = "313146451641"
    trust_relationship_policy_another_aws_service = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    #Following trust relationship policy can be used to provide access to assume this by third party using external id
    try:
        create_role_res = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship_policy_another_aws_service),
            Description='This is a test role',
            Tags=[
                {
                    'Key': 'Owner',
                    'Value': 'ops'
                }
            ]
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            return 'Role already exists... hence exiting from here'
        else:
            return 'Unexpected error occurred... Role could not be created', error

    policy_json = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "ec2:*"
            ],
            "Resource": "*"
        }]
    }

    policy_name = role_name + '_policy'
    policy_arn = ''

    try:
        policy_res = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_json)
        )
        policy_arn = policy_res['Policy']['Arn']
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            print('Policy already exists... hence using the same policy')
            policy_arn = 'arn:aws:iam::' + account_id + ':policy/' + policy_name
        else:
            print('Unexpected error occurred... hence cleaning up', error)
            iam_client.delete_role(
                RoleName= role_name
            )
            return 'Role could not be created...', error

    try:
        policy_attach_res = iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
    except ClientError as error:
        print('Unexpected error occurred... hence cleaning up')
        iam_client.delete_role(
            RoleName= role_name
        )
        return 'Role could not be created...', error

    return 'Role {0} successfully got created'.format(role_name)

response = get_eks_oidc()
#response = create_role()
#print (response)