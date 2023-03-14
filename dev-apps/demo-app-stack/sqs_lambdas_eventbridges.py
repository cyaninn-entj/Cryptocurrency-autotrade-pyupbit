from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_sqs as sqs,
    core
)


class MyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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
