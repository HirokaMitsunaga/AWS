import json
import boto3
#import cfnresponse

#SUCCESS = "SUCCESS"
#FAILED = "FAILED"

print('Loading function')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}
    #try:
    if event['RequestType'] == 'Delete':
        print("Request Type:",event['RequestType'])
        Id=event['ResourceProperties']['Id']
        Bucket=event['ResourceProperties']['Bucket']
        delete_notification(Id, Bucket)
        print("Sending response to custom resource after Delete")
    elif event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
        print("Request Type:",event['RequestType'])
        Id=event['ResourceProperties']['Id']
        Prefix=event['ResourceProperties']['Prefix']
        Suffix=event['ResourceProperties']['Suffix']
        LambdaArn=event['ResourceProperties']['LambdaArn']
        Bucket=event['ResourceProperties']['Bucket']
        add_notification(Id, Prefix, Suffix, LambdaArn, Bucket)
        responseData={'Bucket':Bucket}
        print("Sending response to custom resource")
    #    responseStatus = 'SUCCESS'
    #except Exception as e:
    #    print('Failed to process:', e)
    #    responseStatus = 'FAILED'
    #    responseData = {'Failure': 'Something bad happened.'}
    #cfnresponse.send(event, context, responseStatus, responseData)

def add_notification(Id, Prefix, Suffix, LambdaArn, Bucket):
    bucket_notification = s3.BucketNotification(Bucket)
    print(bucket_notification.lambda_function_configurations)

    lambda_function_configurations = bucket_notification.lambda_function_configurations

    if lambda_function_configurations is None:
        lambda_function_configurations = []
    else:
        lambda_function_configurations = [e for e in lambda_function_configurations if e['Id'] != Id]

    lambda_config = {}
    lambda_config['Id'] = Id
    lambda_config['LambdaFunctionArn'] = LambdaArn
    lambda_config['Events'] = ['s3:ObjectCreated:Put']
    lambda_config['Filter'] = {'Key': {'FilterRules': [
            {'Name': 'Prefix', 'Value': Prefix},
            {'Name': 'Suffix', 'Value': Suffix}
            ]}
    }
    
    lambda_function_configurations.append(lambda_config)
    print(lambda_function_configurations)
    
    put_bucket_notification(bucket_notification, lambda_function_configurations)
    
    print("Put request completed....")
           
def delete_notification(Id, Bucket):

    bucket_notification = s3.BucketNotification(Bucket)
    print(bucket_notification.lambda_function_configurations)

    lambda_function_configurations = bucket_notification.lambda_function_configurations

    if lambda_function_configurations is not None:
        lambda_function_configurations = [e for e in lambda_function_configurations if e['Id'] != Id]

    print(lambda_function_configurations)

    put_bucket_notification(bucket_notification, lambda_function_configurations)

    print("Delete request completed....")

def put_bucket_notification(BucketNotification, LambdaFunctionConfigurations):

    notification_configuration = {}
    if LambdaFunctionConfigurations is not None:
        notification_configuration['LambdaFunctionConfigurations'] = LambdaFunctionConfigurations
    
    if BucketNotification.queue_configurations is not None:
        notification_configuration['QueueConfigurations'] = BucketNotification.queue_configurations

    if BucketNotification.topic_configurations is not None:
        notification_configuration['TopicConfigurations'] = BucketNotification.topic_configurations

    print(notification_configuration)
    
    response = BucketNotification.put(
    NotificationConfiguration= notification_configuration
    )