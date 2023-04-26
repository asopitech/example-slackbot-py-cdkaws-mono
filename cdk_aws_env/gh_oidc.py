# from aws_cdk import core
# from aws_cdk import aws_iam as iam

# import ssl
# import socket
# import hashlib

# def hash_server_certificate_sni(self, dns_name: str, port: int = 443):
#     """ Hash the server certificate for the given host name and port.

#     @param dns_name: The host name to connect to.
#     @param port: The port number to connect to.
#     @return: The SHA-1 hash in hexadecimal.
#     """
#     # Create a connection to the server.
#     context = ssl.create_default_context()
#     conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=dns_name)
#     conn.connect((dns_name, port))

#     # Retrieve the server certificate and return its hash.
#     der_cert_bin = conn.getpeercert(True)
#     return hashlib.sha1(der_cert_bin).hexdigest()

# github_actions_url = "https://token.actions.githubusercontent.com"
# github_pem_server_certificate = hash_server_certificate_sni(github_actions_url)

# class GhSlackbotOIDCStack(core.Stack):
#     def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
#         super().__init__(scope, id, **kwargs)

#         githubprovider = iam.OpenIdConnectProvider(self, "GithubProvider",
#             url=github_actions_url,
#             client_ids=["sts.amazonaws.com"],
#             thumbprints=[github_pem_server_certificate]
#         )

# app = core.App()
# GhSlackbotOIDCStack(app, "GitHubSlackbotOIDCStack")
# app.synth()

from aws_cdk import (
    aws_iam as iam,
    core,
)
from requests import get
from OpenSSL import crypto


class GithubActionsOidcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get the GitHub Actions OIDC thumbprint
        github_actions_oidc_url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
        cert_url = get(github_actions_oidc_url).json()["jwks_uri"]
        cert_pem = get(cert_url).content
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
        thumbprint = cert.digest("sha1").decode()

        # Create the OIDC provider
        github_actions_oidc_provider = iam.OpenIdConnectProvider(
            self,
            "GithubActions",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            thumbprint_list=[thumbprint]
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
                federated=github_actions_oidc_provider.arn,
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
        iam.RolePolicyAttachment(
            self,
            "AdminPolicy",
            policy=iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
            role=github_actions_role
        )


app = core.App()
GithubActionsOidcStack(app, "GithubActionsOidcStack")
app.synth()