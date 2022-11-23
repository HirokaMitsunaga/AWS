#!/bin/bash
set -euo pipefail

# Set timezone
sudo timedatectl set-timezone Asia/Tokyo
timedatectl

# Variables
PREFIX="cloud01"
EC2_NAME="${PREFIX}-web-01"
INSTANCE_ID=$(aws ec2 describe-instances --filter Name=tag:Name,Values=$EC2_NAME Name=instance-state-name,Values=running \
    --query "Reservations[*].Instances[*].InstanceId" --output text) && echo $INSTANCE_ID

# Stop EC2
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID && echo "EC2 has stopped"
  
# AMI
DATETIME="$(date +%Y-%m-%d_%H-%M-%S)" && echo $DATETIME
IMAGE_ID=$(aws ec2 create-image \
  --instance-id $INSTANCE_ID \
  --name ${EC2_NAME}_${DATETIME} \
  --tag-specifications "ResourceType=image,Tags=[{Key=Name,Value=${EC2_NAME}_${DATETIME}}]" \
  --no-reboot \
  --query "ImageId" --output text) && echo $IMAGE_ID

#作成したAMIが利用可能になっているのか確認する。
aws ec2 wait image-available --image-ids $IMAGE_ID && echo "AMI created"
  
# Start EC2
aws ec2 start-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-running --instance-ids $INSTANCE_ID && echo "EC2 is running"
