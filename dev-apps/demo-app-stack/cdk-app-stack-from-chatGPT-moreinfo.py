from aws_cdk import (
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    core,
)

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Use the 2a subnet in the default VPC
        subnet_selection = ec2.SubnetSelection(subnet_id='subnet-05cf568ac20acb748')

        # Get the default VPC
        default_vpc = ec2.Vpc.from_lookup(self, 'DefaultVPC', is_default=True)

        # Create an EC2 instance
        instance = ec2.Instance(
            self, "ethereum-trade-server",
            instance_type=ec2.InstanceType("t3a.micro"),
            machine_image=ec2.MachineImage.lookup(name="ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220228", owners=["099720109477"]),
            vpc=default_vpc,
            vpc_subnets=subnet_selection,
            key_name="dev-all",
            security_group=ec2.SecurityGroup.from_security_group_id(self, "MySG", security_group_id="sg-0774cd1a076ba7269"),
            vpc_subnets_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            allow_all_outbound=True,
            machine_name="ethereum-trade-server",
            public_ip_address=True
        )

        # Create two Lambda functions
        function1 = _lambda.Function(
            self, "demo-best-k",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function1.handler",
            code=_lambda.Code.from_asset("path/to/lambda/function1"),
            timeout=core.Duration.seconds(30),
            vpc=default_vpc,
            vpc_subnets=subnet_selection,
            environment={
                'TABLE_NAME': 'for-ethereum-autotrade'
            }
        )
        function1.add_to_role_policy(statement=dynamodb.Table.from_table_name(self, "DynamoDBTable", "for-ethereum-autotrade").grant_read_write_data())

        function2 = _lambda.Function(
            self, "demo-AI",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function2.handler",
            code=_lambda.Code.from_asset("path/to/lambda/function2"),
            timeout=core.Duration.seconds(30),
            vpc=default_vpc,
            vpc_subnets=subnet_selection,
            environment={
                'TABLE_NAME': 'for-ethereum-autotrade'
            }
        )
        function2.add_to_role_policy(statement=dynamodb.Table.from_table_name(self, "DynamoDBTable", "for-ethereum-autotrade").grant_read_write_data())

        # Create a DynamoDB table
        table = dynamodb.Table(
            self, "MyDynamoDBTable",
            table_name="for-ethereum-autotrade",
            partition_key=dynamodb.Attribute(
                name="ID",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Create two CloudWatch alarms
        alarm1 = cloudwatch.Alarm(
            self, "MyCloudWatchAlarm1",
            alarm_description="My first CloudWatch alarm",
            metric=instance.metric_cpu_utilization(),
            threshold=80,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_name="alarm-for-lambda-bestk"
        )

        alarm2 = cloudwatch.Alarm(
            self, "MyCloudWatchAlarm2",
            alarm_description="My second CloudWatch alarm",
            metric=function1.metric_errors(),
            threshold=5,
            evaluation_periods=3,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_name="alarm-for-lambda-ai"
        )

app = core.App()
MyStack(app, "MyStack")
app.synth()