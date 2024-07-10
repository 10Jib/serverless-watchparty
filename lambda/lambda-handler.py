import logging
import os
import json

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def redirect_to_ecs(event, context):
    response = {
        "statusCode": 302,
        "headers": {
            "Location": "ecs_container_url"
        },
        "body": json.dumps({
            "message": "Redirecting to ECS container"
        })
    }
    return response


def handler(event, context):
    """
    Accepts an action and a single number, performs the specified action on the number,
    and returns the result. The only allowable action is 'increment'.

    :param event: The event dict that contains the parameters sent when the function
                  is invoked.
    :param context: The context in which the function is called.
    :return: The result of the action.
    """
    clusterARN = os.getenv('clusterARN')
    containerID = os.getenv('containerID')

    logger.log(logging.INFO, f"Function started with clusterARN: {clusterARN} and containerID: {containerID}")

    client = boto3.client('ecs')

    response = client.list_container_instances(
        cluster=clusterARN,
    )

    # if containers are active, describe them and get their status.

    # response = client.describe_container_instances(
    #     cluster=clusterARN,
    #     containerInstances=[
    #         containerID,
    #     ],
    # )

    # check to see if this is a base get or xhtml request
    # check to see if service is up, and what ip is
    # return html if service is down, otherwise, straight to the service


    # result = None
    # action = event.get("action")
    # if action == "increment":
    #     result = event.get("number", 0) + 1
    #     logger.info("Calculated result of %s", result)
    # else:
    #     logger.error("%s is not a valid action.", action)

    # response = {"result": result}
    return json.dumps(response)