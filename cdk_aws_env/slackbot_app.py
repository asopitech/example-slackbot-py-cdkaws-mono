from aws_cdk import core
from aws_cdk import aws_lambda as _lambda

class SlackbotExampleLambdaStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        my_lambda = _lambda.Function(
            self, "SlackbotExampleFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler.main",
            code=_lambda.Code.from_asset("../slackbot_lambda"),
        )

app = core.App()
SlackbotExampleLambdaStack(app, "SlackbotExampleLambdaStack")
app.synth()