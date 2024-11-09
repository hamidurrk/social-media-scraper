import sqlite3
import os, re
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "dbfiles",'ipp.db')
conn = sqlite3.connect(DATABASE_PATH)

def create_table():
    c = conn.cursor()
    c.execute("""CREATE TABLE ipplist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                party TEXT,
                name TEXT,
                position TEXT,
                facebook TEXT,
                twitter INTEGER,
                flag INTEGER
                )""")
    conn.close()

def create_profile_table(table_name):
    table_name = ''.join(e for e in table_name if e.isalpha()).lower()
    c = conn.cursor()
    c.execute(f"""CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT,
                post_text TEXT,
                img_link TEXT,
                img_alt TEXT,
                img_tag TEXT,
                comments INTEGER,
                shares INTEGER,
                all_reacts INTEGER,
                like INTEGER,
                love INTEGER,
                care INTEGER,
                haha INTEGER,
                sad INTEGER,
                angry INTEGER
                )""")
    conn.close()
    print(f"Table {table_name} created successfully")

def insert_to_table(
    table_name, 
    datetime,
    post_text,
    img_link,
    img_alt,
    img_tag,
    comments,
    shares,
    all_reacts,
    like,
    love,
    care,
    haha,
    sad,
    angry):
    table_name = ''.join(e for e in table_name if e.isalpha()).lower()
    c = conn.cursor()
    with conn:
        c.execute(f"""INSERT INTO {table_name} (
            datetime,
            post_text,
            img_link,
            img_alt,
            img_tag,
            comments,
            shares,
            all_reacts,
            like,
            love,
            care,
            haha,
            sad,
            angry
            ) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
            )
            """, (
            datetime,
            post_text,
            img_link,
            img_alt,
            img_tag,
            comments,
            shares,
            all_reacts,
            like,
            love,
            care,
            haha,
            sad,
            angry
            ))
    print(f"Data inserted to {table_name} successfully")

def delete_all_rows(table_name):
    c = conn.cursor()
    with conn:
        c.execute(f"DELETE FROM {table_name}")
    print(f"All rows deleted from {table_name}")

def drop_table(table_name):
    c = conn.cursor()
    with conn:
        c.execute(f"DROP TABLE IF EXISTS {table_name}")
    print(f"Table {table_name} dropped successfully")

def read_table(table_name):
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    return c.fetchall()

def fetch_new_profile(column_name):
    c = conn.cursor()
    c.execute(f"SELECT {column_name} FROM ipplist WHERE flag IS NULL LIMIT 1")
    return c.fetchone()[0]

def remove_last_n_rows(table_name, n):
    c = conn.cursor()
    with conn:
        c.execute(f"DELETE FROM {table_name} WHERE id IN (SELECT id FROM {table_name} ORDER BY id DESC LIMIT {n})")
    print(f"{n} rows deleted from {table_name}")

def remove_rows_below_wordcount_threshold(table_name, wordcount_threshold):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    query = f"DELETE FROM {table_name} WHERE all_reacts < ?"
    
    try:
        c.execute(query, (wordcount_threshold,))
        conn.commit()
        print("Rows deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting rows: {e}")
    finally:
        conn.close()

def remove_rows_below_value_threshold_of_column(table_name, column_name,value_threshold):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    query = f"DELETE FROM {table_name} WHERE {column_name} < ?"
    
    try:
        c.execute(query, (value_threshold,))
        conn.commit()
        print("Rows deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting rows: {e}")
    finally:
        conn.close()

def divide_df_by_year_and_save_to_excel(df, directory, paper_name):
    folder_name = f'{paper_name}_excel'
    os.makedirs(os.path.join(directory, folder_name), exist_ok=True)
    
    unique_years = df['year'].unique()
    
    print(f'Years found: {len(unique_years)}\nYears: {unique_years}')
    
    for year in unique_years:
        year_df = df[df['year'] == year]
        
        print(f'Converting year: {year}')
        file_name = f"{paper_name}_{year}.xlsx"
        file_path = os.path.join(directory, folder_name, file_name)
        
        year_df.to_excel(file_path, index=False)

def sqlite_to_excel(database_file, table_name, sort_column):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    try:
        print("Fetching data from database...")
        cursor.execute(f'SELECT * FROM {table_name} ORDER BY {sort_column} DESC')

        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=[col[0] for col in cursor.description])
        
        df = df.drop(columns=['id'])
        
        print("Head of the data:")
        print(df.head())
        
        print("Tail of the data:")
        print(df.tail())
        
        print("DataFrame Description:")
        print(df.describe(include='all'))
        
        print("Converting to xlsx...")
        divide_df_by_year_and_save_to_excel(df, os.path.join(BASE_DIR, "files"), table_name)
        # df.to_excel(excel_file)
        
        print(f"Data from '{table_name}' table sorted by '{sort_column}' column has been successfully exported to '{os.path.join(BASE_DIR, "files")}'.")
    
    except sqlite3.Error as e:
        print("Error:", e)
    
    finally:
        cursor.close()
        conn.close()

def csv_to_sqlite(csv_file, table_name):
    c = conn
    
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, c, if_exists='replace', index=False)
    
    c.close()
    print("Data inserted to sqlite successfully")
    
def rename_column_names_to_lowercase(table_name):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute(f"ALTER TABLE {table_name} RENAME COLUMN Party TO party")
        c.execute(f"ALTER TABLE {table_name} RENAME COLUMN Name TO name")
        c.execute(f"ALTER TABLE {table_name} RENAME COLUMN Position TO position")
        c.execute(f"ALTER TABLE {table_name} RENAME COLUMN Facebook TO facebook")
        c.execute(f"ALTER TABLE {table_name} RENAME COLUMN Twitter TO twitter")
    except sqlite3.Error as e:
        print(f"Error renaming column names: {e}")
    
def add_column(table_name, column_name, column_type):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
    except sqlite3.Error as e:
        print(f"Error adding column: {e}")
    
    conn.commit()
    conn.close()

def get_last_datetime(table_name):
    c = conn.cursor()
    offset = 0
    while True:
        c.execute(f"SELECT datetime FROM {table_name} ORDER BY id DESC LIMIT 1 OFFSET {offset}")
        row = c.fetchone()
        if row[0] != '':
            print(row[0])
            return row[0]
        else:
            offset += 1
            print(offset)

def get_datetime_from_id(table_name, id):
    c = conn.cursor()
    c.execute(f"SELECT datetime FROM {table_name} WHERE id = ?", (id,))
    try:
        return c.fetchone()[0]
    except:
        return ''
            
def check_if_datetime_exists(table_name, date):
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name} WHERE datetime = ?", (date,))
    return True if c.fetchone() else False

def empty_datetime_refactor(table_name):
    c = conn.cursor()
    query = f"SELECT id FROM {table_name} WHERE datetime = ''"
    c.execute(query)
    conn.commit()
    count = 0
    for id in c.fetchall():
        id = id[0]
        prev_date = get_datetime_from_id(table_name, id - 1)
        next_date = get_datetime_from_id(table_name, id + 1)
        if prev_date != '' and next_date != '':
            c.execute(f"UPDATE {table_name} SET datetime = ? WHERE id = ?", (prev_date, id))
        else:
            if prev_date != '':
                c.execute(f"UPDATE {table_name} SET datetime = ? WHERE id = ?", (prev_date, id))
            if next_date != '':
                c.execute(f"UPDATE {table_name} SET datetime = ? WHERE id = ?", (next_date, id))
        conn.commit()
        count += 1
    print(f"{count} rows refactored successfully.")
    
def check_datetime_format(date_string):
    pattern = r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) \d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4} at \d{2}:\d{2}$"
    return bool(re.match(pattern, date_string))

def non_empty_datetime_refactor(table_name):
    c = conn.cursor()
    query = f"SELECT id, datetime FROM {table_name}"
    c.execute(query)
    conn.commit()
    count = 0
    for row in c.fetchall():
        id = row[0]
        datetime = row[1]
        if not check_datetime_format(datetime):
            datetime = datetime.split('\n').pop()
            c.execute(f"UPDATE {table_name} SET datetime = ? WHERE id = ?", (datetime, id))
            if not check_datetime_format(datetime):
                c.execute(f"UPDATE {table_name} SET datetime = '' WHERE id = ?", (id, ))
            conn.commit()
            count += 1
    print(f"{count} rows refactored successfully.")

def update_id_column(table_name):
    c = conn.cursor()
    query = f"""
        UPDATE {table_name}
        SET id = (
            SELECT COUNT(*)
            FROM {table_name} AS t
            WHERE t.id <= {table_name}.id
        );
    """
    print("Updating ID column...")
    c.execute(query)
    conn.commit()
    print("ID column updated successfully.")

def print_duplicate_rows(table_name):
    c = conn.cursor()
    query = f"""
        SELECT *
        FROM {table_name}
        GROUP BY id
        HAVING COUNT(*) > 1;
    """
    c.execute(query)
    duplicates = c.fetchall()
    for row in duplicates:
        print(row)

if __name__ == "__main__":
    # create_table()
    # drop_table("ipplist")
    # csv_to_sqlite(os.path.join(BASE_DIR, "data", "IPP_v1.csv"), "ipplist")
    # rename_column_names_to_lowercase("ipplist")
    # add_column("ipplist", "flag", "INTEGER")
    # data = fetch_new_profile("facebook")
    # print(data)
    # create_profile_table("Bharatiya Janata Party (BJP)")

    # remove_rows_below_wordcount_threshold("bharatiyajanatapartybjp", 1)
    # remove_last_n_rows("bharatiyajanatapartybjp", 1)
    # get_last_datetime("bharatiyajanatapartybjp")
    # print(check_if_datetime_exists("bharatiyajanatapartybjp", "Friday 16 June 2023 at 15:29"))
    # remove_rows_below_value_threshold_of_column("bharatiyajanatapartybjp", "all_reacts", 1)
    # empty_datetime_refactor("bharatiyajanatapartybjp")
    # non_empty_datetime_refactor("bharatiyajanatapartybjp")
    # update_id_column("bharatiyajanatapartybjp")
    print_duplicate_rows("bharatiyajanatapartybjp")