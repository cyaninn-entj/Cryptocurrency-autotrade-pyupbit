from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_sqs as sqs
)
from constructs import Construct

class EthereumAutotradeStack(Stack):
    def __init__(self, scope:Construct, construct_id: str, **kwargs) -> None :
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve the default VPC
        vpc = ec2.Vpc.from_lookup(self, 'Vpc', is_default=True)

        # Define the AMI ID and instance type
        ami_id = 'ami-0e38c97339cddf4bd'
        instance_type = 't3a.micro'

        # Define the key pair name, subnet ID, security group ID, and instance name
        key_pair_name = 'dev-all'
        my_subnet_id = 'subnet-05cf568ac20acb748'
        security_group_id = 'sg-08c21160a4cdd32fd'
        instance_name = 'ehereum-trade-server'

        ami_map={
                instance_type: ami_id
        }

        # Create the EC2 instance
        instance = ec2.Instance(
            self, 'EC2Instance',
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ec2.MachineImage.generic_linux(ami_map),
            key_name=key_pair_name,
            vpc_subnets=ec2.SubnetSelection(subnet_id=my_subnet_id),
            security_group=ec2.SecurityGroup.from_security_group_id(self, 'SecurityGroup', security_group_id),
            instance_name=instance_name
        )

        # Enable automatic public IP assignment 
        instance.instance.add_property_override("AssociatePublicIpAddress", True)





        # Create the DynamoDB table
        table = dynamodb.Table(
            self, 'DevGeneralTable',
            table_name='dev-general-table',
            partition_key=dynamodb.Attribute(name='service', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # Add an item to the table (prod)
        table.add_item(
            item={
                'service': 'ethereum-autotrade',
                'K-value': 0,
                'EndPrice': 0
            }
        )

        # Add an item to the table (test)
        table.add_item(
            item={
                'service': 'test-k',
                'K-value': 230308,
                'EndPrice': 1
            }
        )

        # Add an item to the table (test)
        table.add_item(
            item={
                'service': 'test-ai',
                'K-value': 230315,
                'EndPrice': 1
            }
        )





        # Create an SQS queue
        queue = sqs.Queue(self, 'queue-for-ethereum-autotrade-lambdas', queue_name='queue-for-ethereum-autotrade-lambdas')

        # Create the "best-K" Lambda function
        bestk_lambda = _lambda.Function(
            self, 'best-K',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda_bestk'),
            handler='app.lambda_handler',
            timeout=core.Duration.minutes(1)
        )

        # Grant permission to access the DynamoDB table
        table = dynamodb.Table.from_table_name(self, 'dev-general-table', 'dev-general-table')
        table.grant_read_write_data(bestk_lambda)

        # Create the "endpriceWithAI" Lambda function
        endprice_lambda = _lambda.Function(
            self, 'endpriceWithAI',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda_endpriceWithAI'),
            handler='app.lambda_handler',
            memory_size=4096,
            timeout=core.Duration.minutes(10)
        )

        # Grant permission to access the DynamoDB table
        table.grant_read_write_data(endprice_lambda)

        # Create the "alarm-for-bestk.lambda" EventBridge rule
        alarm_rule_bestk = events.Rule(
            self, 'alarm-for-bestk.lambda',
            schedule=events.Schedule.cron_minute(hours=23, minute=50),
            targets=[targets.LambdaFunction(bestk_lambda)],
            dead_letter_queue=queue
        )

        # Create the "alarm-for-endpriceWithAI.lambda" EventBridge rule
        alarm_rule_endprice = events.Rule(
            self, 'alarm-for-endpriceWithAI.lambda',
            schedule=events.Schedule.cron('0 * * * *'),
            targets=[targets.LambdaFunction(endprice_lambda)],
            dead_letter_queue=queue
        )