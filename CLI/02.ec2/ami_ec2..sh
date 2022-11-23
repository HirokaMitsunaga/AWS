#!/bin/bash
set -euo pipefail

# Variables
# AMI_ID=$(aws ssm get-parame ters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --query "Parameters[*].Value" --output text) && echo $AMI_ID
PUBLIC_SUBNET_ID=$(aws ec2 describe-subnets --filters Name=tag:Name,Values=${PREFIX}-public-subnet-1c --query "Subnets[*].SubnetId" --output text) && echo $PUBLIC_SUBNET_ID
EC2_SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=tag:Name,Values=${PREFIX}-ec2-sg --query "SecurityGroups[*].GroupId" --output text) && echo $EC2_SECURITY_GROUP_ID
EC2_NAME="${PREFIX}-web-02"
PRIVATE_IP_ADDRESS="10.0.12.11"
AMI_ID=$(aws ec2 describe-images --owner self --filters Name=tag:Name,Values=${PREFIX}-web-01_* --query "sort_by(Images, &CreationDate)[-1].ImageId" --output text) && echo $AMI_ID

# EC2
INSTANCE_ID=$(aws ec2 run-instances \aws ec2 describe-images --owner self --filters Name=tag:Name,Values=${PREFIX}-web-01_* --query "sort_by(Images, &CreationDate)[-1].ImageId"
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --count 1 \
  --subnet-id $PUBLIC_SUBNET_ID \
  #パブリックIPアドレスの自動割り当てをの有効化
  --associate-public-ip-address \
  #インスタンスプロファイルの関連付け
  --iam-instance-profile Name=${PREFIX}-ec2-role \
  #インスタンスの終了保護
  --enable-api-termination \
  #詳細モニタリングの無効化
  --monitoring Enabled=false \
  --private-ip-address $PRIVATE_IP_ADDRESS \
  #nginxとMySQLをインストールしてnginxのホームディレクトリを
  --user-data file://param/userdata.sh \
  #EBSの情報をjsonファイルから読み込む
  --block-device-mappings file://param/volume.json \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$EC2_NAME}]" \
  --security-group-ids $EC2_SECURITY_GROUP_ID \
  --key-name ${PREFIX}-key \
  --query "Instances[*].InstanceId" \
  --output text) && echo $INSTANCE_ID

#describe Instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
--filters Name=tag:Name,Values=${PREFIX}-web-01 \
--query "Reservations[*].Instances[*].InstanceId" \
--output text) && echo $INSTANCE_ID
  
#  INSTANCE_ID=$(aws ec2 describe-instances \
#--filters Name=tag:Name,Values=${PREFIX}-web-01 \
#--query "Reservations[*].Instances[*].InstanceId" \
#--output text) && echo $INSTANCE_ID



NETWORK_INTERFACE_ID=$(aws ec2 describe-instances \
  --instance-id $INSTANCE_ID \
  --query "Reservations[*].Instances[*].NetworkInterfaces[*].NetworkInterfaceId" \
  --output text) && echo $NETWORK_INTERFACE_ID

VOLUME_IDS=$(aws ec2 describe-instances \
  --instance-id $INSTANCE_ID \
  --query "Reservations[*].Instances[*].BlockDeviceMappings[*].Ebs.VolumeId" \
  --output text) && echo $VOLUME_IDS

aws ec2 create-tags --resources $NETWORK_INTERFACE_ID $VOLUME_IDS --tags Key=Name,Value=$EC2_NAME

# Check HTTP connectionll
PUBLIC_IP_ADDRESS=$(aws ec2 describe-instances --instance-id $INSTANCE_ID --query "Reservations[*].Instances[*].PublicIpAddress" --output text) && echo $PUBLIC_IP_ADDRESS
curl http://$PUBLIC_IP_ADDRESS

