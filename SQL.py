import os
import sqlite3
import csv
import logging
from typing import List, Optional, Tuple
import time
import re
import json

from collections import OrderedDict
from tkinter import messagebox

from Populate import Populate


# Path for the dictionary
datapath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Dictionaries")
file_path = os.path.join(datapath, 'SQL_schema_dict.txt')  
# Open the text file and load the JSON data
with open(file_path, 'r', encoding='utf8') as file:
    SQL_schema_dict = json.load(file)

################################# Establishes GUI connection to the database #########################################
class SQL:
    def __init__(self):
        self.sql_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ZOO.sql")
        self.db_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ZOO.db")
        self.sql_commands = None
        self.connector = None
        self.cursor = None
        
        try:
            if not os.path.exists(self.db_file_path):
                print("\nThe database does not exist.\n")
                self.create_db()
                self.populate_db()
                self.connect()
                self.read_sql()

            else:
                self.connect()
                self.read_sql()
        except Exception as e:
            error_message = f"An error occurred: {e}\n"
            logging.error(error_message)
            messagebox.showerror("Error", error_message)
        
    # Open the connection
    def connect(self):
        try:
            self.connector = sqlite3.connect(self.db_file_path)
            self.cursor = self.connector.cursor()
            print("Connected to the database",self.db_file_path,"\n")
            return True
        except sqlite3.Error as e:
            print("Failed to connect to the database", e, "\n")
            messagebox.showerror("Connection Failure", {e}, "\n")
            return False
        
    # Commit the changes
    def commit(self):
        self.connector.commit()

    # Close the connection
    def close(self):
        try:
            self.cursor.close()
            self.connector.close()
            return True
        except Exception as e:
            print("Failed to close the database", e, "\n")
            return False
        
    # Create the database
    def create_db(self):
        try:
            print("Creating the database. . .\n")
            self.read_sql()
            self.connector = sqlite3.connect(self.db_file_path)
            self.cursor = self.connector.cursor()
            self.cursor.executescript(self.sql_commands)
        except FileNotFoundError as e:
            print(f"File {self.sql_file_path} does not exist", e, "\n")  
            exit()
        except Exception as e:
            error_message = f"An error occurred: {e}\n"
            logging.error(error_message)
    
    # Read and execute the SQL commands from the file
    def read_sql(self):
        try:
            with open(self.sql_file_path, 'r', encoding='utf-8') as f:
                self.sql_commands = f.read()
        except FileNotFoundError as e:
            print(f"File {self.sql_file_path} does not exist", e, "\n")  
            exit()
        except Exception as e:
            error_message = f"An error occurred: {e}\n"
            logging.error(error_message)
            messagebox.showerror("Error", error_message)       
        return self.sql_commands

    # Populate the database with data from the CSV files
    def populate_db(self):
        try:
            print("Populating the database. . .\n")
            # Create the .csv files for the population
            self.p = Populate()
            self.p.automate_data_creation()
            queries = SQL_queries()
            queries.create_all_queries()        
            # If not, create it and populate it with data from each CSV file
            for table_name in SQL_schema_dict:
                file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.p.datapath)
                data_file_path = os.path.join(file_path, f"{table_name}.csv")
                try:
                    with open(data_file_path, 'r', encoding="UTF-8") as f:
                        reader = csv.reader(f)
                        for row in reader:
                            placeholders = ', '.join('?' * len(row))
                            sql_command = f"INSERT OR IGNORE INTO {table_name} VALUES ({placeholders})"
                            self.cursor.execute(sql_command, row)
                            
                except FileNotFoundError as e:
                    error_message = f"The file {data_file_path} does not exist."
                    logging.error(error_message)
                    messagebox.showerror("Error", error_message)
                    continue
                except csv.Error as e:
                    error_message = f"Error reading CSV file {data_file_path}: {e}"
                    logging.error(error_message)
                    messagebox.showerror("Error", error_message)
                    continue
                except Exception as e:
                    error_message = f"An error occurred: {e}"
                    logging.error(error_message)
                    messagebox.showerror("Error", error_message)
                    continue
        except Exception as e:
            error_message = f"An error occurred: {e}"
            logging.error(error_message)
            messagebox.showerror("Error", error_message)
        self.commit()
    
    # Executes query
    def execute_query(self, sql: str, params: Optional[Tuple] = None, table: Optional[str] = None, 
                      columns: Optional[List[str]] = None) -> Optional[List[Tuple]]:
        try:
            start_time = time.time()  # Measure start time
            print(f"\nExecuting SQL command: \n{sql}") 
            self.cursor.execute(sql)
            
            # Only commit if the SQL command is not a SELECT command
            if not sql.strip().upper().startswith("SELECT"):
                self.commit()
            
            result = self.cursor.fetchall()
            end_time = time.time()  # Measure end time
            execution_time = end_time - start_time  # Calculate execution time
            print(f"Query executed in {execution_time:.10f} seconds\n")  
            return result if result else None
        except Exception as e:
            print(f"Error occurred: {e}")
            raise  # Re-raise the exception
    
    # Make a selection from a table  ### Needs improvement
    def select_from_db(self, table: str = None, columns: Optional[List[str]] = None,
                    where: Optional[str] = None, order: Optional[str] = None) -> Optional[List[Tuple]]:
        """
        Executes a SQL SELECT query on the database.

        Args:
            table (str, optional): The name of the table to select from. Defaults to None.
            columns (Optional[List[str]], optional): The list of columns to select. If None, selects all columns. Defaults to None.
            where (Optional[str], optional): The WHERE clause of the query. Defaults to None.
            order (Optional[str], optional): The ORDER BY clause of the query. Defaults to None.

        Returns:
            Optional[List[Tuple]]: The result of the query as a list of tuples, where each 
            tuple represents a row from the result set. Returns None if the query does not return any results or if an error occurs.
        """
        if table is None:
            print("Table name is required.")
            return None

        # Construct the SQL SELECT statement
        sql_select = f"SELECT {', '.join(columns) if columns else '*'} FROM {table}" 
        if where:
            sql_select += f" WHERE {where}"
        if order:
            sql_select += f" ORDER BY {order}"
        
        return self.execute_query(sql_select)
      
    # Update tables in the database
    def update_db(self, table: str = None, values: Optional[List[str]] = None, where: Optional[str] = None) -> bool:
        """
        Executes a SQL UPDATE query on the database.

        Args:
            table (str, optional): The name of the table to update. Defaults to None.
            values (Optional[List[str]], optional): The new values to set. Each value corresponds to a column in the table. Defaults to None.
            where (Optional[str], optional): The WHERE clause of the query. Defaults to None.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if table is None or values is None:
            print("Table name and values are required.")
            return False
        
        values = [value for value in values]
        # Get the schema for the table
        schema = SQL_schema_dict.get(table)
        if not schema:
            print(f"No schema found for table {table}")
            return False
        
        # Get the column names from the schema
        columns = list(schema.keys())
        
        # Construct the SET clause
        set_clause = ', '.join(f"{column}=NULL" 
                        if value is None else (f"{column}='{value}'" 
                        if isinstance(value, str) else f"{column}={value}") 
                        for column, value in zip(columns, values))

        # Construct where clause
        where = f'{list(SQL_schema_dict[table].keys())[0]} = {values[0]}'

        # Construct the SQL UPDATE statement
        sql_update = f"UPDATE {table} SET {set_clause}"
        if where:
            sql_update += f" WHERE {where}"

        # Execute the SQL UPDATE statement
        try:
            return self.execute_query(sql_update)
        except Exception as e:
            messagebox.showerror("Error executing SQL statement",{e})
            print(f"Error executing SQL statement: {e}")
            return False
            
    # Make an insertion into database 
    def insert_into_db(self, table: str = None, values: Optional[List[str]] = None) -> bool:
        """
        Executes a SQL INSERT query on the database.

        Args:
            table (str, optional): The name of the table to insert into. Defaults to None.
            values (Optional[List[str]], optional): The values to insert. Each value corresponds to a column in the table. Defaults to None.

        Returns:
            bool: True if the insert was successful, False otherwise.
        """
        if table is None or values is None:
            print("Table name and values are required.")
            return False

        # Construct the SQL INSERT statement
        columns = ', '.join(SQL_schema_dict[table].keys())
        placeholders = ', '.join(['?' for _ in values])

        # Constructing the query string with literal values for None or empty strings
        query_values = [f"'{val}'" if val is not None and val != '' else 'NULL' for val in values]
        query_string = f"INSERT INTO {table} ({columns}) VALUES ({', '.join(query_values)})"

        # Execute the SQL INSERT statement using execute_query method
        try:
            result = self.execute_query(query_string, table=table)
            return bool(result)  # Return True if query execution succeeded, False otherwise
        except Exception as e:
            print(f"Error executing SQL statement: {e}")
            return False

    # Delete from database
    def delete_from_db(self, table: Optional[str] = None, id_column: Optional[str] = None, value: Optional[str] = None) -> None:
        """
        Executes a SQL DELETE query on the database.

        Args:
            table (Optional[str], optional): The name of the table to delete from. Defaults to None.
            id_column (Optional[str], optional): The name of the ID column. Defaults to None.
            value (Optional[str], optional):  The value of the ID to delete. Defaults to None.

        Returns:
            None: This function does not return anything.
        """
        if table is None:
            print("Table name is required.")
            return

        # Construct the SQL DELETE statement
        sql_delete = f"DELETE FROM {table}"
        if id_column:
            sql_delete += f" WHERE {id_column} = '{value}'"

        try:
            # Execute the SQL DELETE statement
            return self.execute_query(sql_delete)
        except Exception as e:
            print(f"Error occurred: {e}")

    def find_default_values(self, sql_command):
        """
        Parses SQL command to find the default values for each column.

        Args:
            sql_command (str): The SQL command to parse

        Returns:
            OrderedDict: An ordered dictionary where the key is 
            the column name and the value is the default value or 'None' 
            if no default value. If the column has NOT NULL constraint, an '*' is appended to the column name.
        """
        # Cut the sql_command before the word "PRIMARY"
        sql_command = sql_command.split("PRIMARY")[0]
        # Regular expression to match column name, type, NOT NULL constraint, and optional default value
        pattern = r'"(\w+)"\s+(\w+(?:\(\d+\))?(?:\s+\w+)?)\s*(NOT NULL)?(?:\s+DEFAULT\s+(\w+|NULL|\'\w+\'))?,'
        matches = re.findall(pattern, sql_command)
        
        # If the column has NOT NULL constraint, append an * to the column name
        # Create an OrderedDict where the key is the column name and the value is a dictionary with 'type' and 'default_value'
        default_values = OrderedDict((column + ('*' if not_null else ''), {'type': type, 'default_value': default if default else None}) 
                                    for column, type, not_null, default in matches)

        return default_values


#################################### Creates SQL queries for search button ###########################################
class SQL_queries():
    
    def __init__(self):
        super().__init__()
        self.queries_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Queries")
        if not os.path.exists(self.queries_path):
            os.makedirs(self.queries_path)
            
    def create_sql_queries(self):
        file_path = os.path.join(self.queries_path, 'SQL_queries_with_select.sql')
        # Check if the file already exists
        if os.path.exists(file_path):
            return
        # If the file doesn't exist, create it and write queries to it
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write("SELECT * FROM ANIMAL;\n\n")
            f.write("SELECT * FROM EATING;\n\n")
            f.write("SELECT * FROM EMPLOYEE;\n\n")
            f.write("SELECT * FROM EXHIBIT;\n\n")
            f.write("SELECT * FROM FEEDING;\n\n")
            f.write("SELECT * FROM FOOD;\n\n")
            f.write("SELECT * FROM PURCHASE;\n\n")
            f.write("SELECT * FROM VET;\n\n")

    def create_sql_queries_with_group_by(self):
        file_path = os.path.join(self.queries_path, 'SQL_queries_with_group_by.sql')
        # Check if the file already exists
        if os.path.exists(file_path):
            return
        # If the file doesn't exist, create it and write queries to it        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write("SELECT ANIMAL.Class, COUNT(*) AS Animals_Per_Class FROM ANIMAL GROUP BY ANIMAL.Class;\n\n") 
            f.write("SELECT ANIMAL.Nutrition, COUNT(*) AS Animals_Per_Nutrition FROM ANIMAL GROUP BY ANIMAL.Nutrition;\n\n") 
            f.write("SELECT ANIMAL.Species, COUNT(*) AS Animals_Per_Species FROM ANIMAL GROUP BY ANIMAL.Species;\n\n") 
            f.write("SELECT ANIMAL.Age, COUNT(*) AS Animals_Per_Age FROM ANIMAL GROUP BY ANIMAL.Age;\n\n") 
            f.write("SELECT ANIMAL.Weight, COUNT(*) AS Animals_Per_Weight FROM ANIMAL GROUP BY ANIMAL.Weight;\n\n") 
            f.write("SELECT ANIMAL.Import_Date, COUNT(*) AS Animals_Per_Import_Date FROM ANIMAL GROUP BY ANIMAL.Import_Date;\n\n") 
            f.write("SELECT ANIMAL.Name, ANIMAL.Class, ANIMAL.Species, COUNT(*) AS Lunches_Per_Animal FROM ANIMAL LEFT OUTER JOIN EATING ON ANIMAL.Animal_ID = EATING.Animal_ID GROUP BY EATING.Animal_ID;\n\n")
            f.write("SELECT EMPLOYEE.Employee_ID, EMPLOYEE.First_Name, EMPLOYEE.Last_Name, COUNT(*) AS Animals_Fed FROM EMPLOYEE INNER JOIN FEEDING ON EMPLOYEE.Employee_ID = FEEDING.Employee_ID INNER JOIN ANIMAL ON ANIMAL.Animal_ID = FEEDING.Animal_ID GROUP BY FEEDING.Employee_ID;\n\n")
            f.write("SELECT EXHIBIT.Zone, COUNT(*) AS Animals_Per_Zone FROM EXHIBIT INNER JOIN ANIMAL ON EXHIBIT.Exhibit_ID = ANIMAL.Exhibit_ID GROUP BY EXHIBIT.Zone;\n\n")            
            f.write("SELECT FOOD.Category, COUNT(*) as Food_Per_Category FROM FOOD GROUP BY FOOD.Category;\n\n")
            f.write("SELECT FOOD.Name, FOOD.Category, COUNT(*) AS Lunches FROM FOOD INNER JOIN EATING ON FOOD.Food_ID = EATING.Food_ID GROUP BY EATING.Food_ID;\n\n")
            f.write("SELECT PURCHASE.Place_Of_Origin, COUNT(*) AS Purchases_Per_Country FROM PURCHASE GROUP BY PURCHASE.Place_Of_Origin;\n\n")
            f.write("SELECT VET.Reason, COUNT(*) AS Cases_Per_Reason FROM VET GROUP BY VET.Reason;\n\n")
            f.write("SELECT VET.Import_Date, COUNT(*) AS Cases_Per_Date FROM VET GROUP BY VET.Import_Date;\n\n")
            f.write("SELECT PURCHASE.Place_Of_Origin, COUNT(*) AS Animal_Per_Country FROM ANIMAL INNER JOIN PURCHASE ON ANIMAL.Purchase_ID = PURCHASE.Purchase_ID GROUP BY PURCHASE.Place_Of_Origin;\n\n")
            f.write("SELECT VET.Reason, COUNT(*) AS Animal_Per_Reason FROM ANIMAL INNER JOIN VET ON ANIMAL.Animal_ID = VET.Animal_ID GROUP BY VET.Reason;\n\n")
            f.write("SELECT ANIMAL.Species, ANIMAL.Name, COUNT(*) AS Cases_Per_Animal FROM ANIMAL INNER JOIN VET ON ANIMAL.Animal_ID = VET.Animal_ID GROUP BY VET.Animal_ID;\n\n")
            f.write("SELECT ANIMAL.Species, SUM(PURCHASE.Price) AS Total_Price_Per_Species FROM PURCHASE INNER JOIN ANIMAL ON ANIMAL.Purchase_ID = PURCHASE.Purchase_ID GROUP BY ANIMAL.Species;\n\n")
            
    def create_sql_queries_with_order_by(self):
            file_path = os.path.join(self.queries_path, 'SQL_queries_with_order_by.sql')
            # Check if the file already exists
            if os.path.exists(file_path):
                return
            # If the file doesn't exist, create it and write queries to it
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write("SELECT ANIMAL.Class, ANIMAL.Nutrition, ANIMAL.Species, ANIMAL.Name FROM ANIMAL ORDER BY ANIMAL.Class;\n\n")
                f.write("SELECT EMPLOYEE.First_Name, EMPLOYEE.Last_Name, EMPLOYEE.Salary, EMPLOYEE.Date_Of_Birth FROM EMPLOYEE ORDER BY EMPLOYEE.Date_Of_Birth;\n\n")
                f.write("SELECT VET.Import_Date, VET.Reason FROM VET ORDER BY VET.Import_Date;\n\n")
                f.write("SELECT ANIMAL.Class, ANIMAL.Species, ANIMAL.Name, EXHIBIT.Zone, EXHIBIT.Cage_Name FROM ANIMAL INNER JOIN EXHIBIT ON ANIMAL.Exhibit_ID = EXHIBIT.Exhibit_ID  ORDER BY EXHIBIT.Zone;\n\n")            
                f.write("SELECT Animal_ID, Time, COUNT(*) OVER (PARTITION BY Animal_ID) AS Feeding_Count FROM FEEDING ORDER BY Animal_ID;\n\n")
                f.write("SELECT Animal_ID, DATE(Time) as Date, COUNT(*) AS Feeding_Count FROM FEEDING GROUP BY Animal_ID, DATE(Time) ORDER BY Animal_ID, DATE(Time);\n\n")
                f.write("SELECT EMPLOYEE.First_Name, EMPLOYEE.Last_Name, EXHIBIT.Cage_Name, EXHIBIT.Zone FROM EMPLOYEE INNER JOIN EXHIBIT ON EMPLOYEE.Employee_ID = EXHIBIT.Employee_ID ORDER BY EMPLOYEE.Employee_ID;\n\n")
                f.write("SELECT ANIMAL.Class, ANIMAL.Species, ANIMAL.Name, PURCHASE.Place_OF_Origin, PURCHASE.Price FROM ANIMAL INNER JOIN PURCHASE ON ANIMAL.Purchase_ID = PURCHASE.Purchase_ID ORDER BY PURCHASE.Purchase_Date DESC;\n\n") 
                f.write("SELECT ANIMAL.Class, ANIMAL.Species, ANIMAL.Name, VET.Reason, VET.Import_Date, VET.Export_Date FROM ANIMAL INNER JOIN VET ON ANIMAL.Animal_ID = VET.Animal_ID ORDER BY VET.Import_Date, VET.Medical_Case_ID;\n\n") 
                f.write("SELECT ANIMAL.Species, ANIMAL.Nutrition, FOOD.Name, FOOD.Category, EATING.Amount FROM ANIMAL INNER JOIN EATING ON ANIMAL.Animal_ID = EATING.Animal_ID INNER JOIN FOOD ON EATING.Food_ID = FOOD.Food_ID ORDER BY ANIMAL.Animal_ID;\n\n")
                f.write("SELECT EMPLOYEE.First_Name, EMPLOYEE.Last_Name, ANIMAL.Species, ANIMAL.Name, FEEDING.Time FROM EMPLOYEE INNER JOIN FEEDING ON EMPLOYEE.Employee_ID = FEEDING.Employee_ID INNER JOIN ANIMAL ON FEEDING.Animal_ID = ANIMAL.Animal_ID ORDER BY ANIMAL.Animal_ID;\n\n")
    
    def create_sql_queries_with_distinct(self):
        file_path = os.path.join(self.queries_path, 'SQL_queries_with_distinct.sql')
        # Check if the file already exists
        if os.path.exists(file_path):
            return
        # If the file doesn't exist, create it and write queries to it        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write("SELECT DISTINCT Class FROM ANIMAL;\n\n")
            f.write("SELECT DISTINCT Nutrition FROM ANIMAL;\n\n")
            f.write("SELECT DISTINCT Species FROM ANIMAL;\n\n")         
            f.write("SELECT DISTINCT Zone FROM EXHIBIT;\n\n")
            f.write("SELECT DISTINCT Cage_Name FROM EXHIBIT;\n\n")
            f.write("SELECT DISTINCT Category FROM FOOD;\n\n")
            f.write("SELECT DISTINCT Reason FROM VET;\n\n")
            f.write("SELECT DISTINCT Place_Of_Origin FROM PURCHASE;\n\n")
            
    def create_sql_queries_with_aggregate(self):
        file_path = os.path.join(self.queries_path, 'SQL_queries_with_aggregate.sql')
        # Check if the file already exists
        if os.path.exists(file_path):
            return
        # If the file doesn't exist, create it and write queries to it        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write("SELECT MAX(Age) AS Max_Age, MIN(Age) AS Min_Age, AVG(Age) AS Avg_Age FROM ANIMAL;\n\n")
            f.write("SELECT MAX(Weight) AS Max_Weight, MIN(Weight) AS Min_Weight, AVG(Weight) AS Avg_Weight FROM ANIMAL;\n\n")
            f.write("SELECT MAX(Amount) AS Max_Amount, MIN(Amount) AS Min_Amount, AVG(Amount) AS Avg_Amount FROM EATING;\n\n")
            f.write("SELECT MAX(Salary) AS Max_Salary, MIN(Salary) AS Min_Salary, AVG(Salary) AS Avg_Salary FROM EMPLOYEE;\n\n")
            f.write("SELECT MAX(Price) AS Max_Price, MIN(Price) AS Min_Price, AVG(Price) AS Avg_Price FROM PURCHASE;\n\n")
    
    def create_sql_queries_with_subqueries(self):
        file_path = os.path.join(self.queries_path, 'SQL_queries_with_subqueries.sql')
        # Check if the file already exists
        if os.path.exists(file_path):
            return
        # If the file doesn't exist, create it and write queries to it        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write("SELECT COUNT(*) AS Rich_Employees, AVG(Salary) AS Average_Salary FROM EMPLOYEE WHERE Salary > (SELECT AVG(Salary) FROM EMPLOYEE);\n\n")
            f.write("SELECT COUNT(*) AS Expensive_Purchases, AVG(Price) AS Average_Price FROM PURCHASE WHERE Price > (SELECT AVG(Price) FROM PURCHASE);\n\n")
            f.write("SELECT COUNT(*) AS Old_Animals, AVG(Age) AS Average_Age FROM ANIMAL WHERE Age > (SELECT AVG(Age) FROM ANIMAL);\n\n")
            f.write("SELECT COUNT(*) AS Keepers FROM EMPLOYEE INNER JOIN EXHIBIT ON EMPLOYEE.Employee_ID = EXHIBIT.Employee_ID;\n\n")
            f.write("SELECT COUNT(*) AS Feeders FROM EMPLOYEE INNER JOIN FEEDING ON EMPLOYEE.Employee_ID = FEEDING.Employee_ID;\n\n")
    
    def create_all_queries(self):
        self.create_sql_queries()
        self.create_sql_queries_with_group_by()
        self.create_sql_queries_with_order_by()
        self.create_sql_queries_with_distinct()
        self.create_sql_queries_with_aggregate()
        self.create_sql_queries_with_subqueries()