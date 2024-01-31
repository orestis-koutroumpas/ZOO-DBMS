import csv
import sys
import os
import subprocess
import random
import json

subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])

from faker import Faker
from faker.providers import BaseProvider
from datetime import datetime, timedelta, time
from tkinter import messagebox

time_obj = time(14, 0)

# Creates .csv files with fake data for every table of the database
class Populate:
    def __init__(self):
        # Path for saving all the files in a folder named Fake_Data
        self.datapath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Fake_Data")
        if not os.path.exists(self.datapath):
            os.makedirs(self.datapath)
        self.fake = Faker('el_GR') # Create a Faker object for Greek
        self.fake.add_provider(Provider)
        
        self.num_of_animals = 1000
        self.num_of_purchases = 600
        self.num_of_employees = 50
        self.num_of_exhibits = 0
        self.num_of_medical_cases = 1500
        self.num_of_foods = 0
    
    # Creates fake data for Animal table   
    def automate_data_creation_for_animal(self):
        file_path = os.path.join(self.datapath, 'ANIMAL.csv')   
        if os.path.exists(file_path):
            return  # Exit the function if the file exists
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)            
            for i in range(1, self.num_of_animals + 1):
                animal_id = i
                purchase_id = random.randint(1, self.num_of_purchases)
                exhibit_id, animal_class, nutrition, species, age, weight = self.fake.animal()
                name = self.fake.first_name()
                # Import Date from 2023-01-11 to 2023-01-31
                import_date = datetime.strptime('2023-01-01', '%Y-%m-%d').date() + timedelta(days=random.randint(10, 30))
            
                writer.writerow([animal_id, purchase_id, exhibit_id, animal_class,
                                nutrition, species, name, age, weight, import_date])

    # Creates fake data for Employee table      
    def automate_data_creation_for_employee(self):
        file_path = os.path.join(self.datapath, 'EMPLOYEE.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i in range(1, self.num_of_employees + 1):
                employee_id = i
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                date_of_birth = self.fake.date_of_birth(minimum_age=18, maximum_age=65)
                address = self.fake.address().replace('\n', ' ')
                # Start Date from 2023-01-01 to 2023-01-10
                start_date = datetime.strptime('2023-01-01', '%Y-%m-%d').date() + timedelta(days=random.randint(0, 9))
                # Generate a starting hour (either 08:00:00 or 16:00:00)
                starting_hour = "08:00:00" if random.choice([True, False]) else "16:00:00"
                # Generate a finishing hour (either 16:00:00 or 00:00:00)
                finishing_hour = (datetime.strptime(starting_hour, "%H:%M:%S") + timedelta(hours=8)).strftime("%H:%M:%S")
                salary = 10000 * random.randint(1, 10)

                writer.writerow([employee_id, first_name, last_name, date_of_birth,
                                address, start_date, starting_hour, finishing_hour, salary])
    
    # Creates fake data for Purchase table                  
    def automate_data_creation_for_purchase(self):
        file_path = os.path.join(self.datapath, 'PURCHASE.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i in range(1, self.num_of_purchases + 1):
                purchase_id = i
                place_of_origin = self.fake.country()
                # Purchase Date from 2023-01-01 to 2023-01-10
                purchase_date = datetime.strptime('2023-01-01', '%Y-%m-%d').date() + timedelta(days=random.randint(0, 9))          
                price = 1000 * random.randint(10, 100)
                
                writer.writerow([purchase_id, place_of_origin, purchase_date, price])

    # Creates fake data for Exhibit table      
    def automate_data_creation_for_exhibit(self):
        # Read the ANIMAL.csv file and get the species, class, and exhibit_id columns
        animals, _ = self.read_created_csv_file('ANIMAL')
        cages = list(set((animal[5], animal[3], animal[2]) for animal in animals))  # Get distinct species, their classes, and exhibit_ids

        # Map animal classes to zones
        class_to_zone = {'Θηλαστικό': 'Ζώνη A-Θηλαστικά', 'Πτηνό': 'Ζώνη B-Πτηνά', 'Ερπετό': 'Ζώνη Γ-Ερπετά'}

        file_path = os.path.join(self.datapath, 'EXHIBIT.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for cage, animal_class, exhibit_id in cages:
                employee_id = random.randint(1, self.num_of_employees)
                cage_name = cage
                zone = class_to_zone[animal_class]  # Get the corresponding zone based on the animal class
                # Generate a starting hour 09:00:00 or 15:00:00
                starting_hour = "09:00:00" if random.choice([True, False]) else "15:00:00"
                # Calculate the finishing hour exactly 7 hours later
                finishing_hour = (datetime.strptime(starting_hour, "%H:%M:%S") 
                                + timedelta(hours=7)).strftime("%H:%M:%S")
                
                writer.writerow([exhibit_id, employee_id, cage_name, zone, starting_hour, finishing_hour])
                self.num_of_exhibits+=1
        
    # Creates fake data for Vet table   
    def automate_data_creation_for_vet(self):
        file_path = os.path.join(self.datapath, 'VET.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i in range(1, self.num_of_medical_cases + 1):
                medical_case_id = i
                animal_id = random.randint(1, self.num_of_animals)
                reason = self.fake.animals_medical_reason()
                # Import Date from 2023-02-01 to now
                start_date = datetime.strptime('2023-02-01', '%Y-%m-%d').date()
                current_date = datetime.now().date()
                import_date = start_date + timedelta(days=random.randint(0, (current_date - start_date).days))                
                # Add a random duration up to 30 days to the first_date or null
                prob_of_null = 0.2
                export_date = None
                if random.random() > prob_of_null : export_date = import_date + timedelta(days=random.randint(0, 30))                        
                
                writer.writerow([medical_case_id, animal_id, reason, import_date, export_date])
       
    # Creates fake data for feeding table
    def automate_data_creation_for_food(self):
        nutrition = ['Σαρκοφαγική Δίαιτα', 'Φυτοφική Δίαιτα']
        carnivore_food = ['Ζαρκάδι', 'Κατσίκι', 'Ελάφι', 'Αγριογούρουνο', 'Λαγός', 'Έντομα', 'Μοσχάρι', 'Ψάρια', 'Βατράχια', 'Γαρίδες',
                          'Σαλιγκάρια', 'Αγριόχειρους', 'Αυγά']
        herbivore_food = ['Χόρτα', 'Βότανα', 'Τριφύλλι', 'Βρώμη', 'Κριθάρι', 'Φύλλα', 'Ανθούς', 'Βρύα', 'Βελανίδια', 'Λουλούδια', 'Φρούτα', 
                          'Καρπούς', 'Φλοιό Δέντρων', 'Μανιτάρια', 'Ρετσίνι', 'Νέκταρ', 'Μούρα']
        combinations = []
        for category in nutrition:
            if category == 'Σαρκοφαγική Δίαιτα':
                for food in carnivore_food:
                    combinations.append((food, category))
            else:
                for food in herbivore_food:
                    combinations.append((food, category))

        random.shuffle(combinations)

        file_path = os.path.join(self.datapath, 'FOOD.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for food_id, (name, category) in enumerate(combinations, start=1):
                writer.writerow([food_id, name, category])
                self.num_of_foods += 1
    
    # Creates fake data for feeding table         
    def automate_data_creation_for_feeding(self):
        file_path = os.path.join(self.datapath, 'FEEDING.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists

        # Read the ANIMAL CSV file and store the nutrition type of each animal in a dictionary
        animals, _ = self.read_created_csv_file('ANIMAL')
        animal_nutrition = {int(animal[0]): animal[4] for animal in animals}

        # Initialize the day and time
        day = datetime.strptime('2023-02-01', '%Y-%m-%d').date()
        time = datetime.combine(day, time_obj)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            max_iterations = 20*self.num_of_animals
            feeding_counts = {i: 0 for i in range(1, self.num_of_animals + 1)}  # Initialize feeding counts for each animal
            last_feeding_time = {i: None for i in range(1, self.num_of_animals + 1)}  # Initialize last feeding time for each animal
            for i in range(1, max_iterations + 1):
                feeding_id = i
                
                # Select an animal that has not been fed the maximum number of times based on its nutrition type and that was last fed at least 3 hours ago
                possible_animals = [id for id, count in feeding_counts.items() if ((animal_nutrition[id] in ['Παμφάγο', 'Σαρκοφάγο'] and count < 3) or (animal_nutrition[id] == 'Φυτοφάγο' and count < 1))]
                if not possible_animals:
                    continue  # Skip this iteration if there are no possible animals
                animal_id = random.choice(possible_animals)

                # Update the feeding count and time
                feeding_counts[animal_id] += 1
                time = datetime.combine(day, time_obj) + timedelta(hours=random.randint(1, 3))

                # If the time is beyond 21 (9 PM), reset it to 14 (2 PM) and reset the feeding counts for the new day
                if time.hour > 21:
                    time = datetime.combine(day, time_obj.replace(hour=14))
                    feeding_counts = {i: 0 for i in range(1, self.num_of_animals + 1)}
                
                # Calculate the step size representing 10% of max iterations
                step_size = max_iterations // 10
                
                # Check if current iteration is a multiple of the step size
                if i % step_size == 0:
                    # Add a day in time for each 10% of iterations
                    day += timedelta(days=1)
                    feeding_counts = {i: 0 for i in range(1, self.num_of_animals + 1)}  # Reset feeding counts for the new day
                    last_feeding_time = {i: None for i in range(1, self.num_of_animals + 1)}  # Reset last feeding time for the new day
    
                last_feeding_time[animal_id] = time  # Update the last feeding time for the selected animal
                employee_id = random.randint(1, self.num_of_employees)
                
                time_str = time.strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([feeding_id, animal_id, employee_id, time_str])

    # Creates fake data for eating table              
    def automate_data_creation_for_eating(self):
        file_path = os.path.join(self.datapath, 'EATING.csv')
        if os.path.exists(file_path):
            return  # Exit the function if the file exists

        # Read the ANIMAL and FOOD CSV files and store their data in dictionaries
        animals, _ = self.read_created_csv_file('ANIMAL')
        foods, _ = self.read_created_csv_file('FOOD')
        animal_dict = {animal[0]: animal[4] for animal in animals}
        food_dict = {food[0]: food[2] for food in foods}

        # Map nutrition types to food categories
        nutrition_to_category = {
            'Φυτοφάγο': 'Φυτοφική Δίαιτα',
            'Σαρκοφάγο': 'Σαρκοφαγική Δίαιτα',
            'Παμφάγο': None  # Can eat any food
        }

        # Create a dictionary to map nutrition to a list of suitable food ids
        nutrition_to_food_ids = {
            nutrition: [id for id, category in food_dict.items() if nutrition_to_category[nutrition] is None or category == nutrition_to_category[nutrition]]
            for nutrition in set(animal_dict.values())
        }

        # Read the FEEDING CSV file and store the animal ids in a list
        feedings, _ = self.read_created_csv_file('FEEDING')
        feeding_animal_ids = [feeding[1] for feeding in feedings]

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for i, animal_id in enumerate(feeding_animal_ids, start=1):
                eating_id = i
                nutrition = animal_dict[animal_id]

                # Choose a suitable food id based on the animal's nutrition
                suitable_food_ids = nutrition_to_food_ids[nutrition]
                food_id = random.choice(suitable_food_ids)

                amount = 100 * random.randint(5, 20)
                writer.writerow([eating_id, animal_id, food_id, amount])
                          
    # Read the created CSV File 
    def read_created_csv_file(self, table_name):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Fake_Data")
        data_file_path = os.path.join(file_path, f"{table_name}.csv")
        data = []  # Create an empty list to store the rows
        row_counter = 0 # Initialize a counter for the rows
        if not os.path.exists(data_file_path):
            self.automate_data_creation()
        try:
            with open(data_file_path, 'r', encoding="UTF-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    row_counter += 1
                    data.append(tuple(row))  # Convert the row to a tuple and append it to the list
        except Exception as e:
            messagebox.showerror("Error", f"An error occured while reading the file {data_file_path}.", {e}) 
        return data, row_counter                  
                   
    # Calls all the functions for creating .csv files
    def automate_data_creation(self):
        self.automate_data_creation_for_animal()
        self.automate_data_creation_for_exhibit()
        self.automate_data_creation_for_employee()
        self.automate_data_creation_for_purchase()
        self.automate_data_creation_for_vet()
        self.automate_data_creation_for_food()
        self.automate_data_creation_for_feeding()
        self.automate_data_creation_for_eating()
        
#########################################################################################################

# Create new providers class
class Provider(BaseProvider):       
    def animal(self):
        # Path for the dictionary
        datapath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Dictionaries")
        file_path = os.path.join(datapath, 'animals_dict.txt')
            
        # Open the text file and load the JSON data
        with open(file_path, 'r', encoding='utf8') as file:
            animals_dict = json.load(file)
        
        species = random.choice(list(animals_dict.keys()))
        animal_info = animals_dict[species]

        exhibit_id = animal_info['exhibit_id']
        nutrition = animal_info['nutrition']
        animal_class = animal_info['animal_class']
        max_age = animal_info['max_age']
        avg_weight = animal_info['avg_weight']
        
        age = random.randint(1, max_age)  
        weight = random.randint(max(1, int(avg_weight / 2)), int(avg_weight * 1.5))
        
        return (exhibit_id, animal_class, nutrition, species, age, weight)
      
    # Medical reasons for an animal being in vet
    def animals_medical_reason(self):
        reasons = ['Εμβολιασμός', 'Στείρωση', 'Μηνιαίος Έλεγχος', 'Εξέταση Αίματος', 'Καλαζάρ', 'Εξέταση Οδοντοστοιχίας', 'Λύσσα', 
                   'Κάταγμα', 'Γαστρεντερίτιδα', 'Αλλεργική Κρίση', 'Χειρουργείο', 'Πυρετός']
        
        return random.choice(reasons)