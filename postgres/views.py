import os
import psycopg2

username = os.getenv('POSTGRES_USERNAME')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
database = os.getenv('POSTGRES_DATABASE')
tablename = 'foundation_food_nutrient'

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
    nutrient_list = [item + '%' for item in nutrient_list]
    limit = len(nutrient_list) * 3
    
    nutrient_tuple = ', '.join(f"'{nutrient}'" for nutrient in nutrient_list)
    # nutrients_tuple = tuple(nutrient_list)
    # print(nutrient_tuple)
    
    query = f""" 
        WITH ranked_foods AS (
            SELECT 
                DISTINCT INITCAP(food_name) AS food_name,
                nutrient,
                ROW_NUMBER() OVER (PARTITION BY nutrient ORDER BY food_name) AS rn
            FROM public.foundation_food_nutrient
            WHERE LOWER(nutrient) ILIKE ANY (ARRAY[{nutrient_tuple}])
        )
        SELECT food_name, nutrient
        FROM ranked_foods
        WHERE rn <= 3
        ORDER BY nutrient, rn
        LIMIT {str(limit)};
    """
    # print(query)
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    # print(result)
    
    food_names = [food[0] for food in result]
    return food_names