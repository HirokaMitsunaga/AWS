import boto3
import os
import time

#get file name from s3bucket
def lambda_handler(event, context):
 input_key = event['Records'][0]['s3']['object']['key']
 print("key =", input_key)
 
 #cash clear cloud front
 cloudfront = boto3.client('cloudfront')
 distribution_id = os.environ['DistributionId']
 invalidation = cloudfront.create_invalidation(DistributionId=distribution_id,
     InvalidationBatch={
         'Paths': {
             'Items': ['/*.html'],
             'Quantity': 1
         },
      'CallerReference': str(time.time())
      })
      
 #channge cloudfront default-root-object
 distribution = cloudfront.get_distribution(Id=distribution_id)
 ETag = distribution['ETag']
 distribution_config = distribution['Distribution']['DistributionConfig']
 distribution_config['DefaultRootObject'] = input_key
 cloudfront.update_distribution(DistributionConfig=distribution_config, Id=distribution_id, IfMatch=ETag)