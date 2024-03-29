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
    try:
        file_name = event['Records'][0]['s3']['object']['key']
        logger.info('S3へアップロードされたファイル名は{file_name}です'.format(file_name=file_name))
        clear_cashe_cloudfront(cf_client,file_name,distribution_id)
        change_cloudfront_defaultrootobject(cf_client,file_name,distribution_id)
    except Exception as e:
        logging.exception(e)

#S3へアップロードしたファイル名でCloudFrontのキャッシュをクリアする
def clear_cashe_cloudfront(cf_client,file_name,distribution_id):
    try:
        invalidation = cf_client.create_invalidation(DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Items': ['/{file_name}'.format(file_name=file_name)],
                    'Quantity': 1
                },
             'CallerReference': str(time.time())
             })
        
        #戻り値のHTTPStatusCodeが201である場合、成功としそれ以外は失敗したとする
        invalidation_responce = invalidation['ResponseMetadata']['HTTPStatusCode']
        if invalidation_responce == 201:
            #キャッシュがクリアされるまで待つ
            invalidation_id = invalidation['Invalidation']['Id']
            get_invalidation = cf_client.get_invalidation(DistributionId=distribution_id,Id=invalidation_id)
            invalidation_status = get_invalidation['Invalidation']['Status']
            while(invalidation_status != 'Completed'):
                print('CloudFrontのキャッシュがクリアされるまで待ちます。')
                time.sleep(10)
                get_invalidation = cf_client.get_invalidation(DistributionId=distribution_id,Id=invalidation_id)
                invalidation_status = get_invalidation['Invalidation']['Status']
                print('現在のステータスは{invalidation_status}です'.format(invalidation_status=invalidation_status))
            logger.info('CloudFrontのキャッシュクリアに成功しました')
        else:
            logger.exception('CloudFrontのキャッシュクリアに失敗しました')
            sys.exit()
    except Exception as e:
        logging.exception(e)
        raise e

#S3へアップロードしたファイル名でCloudFrontのデフォルトルートオブジェクトを変更する
def change_cloudfront_defaultrootobject(cf_client,file_name,distribution_id):
    try:
        distribution = cf_client.get_distribution(Id=distribution_id)
        ETag = distribution['ETag']
        distribution_config = distribution['Distribution']['DistributionConfig']
        distribution_config['DefaultRootObject'] = file_name
        update_distribution = cf_client.update_distribution(DistributionConfig=distribution_config,Id=distribution_id, IfMatch=ETag)
        
        #戻り値のHTTPStatusCodeが200である場合、成功としそれ以外は失敗したとする
        update_distribution_responce = update_distribution['ResponseMetadata']['HTTPStatusCode']
        if update_distribution_responce == 200:
            #ディストリビューションが更新されるまで待つ
            get_distribution = cf_client.get_distribution(Id=distribution_id)
            distribution_status = get_distribution['Distribution']['Status']
            while(distribution_status != 'Deployed'):
                print('CloudFrontのディストリビューションが変更されるまで待ちます')
                time.sleep(10)
                get_distribution = cf_client.get_distribution(Id=distribution_id)
                distribution_status = get_distribution['Distribution']['Status']
                print('現在のステータスは{distribution_status}です'.format(distribution_status=distribution_status))
            logger.info('CloudFrontのデフォルトルートオブジェクトの変更に成功しました')
        else:
            logger.exception('CloudFrontのデフォルトルートオブジェクトの変更に失敗しました')            
    except Exception as e:
        logging.exception(e)
        raise e