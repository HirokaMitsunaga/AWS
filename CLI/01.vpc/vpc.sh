#!/bin/bash
set -euo pipefail

# VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --instance-tenancy default \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=cloud01-vpc}]"

# InternetGateway
aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=cloud01-igw}]"

aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-0941e31e80982a59e \
  --vpc-id vpc-04b8bf3c9b44fe311

# Public subnet
aws ec2  create-subnet \
  --vpc-id vpc-04b8bf3c9b44fe311 \
  --cidr-block 10.0.11.0/24 \
  --availability-zone ap-northeast-1a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=cloud01-public-1a}]"

aws ec2  create-subnet \
  --vpc-id vpc-04b8bf3c9b44fe311 \
  --cidr-block 10.0.12.0/24 \
  --availability-zone ap-northeast-1c \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=cloud01-public-1c}]"

# Public routeTable
aws ec2 create-route-table \
  --vpc-id vpc-04b8bf3c9b44fe311 \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=cloud01-public-route}]"

aws ec2 create-route \
  --route-table-id rtb-05b640248887684a6 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-0941e31e80982a59e

aws ec2 associate-route-table \
  --route-table-id rtb-05b640248887684a6 \
  --subnet-id subnet-0447a7a5d140f48ca

aws ec2 associate-route-table \
  --route-table-id rtb-05b640248887684a6 \
  --subnet-id subnet-0286c3e945a544068
