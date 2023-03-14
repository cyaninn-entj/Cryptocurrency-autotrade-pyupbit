from aws_cdk import (
    core,
    aws_ec2 as ec2
)

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) :
        super().__init__(scope, id, **kwargs)

        # Retrieve the default VPC
        vpc = ec2.Vpc.from_lookup(self, 'Vpc', is_default=True)

        # Define the AMI ID and instance type
        ami_id = 'ami-0e38c97339cddf4bd'
        instance_type = 't3a.micro'

        # Define the key pair name, subnet ID, security group ID, and instance name
        key_pair_name = 'dev-all'
        subnet_id = 'subnet-05cf568ac20acb748'
        security_group_id = 'sg-08c21160a4cdd32fd'
        instance_name = 'ehereum-trade-server'

        # Create the EC2 instance
        instance = ec2.Instance(
            self, 'EC2Instance',
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ec2.MachineImage.generic_linux(ami_id),
            key_name=key_pair_name,
            vpc_subnets=ec2.SubnetSelection(subnet_id=subnet_id),
            security_group=ec2.SecurityGroup.from_security_group_id(self, 'SecurityGroup', security_group_id),
            instance_name=instance_name
        )

        # Enable automatic public IP assignment 
        instance.instance.add_property_override("AssociatePublicIpAddress", True)



