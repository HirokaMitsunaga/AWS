import boto3
import os
import time

#get file name from S3bucket
def lambda_handler(event, context):
 input_key = event['Records'][0]['s3']['object']['key']
 print("key =", input_key)
 
 #cash clear CloudFront
 cloudfront = boto3.client('cloudfront')
 distribution_id = os.environ['DistributionId']
 invalidation = cloudfront.create_invalidation(DistributionId=distribution_id,
     InvalidationBatch={
         'Paths': {
             'Items': ['/{input_key}'.format(input_key=input_key)],
             'Quantity': 1
         },
      'CallerReference': str(time.time())
      })
      
 #change CloudFront DefaultRootObject
 distribution = cloudfront.get_distribution(Id=distribution_id)
 ETag = distribution['ETag']
 distribution_config = distribution['Distribution']['DistributionConfig']
 distribution_config['DefaultRootObject'] = input_key
 cloudfront.update_distribution(DistributionConfig=distribution_config, Id=distribution_id, IfMatch=ETag)