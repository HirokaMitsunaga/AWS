import boto3
import csv

s3 = boto3.client('s3')
bucket_name = 'test.prod-hiro-aws.com'
file_list = [[]]

def get_all_file_detail(bucket_name,file_list, marker):
    response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
    while True:
        # オブジェクト表示
        for obj in response['Contents']:
            #print(obj['Key'])
            file_list.extend([[obj["Key"],obj["Size"],obj["LastModified"]]])    
        # 'NextContinuationToken'が存在する場合は、次のデータ取得。
        if 'NextContinuationToken' in response:
            token = response['NextContinuationToken']
            response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5, ContinuationToken=token)
        else:
            break
    return file_list

#get_all_file_detailの実行
file_detail = get_all_file_detail(bucket_name, [[]], "")

#S3バケットから取得しものをcsvファイルへの書き込み
csv_path = r"/Users/mistasunagahiroka/AWS/AWS/lambda/test.csv"
with open(csv_path, 'a', newline='') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(file_detail)