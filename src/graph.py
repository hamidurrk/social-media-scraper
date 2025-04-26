import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "dbfiles",'ipp.db')
GRAPH_PATH = os.path.join(BASE_DIR, "data", "graphs")
conn = sqlite3.connect(DATABASE_PATH)

def show_react(table_name):
    df = pd.read_sql_query(f"SELECT datetime, all_reacts FROM {table_name}", conn)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[(df['datetime'].dt.month != 4) | (df['datetime'].dt.year != 2022)]
    z_scores = np.abs((df['all_reacts'] - df['all_reacts'].mean()) / df['all_reacts'].std())
    df = df[z_scores < 2]
    
    plt.figure(figsize=(10,6))
    plt.scatter(df['datetime'], df['all_reacts'])
    plt.xlabel('Datetime')
    plt.ylabel('All Reacts')
    plt.title('All Reacts over Time')
    plt.show()
    
def frquency_of_post_per_day(table_name):
    df = pd.read_sql_query(f"SELECT datetime, all_reacts FROM {table_name}", conn)

    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[(df['datetime'].dt.month != 4) | (df['datetime'].dt.year != 2022)]

    df['date'] = df['datetime'].dt.date

    daily_counts = df.groupby('date').size().reset_index(name='count')

    plt.figure(figsize=(10,6))
    plt.plot(daily_counts['date'], daily_counts['count'])
    plt.xlabel('Date')
    plt.ylabel('Number of Posts')
    plt.title('Frequency of Posts per Day')
    plt.xticks(rotation=90)
    plt.show()
    
def compare_frequency_of_posts(table1, table2):
    df1 = pd.read_sql_query(f"SELECT datetime FROM {table1}", conn)
    df1['datetime'] = pd.to_datetime(df1['datetime'])
    df1['date'] = df1['datetime'].dt.date
    daily_counts1 = df1.groupby('date').size().reset_index(name='count')
    daily_counts1['table'] = table1

    df2 = pd.read_sql_query(f"SELECT datetime FROM {table2}", conn)
    df2['datetime'] = pd.to_datetime(df2['datetime'])
    df2['date'] = df2['datetime'].dt.date
    daily_counts2 = df2.groupby('date').size().reset_index(name='count')
    daily_counts2['table'] = table2

    combined_df = pd.concat([daily_counts1, daily_counts2])

    plt.figure(figsize=(12, 8))
    for table, group in combined_df.groupby('table'):
        plt.plot(group['date'], group['count'], label=table)

    plt.xlabel('Date')
    plt.ylabel('Number of Posts')
    plt.title('Frequency of Posts per Day (Comparison)')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
if __name__ == "__main__":
    # show_react("bharatiyajanatapartybjp")
    # frquency_of_post_per_day("bharatiyajanatapartybjp")
    compare_frequency_of_posts("bharatiyajanatapartybjp", "indiannationalcongress")