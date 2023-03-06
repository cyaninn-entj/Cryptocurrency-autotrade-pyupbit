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

        # Create a VPC for the instance
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC
                )
            ]
        )

        # Create an EC2 instance
        instance = ec2.Instance(
            self, "MyInstance",
            instance_type=ec2.InstanceType("t3a.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            key_name="my-ec2-keypair"
        )

        # Create two Lambda functions
        function1 = _lambda.Function(
            self, "MyLambdaFunction1",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function1.handler",
            code=_lambda.Code.from_asset("path/to/lambda/function1"),
            timeout=core.Duration.seconds(30)
        )

        function2 = _lambda.Function(
            self, "MyLambdaFunction2",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function2.handler",
            code=_lambda.Code.from_asset("path/to/lambda/function2"),
            timeout=core.Duration.seconds(30)
        )

        # Create a DynamoDB table
        table = dynamodb.Table(
            self, "MyDynamoDBTable",
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
            alarm_name="my-cpu-alarm"
        )

        alarm2 = cloudwatch.Alarm(
            self, "MyCloudWatchAlarm2",
            alarm_description="My second CloudWatch alarm",
            metric=function1.metric_errors(),
            threshold=5,
            evaluation_periods=3,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_name="my-error-alarm"
        )

        # Add an action to the first alarm
        alarm1.add_alarm_action(
            cw_actions.SnsAction(
                topic=my_sns_topic,
                message_body="CPU utilization is above 80%"
            )
        )

app = core.App()
MyStack(app, "MyStack")
app.synth()
