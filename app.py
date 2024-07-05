#!/usr/bin/env python3

import aws_cdk as cdk

from serverless_watchparty.serverless_watchparty_stack import ServerlessWatchpartyStack


app = cdk.App()
ServerlessWatchpartyStack(app, "ServerlessWatchpartyStack")
app.synth()
