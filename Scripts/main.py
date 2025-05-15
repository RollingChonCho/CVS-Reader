"""
Lewis
v1.1
This Python project converts CSV files into a SQLite3 database. It's useful for quickly importing
spreadsheet-style data into a relational database for querying and analysis.
"""

import csv
import sqlite3
import os
import sys

UPLOAD_DIR = 'Upload-File-Here'
DB_PATH = 'table.db'

def main():
    """
    Allow a user to interact with the program
    """
    print('-' * 50)
    user_choice = int(input('Enter your choice: \n1: Print tables\n2: Create new tables\n3: Exit\n'))
    if user_choice == 1:
        print_all_tables(DB_PATH)
    elif user_choice == 2:
        process_all_files()
    elif user_choice == 3:
        print('Goodbye!')
        sys.exit()
    else:
        print('Please enter a valid choice.')
        main()

def print_all_tables(db_path):
    """
    Allow the user to print different tables that have been created
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        print("Which table would you like to print?:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}: {table[0]}")

        choice = input("Enter the table number: ")

        # Validate input
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(tables):
            print("Invalid selection.")
            return

        selected_table = tables[int(choice) - 1][0]

        # Fetch and print all rows from the selected table
        cursor.execute(f'SELECT * FROM "{selected_table}"')
        rows = cursor.fetchall()

        # Get column names
        col_names = [description[0] for description in cursor.description]

        # Print column headers
        print(f"\nContents of table '{selected_table}':")
        print(", ".join(col_names))

        # Print each row
        for row in rows:
            print(", ".join(str(item) for item in row))

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        main()

def process_all_files():
    """
    Proces each file within the Upload-File-Here directory to call the create_table_from_CSV function
    """
    if not os.path.exists(UPLOAD_DIR):
        print(f'No such directory: {UPLOAD_DIR}')
        return

    db_connection = sqlite3.connect(DB_PATH)

    # Collect directory, table name, and call create_table_from_CSV
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.csv'):
                file_path = os.path.join(UPLOAD_DIR, filename)
                table_name = os.path.splitext(filename)[0].replace('-', '_').replace(' ', '_')
                create_table_from_CSV(file_path, table_name, db_connection)

        db_connection.commit()
        print("All CSV files processed and imported into the database.")
    finally:
        db_connection.close()
        main()

def create_table_from_CSV(file_path, table_name, db_connection):
    """
    Create a table from a CSV file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            columns = [clean_column_name(col) for col in reader.fieldnames]

            cursor = db_connection.cursor()

            # Create table dynamically
            create_sql_table = f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                {', '.join([f'"{col}" TEXT' for col in columns])}
            )
            '''
            cursor.execute(create_sql_table)

            # Insert rows
            insert_rows = f'''
            INSERT INTO "{table_name}" ({', '.join([f'"{col}"' for col in columns])})
            VALUES ({', '.join(['?' for _ in columns])})
            '''

            for row in reader:
                values = [row[col] for col in reader.fieldnames]
                cursor.execute(insert_rows, values)

            print(f"Table '{table_name}' created from {os.path.basename(file_path)}")

    except Exception as error:
        print(f"Error processing {file_path}: {error}")

def clean_column_name(name):
    return name.strip().replace(' ', '_').replace('-', '_').lower()

if __name__ == "__main__":
    main()
