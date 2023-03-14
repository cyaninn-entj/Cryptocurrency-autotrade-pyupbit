from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    core
)

class MyStack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the DynamoDB table
        table = dynamodb.Table(
            self, 'DevGeneralTable',
            table_name='dev-general-table',
            partition_key=dynamodb.Attribute(name='service', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # Add an item to the table
        table.add_item(
            item={
                'service': 'ethereum-autotrade',
                'K-value': 0,
                'EndPrice': 0
            }
        )

"""
나는 아래 조건을 만족하는 aws-cdk python을 사용한 stack.py를 원한다.
cdk 작업은 ap-northeast-2 에서 실행될 예정이다.
1개의 dynamoDB table을 만들고 싶다.

테이블 이름은 dev-general-table로 설정.
파티션 키는 service name, string.
테이블 설정은 '설정 사용자 지정' 선택.
테이블 클래스는 DynamoDB Standard 선택.
읽기/쓰기 용량은 각각 1로 프로비저닝.
설정하지 않은 다른 값은 기본값으로 놓고 생성.

1개의 항목을 생성 service name(partition key) 의 값은 'ethereum-autotrade'.
새로운 2개의 속성을 추가할것이다.
첫번째 속성 이름은 K-value, 값은 숫자 타입으로 0으로 입력
두번째 속성 이름은 EndPrice, 값은 숫자 타입으로 0으로 입력
"""