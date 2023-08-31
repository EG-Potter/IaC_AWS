from load_lambda_functions import *
import boto3 # library used to access AWS API
import json
import csv

s3 = boto3.client('s3')

def lambda_handler(event, context):

    try:
        
        for record in event["Records"]:
            bucket = record["s3"]["bucket"]["name"]
            file = record["s3"]["object"]["key"]
            response = s3.get_object(Bucket=bucket, Key=file)
            data = response["Body"].read().decode("utf-8").split("\n")
            data_list = list(csv.DictReader(data, fieldnames=['order_id', 'time_stamp', 'branch_location', 'customer_order', 
                                                                'order_total', 'transaction_type'], delimiter=','))
            
            update_products_catalogue()
            
            # list of dictionaries converted to list of dataclasses (Products).
            
            # list of dictionaries converted to list of dataclasses (Orders).
            
            # list of dictionaries converted to list of dataclasses (Mapping).
            
        return {
             'statusCode': 200,
             'body': 'Operation Successful'
        }
        
    except Exception as help:
        
        # print(help)
        return {
             'statusCode': 400,
             'body': 'Operation Failure'
        }