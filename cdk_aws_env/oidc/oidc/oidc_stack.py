from aws_cdk import (
    Stack,
    aws_iam as iam,
)
import ssl
import socket
import hashlib
from urllib.parse import urlparse

from constructs import Construct

class OidcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the GitHub Actions OIDC thumbprint
        github_actions_oidc_url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"

        # Extract the hostname from the OIDC URL
        parsed_url = urlparse(github_actions_oidc_url)
        hostname = parsed_url.hostname

        # Connect to the host and retrieve the certificate
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_der = ssock.getpeercert(binary_form=True)

        # Compute the thumbprint
        thumbprint = hashlib.sha1(cert_der).hexdigest()
        # Create the OIDC provider
        github_actions_oidc_provider = iam.OpenIdConnectProvider(
            self,
            "GithubActions",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            thumbprints=[thumbprint]
        )

        # Define the allowed GitHub repositories and paths
        allowed_github_repositories = ["foo", "bar"]
        github_org_name = "my-organization"
        full_paths = [f"repo:{github_org_name}/{repo}:*" for repo in allowed_github_repositories]

        # Create the IAM Role
        github_actions_role = iam.Role(
            self,
            "GithubActionsRole",
            assumed_by=iam.FederatedPrincipal(
                federated=github_actions_oidc_provider.open_id_connect_provider_arn,
                conditions={
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": full_paths
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            ),
            description="IAM Role for GitHub Actions OIDC"
        )

        # Attach the AdministratorAccess policy to the role
        admin_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        github_actions_role.add_managed_policy(admin_policy)
