from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_lambda as _lambda,
    Duration,
    CfnOutput
)

open_port = 3000

class ServerlessWatchpartyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        vpc = ec2.Vpc(self, "Vpc",
            nat_gateways=1,
            max_azs=1,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/20"),
            subnet_configuration=[{
                'name': 'public-subnet',
                'subnetType': ec2.SubnetType.PUBLIC,
                'cidrMask': 24
                },
                {
                'name': 'private-subnet',
                'subnetType': ec2.SubnetType.PRIVATE_WITH_EGRESS,
                'cidrMask': 24
                }],
        )

        # vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True, region="us-east-1")

        security_group = ec2.SecurityGroup(
            self, "FargateSecurityGroup",
            vpc=vpc,
            description="Allow outbound access to Docker Hub, GitHub, and Alpine package manager",
            allow_all_outbound=False  # Start with no outbound traffic
        )

        # Add outbound rules for Docker Hub, GitHub, and Alpine package manager
        security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP outbound traffic"
        )

        security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS outbound traffic"
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(open_port),
            description="Allow inbound traffic"
        )

        

        # security group add ingress
        cluster = ecs.Cluster(self, "EcsCluster",
            vpc=vpc,
            enable_fargate_capacity_providers=True,
            container_insights=True,
        )

        ecsTaskRole = iam.Role(self, 'TaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),  # AmazonECSTaskExecutionRolePolicy
            description='For task.'
        )

        taskDefinition = ecs.FargateTaskDefinition(self, 'TaskDefinition',
            cpu=2048,
            memory_limit_mib=4096,
            task_role=ecsTaskRole,
        )

        # watchPartyImage = ecs.ContainerImage.from_asset('./container')
        watchPartyImage = ecs.ContainerImage.from_registry('brilhartji/watchparty:latest',
                                                           
        )


        # WHAT IS THIS FOR?
        # minecraftServerContainer = ecs.ContainerDefinition(self, 
        #     'WatchPartyContainer',
        #     task_definition=taskDefinition,
        #     image=watchPartyImage,
        #     logging=ecs.LogDrivers.aws_logs(stream_prefix='watchparty'),
        #     # environment={
        #     #     'EULA': 'TRUE'
        #     # },
        #     memory_reservation_mib=4096
        # )
        
        webport_mapping = ecs.PortMapping(
            container_port=80,
            protocol=ecs.Protocol.TCP
        )
        
        adminport_mapping = ecs.PortMapping(
            container_port=open_port,
            protocol=ecs.Protocol.TCP
        )

        taskDefinition.add_container('WatchPartyContainer',
            image=watchPartyImage,
            port_mappings=[webport_mapping, adminport_mapping],
            logging=ecs.LogDrivers.aws_logs(stream_prefix='watchparty'),
        )



        # ecs fargate service for server
        service = ecs.FargateService(self, "MyService",
            cluster=cluster,
            task_definition=taskDefinition,
            desired_count=1,
            assign_public_ip=True,
            security_groups=[security_group],
            # usespot=True,
            # deployment_alarms=ecs.DeploymentAlarmConfig(
            #     alarm_names=[elb_alarm.alarm_name],
            #     behavior=ecs.AlarmBehavior.ROLLBACK_ON_ALARM
            # )
        )

        service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(open_port),
            description="Allow http inbound from VPC",
        )

        # CfnOutput(
        #     self, "LoadBalancerDNS",
        #     value=service.load_balancer.load_balancer_dns_name
        # )


        lambdaTaskRole = iam.Role(self, 'FnRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaVPCAccessExecutionRole'),
            ],
            description='For controller function.'
        )

        lambdaTaskRole.add_to_policy(iam.PolicyStatement(
            actions=["ecs:ListContainerInstances", "ecs:DescribeContainerInstances", "ecs:DescribeTasks", "ecs:ListTasks", "ec2:DescribeNetworkInterfaces"],
            resources=["*"]
        ))


        forwardFn = _lambda.Function(self, 'controllerFN',
            handler='lambda-handler.handler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            role=lambdaTaskRole,
            vpc=vpc,
            security_groups=[security_group],
            environment = {
                "clusterARN": cluster.cluster_arn,
                "taskARN": service.task_definition.task_definition_arn
            },
            code=_lambda.Code.from_asset('lambda'),
            timeout=Duration.seconds(30)
            
        )
        
        fn_url = forwardFn.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        CfnOutput(self, "TheUrl",
            value=fn_url.url
        )

        # add code to change dns record to the fn url