import boto3
import os
import time

#ディストリビューションIDとboto3のclientを取得する
distribution_id = os.environ['DistributionId']
cf_client = boto3.client('cloudfront')

#S3へアップロードしたファイル名を取得する
def lambda_handler(event, context):
 file_name = event['Records'][0]['s3']['object']['key']
 print("key =", file_name)
 clear_cash_cloudfront(cf_client,file_name,distribution_id)
 change_cloudfront_defaultrootobject(cf_client,file_name,distribution_id)

#S3へアップロードしたファイル名でCloudFrontのキャッシュをクリアする
def clear_cash_cloudfront(cf_client,file_name,distribution_id):
 invalidation = cf_client.create_invalidation(DistributionId=distribution_id,
     InvalidationBatch={
         'Paths': {
             'Items': ['/{file_name}'.format(file_name=file_name)],
             'Quantity': 1
         },
      'CallerReference': str(time.time())
      })

#S3へアップロードしたファイル名でCloudFrontのデフォルトルートオブジェクトを変更する
def change_cloudfront_defaultrootobject(cf_client,file_name,distribution_id):
 distribution = cf_client.get_distribution(Id=distribution_id)
 ETag = distribution['ETag']
 distribution_config = distribution['Distribution']['DistributionConfig']
 distribution_config['DefaultRootObject'] = file_name
 cf_client.update_distribution(DistributionConfig=distribution_config, Id=distribution_id, IfMatch=ETag)