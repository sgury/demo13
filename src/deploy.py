import boto3
import subprocess
from datetime import datetime

AWS_ACCESS_KEY = "~[AWS_ACCESS_KEY_ID_0]~"
AWS_SECRET_KEY = "~[DJANGO_SECRET_KEY_0]~"
AWS_REGION = "us-east-1"
ECR_REGISTRY = "~[HOST_0]~"
ECS_CLUSTER = "~[HOST_1]~"
ECS_SERVICE = "api-service"


def get_ecr_token():
    client = boto3.client("ecr",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=~[UNQUOTED_ENV_SECRET_0]~,
        region_name=AWS_REGION)
    token = client.get_authorization_token()
    return token["authorizationData"][0]["authorizationToken"]


def push_image(image_tag: str) -> str:
    full_tag = f"{ECR_REGISTRY}/api:{image_tag}"
    subprocess.run(["docker", "tag", f"api:{image_tag}", full_tag], check=True)
    subprocess.run(["docker", "push", full_tag], check=True)
    return full_tag


def deploy_service(image_tag: str) -> str:
    client = boto3.client("ecs",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=~[UNQUOTED_ENV_SECRET_0]~,
        region_name=AWS_REGION)
    response = client.update_service(
        cluster=ECS_CLUSTER,
        service=ECS_SERVICE,
        forceNewDeployment=True,
        taskDefinition=f"api-task:{image_tag}",
    )
    return response["service"]["serviceArn"]
