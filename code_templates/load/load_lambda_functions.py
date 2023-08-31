from dataclasses import dataclass # required for @dataclass() functionality.
from dataclasses import asdict
from csv import DictWriter
import datetime # importing datetime module.
import json
import uuid


@dataclass() #TODO: (!) Clarify if needed. (!)
class Products: # handles the managing of class 'Products' templates.
    product_id: str
    branch_location: str
    product_name : str
    product_price : float

@dataclass()    
class Orders: # handles the managing of class 'Orders' templates.
    order_id : str
    time_stamp : str
    product_id: str
    product_price: float
    order_total : float
    transaction_type : str
    
@dataclass()
class OrderProducts: # handles the managing of class 'OrderProducts' templates.
    order_id : str
    product_id : str
    product_name : str
    product_price : float
    
#TODO: Check product name, product_price, size, branch against current products database.
# If product exists, leave blank, if not generate new record with GUID.
def update_products_catalogue():
    pass

# Normalized with Products, Orders, and OrderProducts.
def normalize_data():
    pass
