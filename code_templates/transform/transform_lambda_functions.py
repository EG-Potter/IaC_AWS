from dataclasses import dataclass # required for @dataclass() functionality.
from dataclasses import asdict
from csv import DictWriter
import datetime # importing datetime module.
import json
import uuid

@dataclass()
class Orders: # handles the managing of class 'Orders' templates.
    order_id : str
    time_stamp : str
    branch_location : str
    customer_order : str
    order_total : float
    transaction_type : str
    
@dataclass()
class ValidatedOrders: # handles the managing of class 'Orders' templates.
    order_id : str
    time_stamp : str
    branch_location : str
    customer_order : list
    order_total : float
    transaction_type : str
    
# dictionary_to_dataclass(); converts list of dictionaries to a list of dataclasses.
# - list_of_dictionaries; argument being converted.
# - bucket; storage files are being deployed to. 
# - filename; name of file data will be stored under. 
# - s3; connection to s3 service.
def export_csv(list_of_dictionaries : list, bucket : str, filename : str, s3):
    keys = list_of_dictionaries[0].keys()
    with open('/tmp/' + filename, 'w', newline='') as f:
        writer = DictWriter(f, keys)
        writer.writerows(list_of_dictionaries)
            
    s3.upload_file('/tmp/' + filename, bucket, filename)
    
def export_json(list_of_dictionaries : list, bucket : str, filename : str, s3):
    with open('/tmp/' + filename, 'w') as f:
        json.dump(list_of_dictionaries, f)
    
    s3.upload_file('/tmp/' + filename, bucket, filename)

# upload_path = '/tmp/' + filename + '.json'.format(uuid4())
    
# dictionary_to_dataclass(); converts list of dictionaries to a list of dataclasses.
# - dictionary_list; argument being converted.
def dictionary_to_dataclass(dictionary_list : list) -> list:
    
    list_of_dataclasses = []
    for dictionary in dictionary_list[:]:
        
            guid = str(uuid.uuid1())
            orders = Orders(order_id = guid, time_stamp = dictionary['time_stamp'], branch_location = dictionary['branch_location'], 
                            customer_order = dictionary['customer_order'], order_total = dictionary['order_total'], 
                            transaction_type = dictionary['transaction_type'])
            list_of_dataclasses.append(orders)
        
    return list_of_dataclasses
    
# dataclass_to_dictionary(); converts list of dataclasses to a list of dictionaries.
# - dataclass_list; argument being converted.
def dataclass_to_dictionary(dataclass_list : list) -> list:
    
    list_of_dictionaries = []
    for dataclass in dataclass_list[:]:
        dictionary = asdict(dataclass)
        list_of_dictionaries.append(dictionary)
        
    return list_of_dictionaries
    
# validate_branch_location(); validates whether the entered list obj.branch_location is on the registered_places_list.
# - list_objs; argument being validated.
# - s3; connection to s3 service.
def validate_branch_location(list_objs : list, s3) -> list:
    
    bucket = 'ep-sensitive-data-bucket'
    file = 'official_places_uk.txt'
    response = s3.get_object(Bucket=bucket, Key=file)
    registered_places = response["Body"].read().decode("utf-8").split("\n")

    for obj in list_objs[:]:
        
        if ' ' in obj.branch_location:
            split_branch_location = obj.branch_location.split(' ')
            if split_branch_location[0] not in registered_places:
                list_objs.remove(obj)
                
        elif obj.branch_location not in registered_places:
            list_objs.remove(obj)
            
        elif len(obj.branch_location.strip()) == 0:
            list_objs.remove(obj)
        
    return list_objs


# validate_transaction_type(); validates whether the entered list obj.transaction_type is 'CASH' or 'CARD'.
# - list_objs; list of objects being validated.
def validate_transaction_type(list_objs : list) -> list:
    
    for obj in list_objs[:]:
        if obj.transaction_type not in ['CASH', 'CARD']:
            list_objs.remove(obj)
            
    return list_objs


# validate_time_stamp(); validates whether the entered list obj.time_stamp is valid.
# - list_objs; list of objects being validated.
def validate_time_stamp(list_objs : list) -> list:
    
    for obj in list_objs[:]:
        date_format = '%d/%m/%Y %H:%M'
        try:
            datetime.datetime.strptime(obj.time_stamp, date_format)
        except ValueError:
            list_objs.remove(obj)
            
    return list_objs


# basket_price_and_total_price_matching(); compares total of all second elements within lists, against obj.order_total.
# - list_objs; list of lists being checked/totaled for validation.
# - object; object with values to have obj.order_total validated against.
def basket_price_and_total_price_matching(list_objs : list, object) -> bool:
    
    compare_total = 0
    
    for ele in list_objs[:]:
        compare_total += ele[1]
        
    if ("%.2f" % compare_total == "%.2f" % float(object.order_total)) == True: # limit to 2 decimal places.
        return True
    else:
        return False

# split_large_regular(); Separate string of 'Large' & 'Regular' and include within list.
# - order_list; orders being checked and altered.
def split_large_regular(order_list : list) -> list:
    for order in order_list:
        original_length = len(order[0])
        large_length = order[0].removeprefix('Large')
        regular_length = order[0].removeprefix('Regular')
        if original_length != len(large_length):
            order[0] = order[0].removeprefix('Large').strip()
            order.append('Large')
        elif original_length != len(regular_length):
            order[0] = order[0].removeprefix('Regular').strip()
            order.append('Regular')
    
    return order_list
            
# split_and_validate_orders(); Separate string of multiple basket items into a list, then separates item price from item name.
# - list_objs; list of objects being checked/totaled for validation.
def split_and_validate_orders(list_objs : list) -> list:
    
        for index, obj in enumerate(list_objs[:]):
            
            sorted_orders = obj.customer_order.split(', ')
            new_format = []
            
            try:
                
                for ele in sorted_orders:
                    basket = ele.rsplit('-', 1)
                    stripped_ele = basket[1].strip()
                    if stripped_ele.replace('.', '').isdigit():
                        stripped_ele = float(stripped_ele)
                            
                    basket[1] = stripped_ele
                    new_format.append(basket)
                    
                if basket_price_and_total_price_matching(new_format, obj) != True:
                    list_objs.remove(obj)
                    
                customer_orders = split_large_regular(new_format)
                    
                validatedOrders = ValidatedOrders(order_id = obj.order_id, time_stamp = obj.time_stamp, branch_location = obj.branch_location, 
                                                  customer_order = customer_orders, order_total = obj.order_total, 
                                                  transaction_type = obj.transaction_type)
                                
                list_objs[index] = validatedOrders    
            
            except Exception as help:

                # print(help)
                list_objs.remove(obj)
    
        return list_objs
        
        
    