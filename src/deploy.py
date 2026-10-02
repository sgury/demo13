import boto3
import subprocess
from datetime import datetime

AWS_ACCESS_KEY = "~[AWS_ACCESS_KEY_ID_0]~"
AWS_SECRET_KEY = "~[DJANGO_SECRET_KEY_0]~"
AWS_REGION = "us-east-1"
ECR_REGISTRY = "~[HOST_0]~"
ECS_CLUSTER = "~[HOST_1]~"
ECS_SERVICE = "api-service"


def get_ecr_token() -> str:
    """Return an authorization token for the configured Amazon ECR registry."""
    client = boto3.client("ecr",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=~[UNQUOTED_ENV_SECRET_0]~,
        region_name=AWS_REGION)
    token = client.get_authorization_token()
    return token["authorizationData"][0]["authorizationToken"]


def push_image(image_tag: str) -> str:
    """Tag and push an API Docker image to the configured ECR registry.

    Args:
        image_tag: Tag identifying the local API image.

    Returns:
        The fully qualified ECR image tag.
    """
    full_tag = f"{ECR_REGISTRY}/api:{image_tag}"
    subprocess.run(["docker", "tag", f"api:{image_tag}", full_tag], check=True)
    subprocess.run(["docker", "push", full_tag], check=True)
    return full_tag


def deploy_service(image_tag: str) -> str:
    """Trigger a new ECS deployment using the specified image tag.

    Args:
        image_tag: Tag to use in the ECS task definition.

    Returns:
        The ARN of the updated ECS service.
    """
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
