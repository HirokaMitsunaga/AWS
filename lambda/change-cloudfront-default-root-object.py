import boto3
import os
import time
import logging
import sys

#ディストリビューションID`、CloudfrontのClientAPI、loggerの設定をする
distribution_id = os.environ['DistributionId']
cf_client = boto3.client('cloudfront')
logger = logging.getLogger(__name__)
#infoのログも出力するように設定する
logger.setLevel(20)

#S3へアップロードしたファイル名を取得する
def lambda_handler(event, context):
    file_name = event['Records'][0]['s3']['object']['key']
    logger.info('S3へアップロードされたファイル名は{file_name}です'.format(file_name=file_name))
    try:
        clear_cash_cloudfront(cf_client,file_name,distribution_id)
        logger.info('CloudFrontのキャッシュクリアに成功しました')
    except:
        logger.exception('CloudFrontのキャッシュクリアに失敗しました')
        sys.exit()
    try:
        change_cloudfront_defaultrootobject(cf_client,file_name,distribution_id)
        logger.info('CloudFrontのデフォルトルートオブジェクトの変更に成功しました')
    except:
        logger.exception('CloudFrontのデフォルトルートオブジェクトの変更に失敗しました')

#S3へアップロードしたファイル名でCloudFrontのキャッシュをクリアする
def clear_cash_cloudfront(cf_client,file_name,distribution_id):
    try:
        invalidation = cf_client.create_invalidation(DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Items': ['/{file_name}'.format(file_name=file_name)],
                    'Quantity': 1
                },
             'CallerReference': str(time.time())
             })
    except Exception as e:
        logging.exception(e)
        raise

#S3へアップロードしたファイル名でCloudFrontのデフォルトルートオブジェクトを変更する
def change_cloudfront_defaultrootobject(cf_client,file_name,distribution_id):
    try:
        distribution = cf_client.get_distribution(Id=distribution_id)
        ETag = distribution['ETag']
        distribution_config = distribution['Distribution']['DistributionConfig']
        distribution_config['DefaultRootObject'] = file_name
        cf_client.update_distribution(DistributionConfig=distribution_config, Id=distribution_id, IfMatch=ETag)
    except Exception as e:
        logging.exception(e)
        raise