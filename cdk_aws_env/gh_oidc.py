from aws_cdk import core
from aws_cdk import aws_iam as iam

import ssl
import socket
import hashlib

def hash_server_certificate_sni(self, dns_name: str, port: int = 443):
    """ Hash the server certificate for the given host name and port.

    @param dns_name: The host name to connect to.
    @param port: The port number to connect to.
    @return: The SHA-1 hash in hexadecimal.
    """
    # Create a connection to the server.
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=dns_name)
    conn.connect((dns_name, port))

    # Retrieve the server certificate and return its hash.
    der_cert_bin = conn.getpeercert(True)
    return hashlib.sha1(der_cert_bin).hexdigest()

github_actions_url = "https://token.actions.githubusercontent.com"
github_pem_server_certificate = hash_server_certificate_sni(github_actions_url)

class GhSlackbotOIDCStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        githubprovider = iam.OpenIdConnectProvider(self, "GithubProvider",
            url=github_actions_url,
            client_ids=["sts.amazonaws.com"],
            thumbprints=[github_pem_server_certificate]
        )

app = core.App()
GhSlackbotOIDCStack(app, "GitHubSlackbotOIDCStack")
app.synth()

