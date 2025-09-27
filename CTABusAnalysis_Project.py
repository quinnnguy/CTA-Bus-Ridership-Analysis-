# MCS275
# Name: Ngoc Nguyen
# Email: nnguy20@uic.edu
# I hereby attest that I have adhered to the rules for quizzes and projects as well as UIC’s Academic Integrity standards. 
# Signed: Ngoc Nguyen 

import sqlite3
import csv
import json
import matplotlib.pyplot as plt
import math
import numpy as np

# First function
def convert():
    """ 
    Takes no input & doesn't return aything. 
    Extracts all the data from bus_data.csv and puts it all into SQLite database called bus_data.db.
    Keep all of data and headers the same.
    Answer "How much memory did the csv file take up? How much memory does the new database file take?" in comment.
    
    If bus_data.db already exists, then the function shouldn't cause an error but should instead print:
    "Can't convert: destination file already exists".
    """
    try:
        # Import csv and extract data
        with open('bus_data.csv', 'r') as f:
            dr = csv.DictReader(f)
            bus_info = [(i['route'], i['date'], i['daytype'], i['rides']) for i in dr]
        
        # Connect to SQLite
        conn = sqlite3.connect('bus_data.db') 
        cur = conn.cursor() # creating a cursor 
        
        # Create a table
        cur.execute('''CREATE TABLE bus_data (route text, date text, daytype text, rides int)''')
        
        # Insert data into table
        cur.executemany('INSERT INTO bus_data (route, date, daytype, rides ) VALUES (?, ?, ?, ?);', bus_info)
        
        # Commit to work and close connection
        conn.commit()
        cur.close()
        
    except sqlite3.OperationalError: 
        print('Can’t convert: destination file already exists')
        
    # The csv file takes up 21138786 bytes
    # The new database file takes up 52551680 bytes
    

"""
All subsequent functions below should deal directly with the converted database file bus_data.db
"""

# Second function
def route_data(route_name):
    """
    Takes as input a specified route (as a string).
    Prints 2 things: 
        - The average daily ridership for that route
        - Percentage of days for which that route is "underused" 
    
    A bus route is underused when its ridership for the given day is below 200.
    Make sure your print output is labelled and readable.
    """
    conn = sqlite3.connect('bus_data.db')
    cur = conn.cursor()
    
    avgrides_select = cur.execute('SELECT AVG(rides) FROM bus_data WHERE route = ?;', (route_name,))
    # Fetch the average daily ridership for that route
    avg_ridership = avgrides_select.fetchone()[0]
    
    underused_select = cur.execute('SELECT COUNT(*) FROM bus_data WHERE route = ? AND rides < 200;', (route_name,))
    # Fetch the underused rides & check if the route has any underused day 
    underused_fetch = underused_select.fetchone()
    if underused_fetch:
        underused_rides = underused_fetch[0]
    else:
        underused_rides = 0
        
    rides_select = cur.execute('SELECT COUNT(*) FROM bus_data WHERE route = ?;', (route_name,))
    # Fetch all the rides
    total_rides = rides_select.fetchone()[0]
                      
    # Calculate the percentage of days for which that route is underused
    underused_percent = (underused_rides/total_rides) * 100
                               
    print(f"The average daily ridership: {avg_ridership:.2f}")
    print(f"Percentage of days for which that route is underused: {underused_percent:.2f}%.")
    

# Third function
def yearly_max():
    """
    Takes no input but creates a JSON file called year_max.json
    where the keys are years 2001 to 2021
    and the value for each year is the name of the route that had the highest one-day ridership for that year.
    """  
    # Initialize dictionary to contain information, keys are years from 2001 to 2021
    max_dict = {}
    
    conn = sqlite3.connect('bus_data.db')
    cur = conn.cursor()
    
    # Find the routes that had highest one-day ridership yearly from 2001 to 2021
    for year in range(2001, 2022): 
        routemax = cur.execute('SELECT route FROM bus_data WHERE rides = (SELECT MAX(rides) FROM bus_data WHERE date LIKE ?) AND date LIKE ?;', (f'%{year}',f'%{year}'))
        routemax_fetch = routemax.fetchone()[0]
        
        max_dict[str(year)] = routemax_fetch  # Append max value to the dictionary: keys are years, values are the routes that had maximum one-day ridership
    
    # Create a JSON file and dump the dictionary into the file 
    with open('year_max.json', 'w') as json_file:
        json_file.write(json.dumps(max_dict)) 
    
# Fourth function
def my_func():
    """
    Creates one or more matplotlib graphs that shows an interesting pattern in the data. 
    
    My idea:
    - Create a line chart showing pattern of rides on Sundays or holidays in 2019 and 2020
    """
    # Initialize 2 lists, each containing the average ridership of all routes of each month in 2019 and 2020 
    list19 = []
    list20 = []

    conn = sqlite3.connect('bus_data.db')
    cur = conn.cursor()
    
    # Loop through 12 months in 2019 and 2020
    for month in range(1, 13):

        ride19 = cur.execute("SELECT AVG(rides) FROM bus_data WHERE daytype = 'U' AND date LIKE ?;", (f'%{month}%2019',))
        ride19_fetch = ride19.fetchone()[0]
        
        ride20 = cur.execute("SELECT AVG(rides) FROM bus_data WHERE daytype = 'U' AND date LIKE ?;", (f'%{month}%2020',))
        ride20_fetch = ride20.fetchone()[0]
        
        # Append to created lists and round down
        list19.append(math.floor(ride19_fetch)) 
        list20.append(math.floor(ride20_fetch))
    
    # Draw a line chart comparing the difference between rides on Sundays or holidays in 2019 and 2020
    months_19 = [month for month in range(1,13)]
    months_20 = [month for month in range(1,13)]
    
    # Plot the line chart
    plt.plot(months_19, list19, color='red', marker='o')
    plt.plot(months_20, list20, color='blue', marker='o')
    
    # Title and labels
    plt.title('Ridership between 2019 (red) and 2020 (blue)', fontsize=14)
    plt.xlabel('Months', fontsize=14)
    plt.ylabel('Average Ridership', fontsize=14)
    plt.xticks(np.arange(1,13,1)) # show 12 months 
    plt.show()
    

# Fifth function
def update():
    """
    Increases the "rides" value of each U by 15 percent, rounded down (use "floor" functiont to round down)
    Golden rule: always create a backup file before changing the database.
    
    This function must create a new database called bus_data_backup.db BEFORE updating the original database.
    Doesn't need to print or return anything
    """
    # Create a backup db
    original_conn = sqlite3.connect('bus_data.db')
    backup_conn = sqlite3.connect('bus_data_backup.db')
    
    original_cur = original_conn.cursor() 
    backup_cur = backup_conn.cursor()
    backup_cur.execute('''CREATE TABLE IF NOT EXISTS bus_data_backup (route text, date text, daytype text, rides int)''')
    
    original_select = original_cur.execute('SELECT * FROM bus_data')
    original_data = original_select.fetchall()
    
    backup_insert = backup_cur.executemany('INSERT INTO bus_data_backup (route, date, daytype, rides ) VALUES (?, ?, ?, ?);', original_data)
    backup_conn.commit()
    
    original_conn.close()
    backup_conn.close()
    
    # Update the original db
    conn = sqlite3.connect('bus_data.db')
    cur = conn.cursor()
    
    # Increase “rides” value of each "U" day by 15 percent, rounded down
    cur.execute("UPDATE bus_data SET rides = FLOOR(rides*1.15) WHERE daytype = 'U'") 

    

    