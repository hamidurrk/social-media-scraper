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

    # Convert the datetime column to a datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[(df['datetime'].dt.month != 4) | (df['datetime'].dt.year != 2022)]

    # Extract the date from the datetime column
    df['date'] = df['datetime'].dt.date

    # Group the data by date and count the number of posts
    daily_counts = df.groupby('date').size().reset_index(name='count')

    # Plot the daily counts
    plt.figure(figsize=(10,6))
    plt.plot(daily_counts['date'], daily_counts['count'])
    plt.xlabel('Date')
    plt.ylabel('Number of Posts')
    plt.title('Frequency of Posts per Day')
    plt.xticks(rotation=90)
    plt.show()
    
if __name__ == "__main__":
    # show_react("bharatiyajanatapartybjp")
    frquency_of_post_per_day("bharatiyajanatapartybjp")