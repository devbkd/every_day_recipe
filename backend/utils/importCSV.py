import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_params = {
    'dbname': os.getenv('POSTGRES_DB', 'django'),
    'user': os.getenv('POSTGRES_USER', 'django'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'host': os.getenv('POSTGRES_HOST', ''),
    'port': os.getenv('POSTGRES_PORT', 5432),
}

csv_file_path = Path(__file__).parent.parent / 'data' / 'ingredients.csv'

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)

    for row in csv_reader:
        query = 'INSERT INTO recipes_ingredient '
        '(name, measurement_unit) VALUES (%s, %s);'
        data = (
            row[0],
            row[1],
        )
        cursor.execute(query, data)
        conn.commit()

cursor.close()
conn.close()
