#!/bin/bash
set -euo pipefail

# Variables
MY_DOMAIN="aws-and-infra-hiro.com"

# Route53 hosted zone
HOSTED_ZONE_ID=$(aws route53 create-hosted-zone \
  --name $MY_DOMAIN \
  --caller-reference "$(date +%Y-%m-%d_%H-%M-%S)" \
  --query "HostedZone.Id" --output text) && echo $HOSTED_ZONE_ID

# Get NS records
aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query 'ResourceRecordSets[?Type==`NS`].ResourceRecords[*].Value'

# ACM
CERTIFICATE_ARN=$(aws acm request-certificate \
  --domain-name *.${MY_DOMAIN} \
  --validation-method DNS \
  --query "CertificateArn" --output text) && echo $CERTIFICATE_ARN

VALIDATION_RECORD_NAME=$(aws acm describe-certificate \
  --certificate-arn $CERTIFICATE_ARN \
  --query "Certificate.DomainValidationOptions[*].ResourceRecord.Name" --output text) && echo $VALIDATION_RECORD_NAME

VALIDATION_RECORD_VALUE=$(aws acm describe-certificate \
  --certificate-arn $CERTIFICATE_ARN \
  --query "Certificate.DomainValidationOptions[*].ResourceRecord.Value" --output text) && echo $VALIDATION_RECORD_VALUE

## DNS validation
# Update record sets file
VALIDATION_RECORD_FILE=./recordsets/dnsvalidation.json
sed -i -e "s/%VALIDATION_RECORD_NAME%/$VALIDATION_RECORD_NAME/" $VALIDATION_RECORD_FILE
sed -i -e "s/%VALIDATION_RECORD_VALUE%/$VALIDATION_RECORD_VALUE/" $VALIDATION_RECORD_FILE

# Add record sets
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://$VALIDATION_RECORD_FILE

# Initialize
git restore $VALIDATION_RECORD_FILE


## ELB alias
MY_DOMAIN="aws-and-infra-hiro.com"
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones --query "HostedZones[?Name==\`${MY_DOMAIN}.\`].Id" --output text) && echo $HOSTED_ZONE_ID
PREFIX="cloud01"
ELB_NAME="${PREFIX}-alb"
FQDN="www.${MY_DOMAIN}"
ELB_HOSTED_ZONE_ID=$(aws elbv2 describe-load-balancers --query "LoadBalancers[?LoadBalancerName==\`$ELB_NAME\`].CanonicalHostedZoneId" --output text) && echo $ELB_HOSTED_ZONE_ID
ELB_DNS_NAME=$(aws elbv2 describe-load-balancers --query "LoadBalancers[?LoadBalancerName==\`$ELB_NAME\`].DNSName" --output text) && echo $ELB_DNS_NAME

# Update record sets file
ELB_RECORD_FILE=./recordsets/elb.json
sed -i -e "s/%FQDN%/$FQDN/" $ELB_RECORD_FILE
sed -i -e "s/%ELB_HOSTED_ZONE_ID%/$ELB_HOSTED_ZONE_ID/" $ELB_RECORD_FILE
sed -i -e "s/%ELB_DNS_NAME%/$ELB_DNS_NAME/" $ELB_RECORD_FILE

# Add record sets
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://$ELB_RECORD_FILE
  
# Initialize
git restore $ELB_RECORD_FILE
