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
    taskARN = os.getenv('taskARN')

    logger.log(logging.INFO, f"Function started with clusterARN: {clusterARN} and containerID: {taskARN}")

    ecsClient = boto3.client('ecs')
    ec2Client = boto3.client('ec2')

    response = ecsClient.list_tasks(
        cluster=clusterARN
    )


    response = ecsClient.describe_tasks(
        cluster=clusterARN,
        tasks=[
            response['taskArns'][0],
        ]
    )

    # if containers are active, describe them and get their status.
    if len(response['tasks']) == 0:
        return {'body': 'No tasks instances found.'}  # should also start task
    
    if len(response['tasks'][0]) > 1:
        logger.error("More than one task found. This should not happen.")

    # response = ecsClient.describe_container_instances(
    #     cluster=clusterARN,
    #     containerInstances=response['containerInstanceArns'],
    # )
    # print(response[0]['status'])
    logger.info(response['tasks'][0]['containers'][0]['lastStatus'])




    # Describe the tasks to find associated ENIs
    attachments = response['tasks'][0]['attachments'][0]['details']
    eni_id = [d['value'] for d in attachments if d['name'] == 'networkInterfaceId'][0]

    # Describe the ENI to get the public IP
    eni_response = ec2Client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
    public_ip = eni_response['NetworkInterfaces'][0]['Association']['PublicIp']

    print("Public IP:", public_ip)



    return {
        'statusCode': 200,
        'body': json.dumps(public_ip)
    }
    # return response['tasks'][0]['containers'][0]['networkInterfaces'][0]

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