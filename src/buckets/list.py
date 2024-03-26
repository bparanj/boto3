import boto3

s3 = boto3.client('s3')

response = s3.list_buckets()

if not response['Buckets']:
    print('No buckets')

for bucket in response['Buckets']:
    print(bucket['Name'])