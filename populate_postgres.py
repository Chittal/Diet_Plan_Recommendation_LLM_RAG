import pandas as pd
import os

from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = 'data/food_data'
FOUNDATION_FOOD_PATH = 'foundation_food'
BRANDED_FOOD_PATH =  'branded_food'

# Database connection parameters
username = os.getenv('POSTGRES_USERNAME')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = int(os.getenv('POSTGRES_PORT'))
database = os.getenv('POSTGRES_DATABASE')

# Create a connection string
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

def combine_all_years(PATH, file_path):
    # Walk through each sub-directory and process the files
    combined_data = pd.DataFrame()

    # Traverse through folders, merging each year's data
    for root, dirs, files in os.walk(PATH):
        # Check if the current folder contains the necessary files
        print(root, dirs, files)
        if 'food.csv' in files and 'food_nutrient.csv' in files and 'nutrient.csv' in files:
            # process food_df
            food_df = pd.read_csv(os.path.join(root, 'food.csv'))
            food_df = food_df[['fdc_id', 'description', 'publication_date']]
            food_df = food_df.drop_duplicates(subset='description', keep='first')
            # process food_nutrients_df
            food_nutrients_df = pd.read_csv(os.path.join(root, 'food_nutrient.csv'))
            food_nutrients_df = food_nutrients_df[['fdc_id', 'nutrient_id', 'amount']]
            # process nutrients_df
            nutrient_df = pd.read_csv(os.path.join(root, 'nutrient.csv'))
            nutrient_df = nutrient_df[['id', 'name', 'unit_name']]
            nutrient_df = nutrient_df.rename(columns={'id': 'nutrient_id'})
            
            merged_food_nutrients = food_df.merge(food_nutrients_df, on='fdc_id', how='left')
            merged_data = merged_food_nutrients.merge(nutrient_df, on='nutrient_id', how='left')
            
            combined_data = pd.concat([combined_data, merged_data], ignore_index=True)

    # Save combined data to a single CSV file
    combined_data.to_csv(file_path, index=False)
    print(combined_data.size)
    return combined_data


def preprocess_data(foundation_df):
    foundation_df = foundation_df.drop(columns=['publication_date', 'nutrient_id'])
    foundation_df = foundation_df.rename(columns={'name': 'nutrient', 'description': 'food_name'})
    duplicates = foundation_df.duplicated()
    duplicates = foundation_df[duplicates]
    duplicates['fdc_id'].value_counts()
    foundation_df = foundation_df.drop_duplicates()
    rows_with_missing = foundation_df[foundation_df.isnull().any(axis=1)]
    print("Rows with missing values:")
    print(rows_with_missing)
    foundation_df = foundation_df.dropna()
    # duplicate_entries = foundation_df[foundation_df.duplicated(subset='food_name', keep=False)]
    # print(duplicate_entries)
    return foundation_df


def save_to_database(df, table_name):
    # Save DataFrame to a PostgreSQL table
    # food_data_df.to_sql(table_name, engine, if_exists='append', index=False)
    # Save DataFrame to PostgreSQL in chunks
    chunk_size = 10000  # Adjust based on your system's capacity

    try:
        for i in range(0, len(df), chunk_size):
            chunk = df[i:i + chunk_size]
            chunk.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Successfully saved '{str(len(df))}' million records to '{table_name}' in PostgreSQL.")
    except Exception as e:
        print("Error while saving DataFrame in chunks:", e)


# Define file path
file_path = 'data/foundation_food_data.csv'
if not os.path.exists(file_path):
    foundation_df = combine_all_years(BASE_DIR + '/' + FOUNDATION_FOOD_PATH, file_path)
else:
    foundation_df = pd.read_csv(file_path)

# preprocess data
foundation_df = preprocess_data(foundation_df)

# save data to database
save_to_database(foundation_df, 'foundation_food_nutrient')
print("DONE")
