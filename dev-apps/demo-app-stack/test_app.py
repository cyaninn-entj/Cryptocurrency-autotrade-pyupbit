import boto3

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('dev-general-table')

def lambda_handler(event, context):
    # Update the item in the DynamoDB table
    table.update_item(
        Key={
            'PartitionKey': 'test'
        },
        UpdateExpression='SET EndPrice = :val',
        ExpressionAttributeValues={
            ':val': 123
        }
    )

    return {
        'statusCode': 200,
        'body': 'Item updated successfully'
    }
