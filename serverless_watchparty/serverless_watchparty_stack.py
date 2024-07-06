from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ecs as ecs,
    CfnOutput
)


class ServerlessWatchpartyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        vpc = ec2.Vpc(self, "Vpc",
            # nat_gateways=0,
            max_azs=1,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/20"),
            subnet_configuration=[{
                'name': 'public-subnet',
                'subnetType': ec2.SubnetType.PUBLIC,
                'cidrMask': 24
                }],
        )

        # security group add ingress
        cluster = ecs.Cluster(self, "EcsCluster",
            vpc=vpc,
            enable_fargate_capacity_providers=True,
            container_insights=True,
        )

        ecsTaskRole = iam.Role(self, 'TaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            description='For task.'
        )

        taskDefinition = ecs.FargateTaskDefinition(self, 'TaskDefinition',
            cpu=2048,
            memory_limit_mib=4096,
            task_role=ecsTaskRole
        )

        # watchPartyImage = ecs.ContainerImage.from_asset('./container')
        watchPartyImage = ecs.ContainerImage.from_registry('brilhartji/watchparty:latest')

        # minecraftServerContainer = ecs.ContainerDefinition(self, 
        #     'WatchPartyContainer',
        #     task_definition=taskDefinition,
        #     image=watchPartyImage,
        #     # logging=ecs.LogDrivers.aws_logs(stream_prefix='minecraft'),
        #     # environment={
        #     #     'EULA': 'TRUE'
        #     # },
        #     memory_reservation_mib=4096
        # )

        taskDefinition.add_container('WatchPartyContainer', image=watchPartyImage)


        # ecs fargate service for server
        service = ecs.FargateService(self, "MyService",
            cluster=cluster,
            task_definition=taskDefinition,
            desired_count=1,
            # deployment_alarms=ecs.DeploymentAlarmConfig(
            #     alarm_names=[elb_alarm.alarm_name],
            #     behavior=ecs.AlarmBehavior.ROLLBACK_ON_ALARM
            # )
        )

        service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(3000),
            description="Allow http inbound from VPC"
        )

        # CfnOutput(
        #     self, "LoadBalancerDNS",
        #     value=service.load_balancer.load_balancer_dns_name
        # )