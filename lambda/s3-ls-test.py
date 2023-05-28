import boto3
import csv

bucket_name = 'test.prod-hiro-aws.com'
#バケットの中のファイル名、ファイルサイズ、時刻を取得し、結果を２次元配列で返す関数
#1000件を超えるとobjects.get("isTruncated")の値がtrueになるためそれ以降にもう一回list_objects_v2を実行してバケットの中のファイルが存在する限り取得し続ける
def get_all_file_detail(bucket_name,file_list, marker):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    objects = bucket.meta.client.list_objects_v2(Bucket=bucket.name,StartAfter=marker)
    if "Contents" in objects:
        for content in objects["Contents"]:
            #ファイルサイズが0のものを弾く
            if content["Size"] != 0:
                file_list.extend([[content["Key"],content["Size"],content["LastModified"]]])
                #print(objects["IsTruncated"])
                #print(objects.get("Contents"))
                #objects["IsTruncated"]=True
                #1000行を超えたらisTruncatedがTrueになるため、1000行以降も取得できるように再度関数を実行する
                if objects.get("isTruncated")==True:
                    return get_all_file_detail(bucket_name=bucket_name, file_list=file_list, marker=file_list[-1])
    return file_list

#get_all_file_detailの実行
file_detail = get_all_file_detail(bucket_name, [[]], "")

#S3バケットから取得しものをcsvファイルへの書き込み
csv_path = r"/Users/mistasunagahiroka/AWS/AWS/lambda/test.csv"
with open(csv_path, 'a', newline='') as file:
    writer = csv.writer(file, lineterminator='\n')
    writer.writerows(file_detail)