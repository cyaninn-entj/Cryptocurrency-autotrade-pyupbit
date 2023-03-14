# [local] dockerfile upload
scp -i [identity_file] Dockerfile ubuntu@[target ip]

# [jenkins-server] docker login
docker login
docker build -t cyaninn/awscdk_python:23.03.v1 .
docker push cyaninn/awscdk_python:23.03.v1
docker run -it -d --name CDK cyaninn/awscdk_python:23.03.v1
docker exec -it CDK bash

# [CDK container] check installed tools
python3 --version
curl --version
zip
nodejs -v
npm --version
aws --version
cdk --version


# [CDK container] aws-cli configure
aws configure
# AWS Access Key ID [None]: 
# AWS Secret Access Key [None]: 
# Default region name [None]: ap-northeast-2
# Default output format [None]: json

cat source.bat
source .venv/bin/activate

# Bootstrapping environment
cdk bootstrap

# requirements.txt edited appropriately to allow upgrades, 
# issue this command to upgrade your project's installed modules at any time
pip install --upgrade -r requirements.txt

cdk synth                 # app defines single stack
cdk deploy Happy Grumpy   # app defines two or more stacks; two are deployed

