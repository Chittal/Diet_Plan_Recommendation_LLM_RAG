import os
import psycopg2

username = os.getenv('POSTGRES_USERNAME')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
database = os.getenv('POSTGRES_DATABASE')
tablename = 'food_nutrient'

def get_nutrients_data(nutrient_list):
    # Establishing the connection to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=database, 
        user=username, 
        password=password, 
        host=host
    )
    cursor = conn.cursor()

    # Convert nutrient_list to a SQL-friendly string (assuming they are column names or keywords)
    nutrients_tuple = tuple(nutrient_list)
    print(nutrients_tuple)
    
    # Query to get items with specified nutrients
    query = f"""
        SELECT food_name
        FROM {tablename}
        WHERE LOWER(nutrient) IN %s LIMIT 10;
    """
    print(query)
    
    cursor.execute(query, (nutrients_tuple,))
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(result)
    
    food_names = [food[0] for food in result]
    return food_names