from transform_lambda_functions import *
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
            data_list = list(csv.DictReader(data, fieldnames=['time_stamp', 'branch_location', 'customer_name', 'customer_order', 
                                                                'order_total', 'transaction_type','customer_pan'], delimiter=','))
            # list of dictionaries converted to list of dataclasses.
            list_of_dataclass = dictionary_to_dataclass(data_list)

            # obj.branch_location; validation.
            branch_location_list = validate_branch_location(list_of_dataclass, s3)
            
            # obj.time_stamp; validation.
            time_stamp_list = validate_time_stamp(branch_location_list)
            
            # obj.transaction_type; validation.
            transaction_type_list = validate_transaction_type(time_stamp_list)
        
            # obj.customer_orders and obj.order_total; validation.
            dataclass_order_list = split_and_validate_orders(transaction_type_list)
                
            # list of dataclasses converted to list of dictionaries for export.
            dictionary_order_list = dataclass_to_dictionary(dataclass_order_list)
            
            # Export arguments.
            load_bucket = 'ep-transform-bucket'
            filename_csv = 'test1_' + record["s3"]["object"]["key"]
            filename_json = 'test3_' + record["s3"]["object"]["key"][:-4] + '.json'
        
            # Exports csv to external bucket.
            # export_csv(dictionary_order_list, load_bucket, filename_csv, s3)
            # Exports .json to external bucket. 
            export_json(dictionary_order_list, load_bucket, filename_json, s3)
            
        return {
             'statusCode': 200,
             "body": "Operation Successful"
        }
        
    except Exception as help:
        
        # print(help)
        return {
             'statusCode': 400,
             "body": "Operation Failure"
        }
        