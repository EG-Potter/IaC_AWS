from connect_to_db import *

def create_db_tables(connection, cursor) -> True or False:
    print('create_db_tables started')
    try:

        print('...creating customers')
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT IDENTITY(1, 1) PRIMARY KEY,
                customer_name VARCHAR(250) NOT NULL
            );
          """)

        connection.commit()
        print('...committed')
        print('create_db_tables done')
        return True
    except Exception as ex:
        print(f'create_db_tables failed to generate table/s:\n{ex}')
        return False
