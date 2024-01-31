import os
import subprocess
import sys
import json
import re

subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "NLTK"])

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import customtkinter as ctk
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from PIL import Image
from SQL import SQL, SQL_schema_dict
from collections import OrderedDict
from ScrolledListBox import ScrolledListbox


# Check if WordNet corpus is installed; if not, download it
try:
    wordnet.ensure_loaded()
    lemmatizer = WordNetLemmatizer()
except LookupError:
    nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()

# Creates GUI
class GUI:  
    def __init__(self):
        super().__init__()
        
        # Make an Instance of the SQL
        self.sql = SQL()
        
        # Initializations in the constructor
        self.last_pressed_button = None
        self.selected_value = None
        self.update_on_entry_window_called = False
        self.height = 30
        
        self.textboxes = {}
        self.label_entry_dict = {} # Create a dictionary to store the entry widgets and their corresponding labels
        
        # Initialize windows
        self.edit_window = None
        self.entry_window = None
        self.search_window = None
        self.tabview = None
        self.current_tabview = None  # Define the attribute 
        self.sql_files_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Queries")


##################################### Widgets Initialization ###################################################################   

        # Create the main window
        self.root = ctk.CTk()
        self.width, self.height = 1000, 600
        self.root.geometry(f"{self.width}x{self.height}+400+200")
        self.switch_var = ctk.StringVar(value="off") # Initialize the mode off the switch to be off

        # set grid layout 4x4
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure((2, 3), weight=0)
        self.root.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.root.resizable(False,False)
        self.root.title('ZOO Management System')        

        # Set the path for the images
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Images")
        self.animal_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Animal_Light.png")),
                                        dark_image=Image.open(os.path.join(image_path, "Animal_Dark.png")), size=(25, 25))
        self.employee_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "employee_dark.png")),
                                        dark_image=Image.open(os.path.join(image_path, "employee_light.png")), size=(20, 20))
        self.exhibit_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "exhibit_dark.png")),
                                        dark_image=Image.open(os.path.join(image_path, "exhibit_light.png")), size=(20, 20))
        self.food_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Food_Light.png")),
                                        dark_image=Image.open(os.path.join(image_path, "Food_Dark.png")), size=(24, 24))
        self.purchase_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Purchase_Light.png")),
                                        dark_image=Image.open(os.path.join(image_path, "Purchase_Dark.png")), size=(28, 28))
        self.vet_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Vet_Light.png")),
                                        dark_image=Image.open(os.path.join(image_path, "Vet_Dark.png")), size=(24, 24))
        self.new_entry_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Add_Light.png")),
                                        dark_image=Image.open(os.path.join(image_path, "Add_Dark.png")), size=(20, 20))
        self.search_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "Search_Dark.png")),
                                        dark_image=Image.open(os.path.join(image_path, "Search_Light.png")), size=(20, 20))
        self.delete_image = ctk.CTkImage(Image.open(os.path.join(image_path, "Delete_button.png")), size=(60, 40))
        self.edit_image = ctk.CTkImage(Image.open(os.path.join(image_path, "Edit_Button.png")), size=(26, 26))

        # Create navigation frame
        self.parent_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.parent_frame.grid(row=0, column=0, rowspan=7, sticky="nsew")
        self.parent_frame.grid_rowconfigure(9, weight=1)
        
        # Create table frame
        self.table_frame = ctk.CTkFrame(self.root, corner_radius=20)
        self.table_frame.grid(row=0, column=2, rowspan=7, sticky="nsew")
        
        # Create middle frame
        self.middle_frame =ctk.CTkFrame(self.root, corner_radius=20)
        self.middle_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")        

        # Create Title Label
        self.parent_frame_label = ctk.CTkLabel(self.parent_frame, text="ZOO Management System",
                                            compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.parent_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Create all the buttons in the navigation/left frame
        self.animal_button = self.create_button("Animal", 1, 0, 
                                            self.animal_image,lambda event: self.entities_button_event("ANIMAL"))
        self.eating_button = self.create_button("Eating", 2, 0, 
                                            self.food_image,lambda event: self.entities_button_event("EATING"))
        self.employee_button = self.create_button("Employee", 3, 0, 
                                            self.employee_image,lambda event: self.entities_button_event("EMPLOYEE"))
        self.exhibit_button = self.create_button("Exhibit", 4, 0, 
                                            self.exhibit_image,lambda event: self.entities_button_event("EXHIBIT"))
        self.feeding_button = self.create_button("Feeding", 5, 0, 
                                            self.food_image,lambda event: self.entities_button_event("FEEDING"))
        self.food_button = self.create_button("Food", 6, 0, 
                                            self.food_image,lambda event: self.entities_button_event("FOOD"))
        self.purchase_button = self.create_button("Purchase", 7, 0, 
                                            self.purchase_image,lambda event: self.entities_button_event("PURCHASE"))
        self.vet_button = self.create_button("Vet", 8, 0, 
                                            self.vet_image,lambda event: self.entities_button_event("VET"))
        self.search_button = self.create_button("Search", 10, 0, 
                                            self.search_image,lambda event: self.search_button_event(event))
        self.new_entry_button = self.create_button("New Entry", 11, 0, 
                                            self.new_entry_image,lambda event: self.new_entry_button_event(event))

        # Create the TextBox in the middle of the parent frame
        self.search_entry = ctk.CTkTextbox(self.middle_frame, corner_radius=20, 
                                        width=500, height = 400, fg_color="transparent",text_color=("gray10", "gray90")) 
        self.search_entry.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.search_entry.configure(state="disabled")  # Make the TextBox read-only
        
        # Create the scrolled listbox in the table/right frame
        self.scrolled_listbox = self.create_scrolled_listbox(self.table_frame, 
                                                            self.last_pressed_button, font=("Helvetica", 14))    
        self.scrolled_listbox.pack(fill="both", expand=True)
        self.scrolled_listbox.set_select_callback(self.on_scrolled_listbox_select)
        

        # Create the edit and delete buttons in the table/right frame
        self.edit_button = ctk.CTkButton(self.table_frame, corner_radius=10, height=35, width=20, text="Edit Selected",
                                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            image = self.edit_image, anchor="w", command=self.edit_button_event)
        self.edit_button.pack(side="left")
        
        self.delete_button = ctk.CTkButton(self.table_frame, corner_radius=10, height=25, width=30, text="",
                                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            image = self.delete_image, anchor="center", command=self.delete)
        self.delete_button.pack(side="right")

        # Create the appearance mode menu
        self.appearance_mode_label = ctk.CTkLabel(self.root, text="Appearance Mode:", anchor="center")
        self.appearance_mode_label.place(relx = 0.3, rely = 0.87)
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.root, values=["Light", "Dark", "System"],
                                                    command=self.change_appearance_mode)
        self.appearance_mode_menu.place(relx = 0.29, rely = 0.92)
        self.appearance_mode_menu.set("System")
        
        # Create the scaling menu
        self.scaling_label = ctk.CTkLabel(self.root, text="UI Scaling:", anchor="center")
        self.scaling_label.place(relx = 0.63, rely = 0.87)
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.root, values=["80%", "90%", "100%", "110%"],
                                                    command=self.change_scaling_event)
        self.scaling_optionemenu.place(relx = 0.60, rely = 0.92)
        self.scaling_optionemenu.set("100%")

        # Set focus to the widgets
        self.root.focus_set()

        # Bind the Escape key to the on_closing method
        self.root.bind("<Escape>", lambda event: self.on_closing(event))
        
        # Close the window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
        # Create a dictionary mapping button names to buttons and table columns
        self.button_table_map = {
            "ANIMAL": {"button": self.animal_button, "column": "Animal_ID"},
            "EATING": {"button": self.eating_button, "column": "Eating_ID"},
            "EMPLOYEE": {"button": self.employee_button, "column": "Employee_ID"},
            "EXHIBIT": {"button": self.exhibit_button, "column": "Exhibit_ID"},
            "FEEDING": {"button": self.feeding_button, "column": "Feeding_ID"},
            "FOOD": {"button": self.food_button, "column": "Food_ID"},
            "PURCHASE": {"button": self.purchase_button, "column": "Purchase_ID"},
            "VET": {"button": self.vet_button, "column": "Medical_Case_ID"}
        }
        self.table_names = list(self.button_table_map.keys())

################################################################################################################################       
###################################### Functions for the widgets ###############################################################
################################################################################################################################       

#################### Functions for the left/navigation frame ###################################################################

    # Creates button for the parent/left frame
    def create_button(self, name, row_number, column_number, image, command=None):
        """
        Creates a button with the specified properties and adds it to the parent frame.

        Args:
            name (str): The text to display on the button.
            row_number (int): The row number where the button should be placed in the grid.
            column_number (int): The column number where the button should be placed in the grid.
            image: The image to display on the button.
            command (Callable, optional): The function to call when the button is clicked. Defaults to None.

        Returns:
            ctk.CTkButton: The created button.
        """
        button = ctk.CTkButton(
        self.parent_frame,
        corner_radius=10,
        height=40,
        border_spacing=10,
        text=name,
        fg_color="transparent",
        text_color=("gray10", "gray90"),
        hover_color=("gray70", "gray30"),
        image=image,
        anchor="w" if command else "center"
        )
        button.grid(row=row_number, column=column_number, sticky="ew")
        if command:
           button.bind("<Button-1>", command)
        return button
    
    # Displays the keys of the entity selected in the scrollbox
    def entities_button_event(self, button_name):
        """
        Handles the event when an entity button is clicked. It enables the scrolled listbox if it exists, resets the selected value, 
        updates the last pressed button, selects the table ID by name, updates the scrolled listbox, and resets the search entry.

        Args:
            button_name (str): The name of the button that was clicked.
        """
        if self.scrolled_listbox and self.scrolled_listbox.listbox.winfo_exists():
            self.scrolled_listbox.enable()
        self.selected_value = None # Reset the older values
        self.last_pressed_button = button_name.upper()
        listvariable = self.select_table_id_by_name(button_name)
        self.update_listbox(listbox=self.scrolled_listbox, listvariable=listvariable)
        self.search_entry.configure(state='normal')
        self.search_entry.delete(1.0, 'end')
        self.search_entry.configure(state='disabled')
    
#################### Functions for search button ###############################################################################

    # Create the method that is responsible for creating the search window
    def search_button_event(self, event=None):
        """
        Handles the event when the search button is clicked. It clears the widgets input, disables the scrolled listbox, 
        creates a new top-level window for search, configures the window properties, creates a tab view in the window, 
        and adds a tab for each table in the button-table map.
        Args:
            event (optional): The event information. Defaults to None.
        """
        self.clear_widgets_input([self.parent_frame, self.middle_frame, self.table_frame])
        self.scrolled_listbox.disable()
        self.search_window = ctk.CTkToplevel(self.root)
        width, height = 600, 600
        self.search_window.geometry(f"{width}x{height}+600+200")
        self.search_window.resizable(False, False)
        self.search_window.title("Search Window")
        self.search_window.grid_rowconfigure(0, weight=1)
        self.search_window.grid_columnconfigure(2, weight=1)
        self.search_window.focus_force()
        self.search_window.grab_set() # Make the current window the only clickable one
        self.tabview = ctk.CTkTabview(self.search_window)
        self.tabview.grid(row=0, column=2, sticky="nsew")
        for table_name in self.button_table_map:
            self.tabview.add(table_name)
            self.create_tabview(self.tabview.tab(table_name), table_name)
        self.tabview.set("ANIMAL")

    # Method that handles the creation of the tabs in the search window
    def create_tabview(self, window, table_name, text=None):
        """
        Creates a tab view in the specified window for the specified table. It sets the text for the tab, 
        automates the tab view creation, binds the backwards button to the go_backwards function, and removes any warning labels.

        Args:
            window: The window in which to create the tab view.
            table_name (str): The name of the table for which to create the tab view.
            text (str, optional): The text to display in the tab. Defaults to None.
        """
        text = f"Type here to search from the {table_name} table:"
        self.automate_tabview_creation(window, table_name, text,  iter=1)
        self.backwards_button.bind("<Button-1>", lambda event: self.go_backwards(window=self.search_window))
        self.warning1_label.grid_remove() # Remove warning labels from the search window
        self.warning2_label.grid_remove()

    # Automatically create the widgets for each tab
    def automate_tabview_creation(self, window, table_name, text=None, iter=None):
        """
        Automatically creates the widgets for each tab in the tab view. It creates entry boxes, binds events to them, 
        creates a textbox for the tab, creates a switch, places the enter and backwards buttons, and returns the created widgets.

        Args:
            window: The window in which to create the tab view.
            table_name (str): The name of the table for which to create the tab view.
            text (str, optional): The text to display in the entry box. Defaults to None.
            iter (int, optional): The iteration number for entry box creation. Defaults to None.

        Returns:
            List[Widget]: The created widgets.
        """
        widgets = []
        entries,labels = self.Automate_EntryBox_creation(working_window=window, table_name=table_name, iter=iter, show_switch=False)
        self.label.place(relx=0.05, rely=0.02)
        self.entry.place(relx=0.25, rely=0.02)
        for entry in entries:
            entry.bind("<Return>", lambda event, entry=entry: self.enter_pressed_on_tabview_window(window, table_name, event))
        self.enter_button.bind("<Button-1>", lambda event: self.enter_pressed_on_tabview_window(window, table_name, event))
        self.entry1 = ctk.CTkEntry(window, width=380, corner_radius=20)
        self.entry1.place(relx=0.04, rely=0.12)
        self.entry1.bind("<Return>", lambda event: self.enter_pressed_on_tabview_window(window, table_name, event))
        self.entry1.insert(0, text)
        self.entry1.bind("<FocusIn>", lambda event, entry=self.entry1: 
            self.clear_entry_input(event=event, entry=entry))
        self.entry1.bind("<FocusOut>", lambda event, entry=self.entry1:
            self.insert_default_text_in_widget(event=event, text=text, entry=entry))
        
        self.entry1.bind("<FocusIn>", lambda event, entry=self.entry1, other_entry=self.entry: 
            self.toggle_entry_state(event=event, entry=entry, other_entry=other_entry))
        self.entry1.bind("<FocusOut>", lambda event, entry=self.entry, other_entry=self.entry1: 
            self.toggle_entry_state(event=event, entry=entry, other_entry=other_entry))

        # Create a textbox for this tab and store it in the dictionary
        self.textboxes[table_name] = ctk.CTkTextbox(window, width=580, height=320, 
                                                fg_color="transparent", 
                                                text_color=("gray10", "gray90"),
                                                wrap='none', activate_scrollbars=True)  # Disable text wrapping
        self.textboxes[table_name].place(relx=0.01, rely=0.2)
        self.textboxes[table_name].configure(state="disabled")

        # Create a switch
        self.switch = ctk.CTkSwitch(window, text="Built-in Queries", command=self.switch_event_on_tabview, 
                            variable=self.switch_var, onvalue="on", offvalue="off")
        self.switch.place(relx=0.88, rely=0.95, anchor='center')
        
        #Configure the place for Enter,Backwards Buttons
        self.enter_button.place(relx=0.65, rely=0.88, anchor='center')
        self.backwards_button.place(relx=0.32, rely=0.88, anchor='center')
        
        # Bind enter button with the whole window 
        #window.bind("<Return>", lambda event: self.enter_pressed_on_tabview_window(window, table_name, event))    ## It does not work accordingly
        widgets.extend(entries)
        widgets.append(self.entry1)
        return widgets
    
    # Function that handles the state of the switch and opens the help window
    def switch_event_on_tabview(self, event=None):
        """
        Handles the state of the switch and opens the help window. It resets the older values, stores the current tabview, 
        creates a new help window, configures the window, creates a label, a go back button, an enter button, binds events to them, 
        uploads SQL queries, creates a scrolled listbox, and toggles the switch off.

        Args:
            event (optional): The event that triggered this method. Defaults to None.
        """
        self.selected_value = None # Reset the older values
        self.current_tabview = self.tabview.get() # Store the current tabview
        self.help_window = ctk.CTkToplevel(self.root)
        width, height = 600, 300
        self.help_window.geometry(f"{width}x{height}+600+200")
        self.help_window.resizable(False, False)
        self.help_window.grid_rowconfigure((0,1,2), weight=0)
        self.help_window.grid_rowconfigure(3, weight=1)
        self.help_window.grid_columnconfigure((0,1,2,3), weight=1)
        self.help_window.title("Queries Window")
        self.help_window.focus_force()
        self.help_window.grab_set() # Make the current window the only clickable one
        help_label = ctk.CTkLabel(self.help_window, text="Choose a pre-built SQL Query to implement", font=("Courier", 14) )
        help_label.grid(row=1,column=0,columnspan=4)
        go_back_button = ctk.CTkButton(self.help_window, text="Go Back")
        go_back_button.grid(row=3, column=1)
        go_back_button.bind("<Button-1>", lambda event: self.go_backwards(self.help_window))
        enter_button = ctk.CTkButton(self.help_window, text="Enter")
        enter_button.grid(row=3, column=2)  
        enter_button.bind("<Button-1>", lambda event: self.enter_pressed_on_help_window(event))
        self.help_window.bind("<Return>", lambda event: self.enter_pressed_on_help_window(event))
        queries = self.sql_queries_upload(self.tabview.get())
        queries = list(queries.keys())
        queries_var = ctk.StringVar(value=queries)
        if queries is None:
            self.help_window.destroy()
            self.switch_var.set("off")
            return
        self.built_in_phrases = self.create_scrolled_listbox(self.help_window, queries_var, 
                                                            font=("Helvetica", 10, "italic"), width=70, height=10)
        self.built_in_phrases.set_select_callback(self.on_built_in_listbox_select)
        if self.built_in_phrases:
            self.built_in_phrases.enable()
        self.built_in_phrases.grid(row=2, column=1, columnspan=2) 
        # Toggle the switch off
        self.switch_var.set("off")
        
    # Event handler for selecting from the listbox in the help window
    def on_built_in_listbox_select(self, event=None):
        selected_phrase = self.get_selected_value_from_listbox(self.help_window,self.built_in_phrases)
        sql_queries = self.sql_queries_upload(self.tabview.get())
        sql_query = sql_queries[selected_phrase]
        return sql_query
        
    # Method that handles the event when the user presses the enter button on the help window
    def enter_pressed_on_help_window(self, event=None):
        selection = self.on_built_in_listbox_select(event) if self.built_in_phrases else None
        if selection is None:
            messagebox.showerror("Error", "No selection was made")
            return
        self.help_window.destroy()
        self.clear_widgets_input([], self.tabview.tab(self.tabview.get()))
        query = self.query_info_extraction(selection)
        data = self.sql.execute_query(selection) # Execute the query
        self.insert_table_into_textbox(textbox=self.textboxes[self.current_tabview], 
                                    columns=query["columns"], data=data)
        self.selected_value = None # Reset the older values

    # Method that handles the event when the user presses the enter button on the tab window
    def enter_pressed_on_tabview_window(self, window, table_name, event=None):
        """
        Handles the event when the enter key is pressed on the tabview window. It gets the current tabview, 
        processes the entered values, and performs different actions based on the type of the entered values.

        Args:
            window: The window in which the event occurred.
            table_name (str): The name of the table in the tabview.
            event (optional): The event that triggered this method. Defaults to None.
        """
        table_name = self.tabview.get()
        values = self.enter_pressed(window)
        self.clear_widgets_input([], self.tabview.tab(self.tabview.get()))
        
        if values is None:
            return
        else:
            for value in values:
                if value.isdigit():
                    data = self.select(table_name=table_name, where=value)
                    self.insert_text_into_textbox_generic(widget_name=self.textboxes[table_name], 
                                                            table_name=table_name, data=data, operation="select")
                elif any(char.isalpha() or char.isspace() for char in value):
                    try:
                        # Check if the value contains "drop table"
                        if "drop" in value.lower():
                            messagebox.showerror("Error", "The query contains 'DROP', which is not allowed!")
                            return
                        try:
                            # Try to execute the query
                            self.sql.execute_query(value)
                        except Exception:
                            value = value.lower()
                            value = self.custom_query("Queries", value, table_name)
                        query = self.query_info_extraction(value)
                        data = self.sql.execute_query(value)
                        self.insert_table_into_textbox(textbox=self.textboxes[self.tabview.get()],
                                                        columns=query["columns"], data=data)
                    except Exception as e:
                        messagebox.showerror("Error", {e})
                        return
                else:
                    messagebox.showerror("Error", "Invalid input!")
                    return
                
    # Execute custom sql query - Search for a match in sql files
    def custom_query(self, directory, user_input, current_tab): 
        """
        Executes a custom SQL query by searching for a match in SQL files or creating one from user input words.

        Args:
            directory (str): The directory where the SQL files are located.
            user_input (str): The user's input to be converted into a SQL query.
            current_tab (str): The current tab or context in which the query is being executed.

        Returns:
            str: The user's input if it does not match any sentence in the SQL files, otherwise None.
        """
        # Path for the dictionary
        datapath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Dictionaries")
        file_path = os.path.join(datapath, 'human_to_sql.txt')
        schema_path = os.path.join(datapath, 'SQL_schema_dict.txt')
        closest_match = None
        highest_ratio = 0
        closest_sentence = None

        # Read the human_to_sql dictionary from the text file
        with open(file_path, 'r') as file:
            human_to_sql = json.loads(file.read())

        # Read the SQL_schema_dict from the text file
        with open(schema_path, 'r') as file:
            sql_schema_dict = json.loads(file.read())

        # If user input is "find animal with id=5", replace the second word with "*"
        if ' ' in user_input:
            words = user_input.split(' ')
            if len(words) > 1 and words[1].lower() == current_tab.lower():
                words[1] = '*'
            user_input = ' '.join(words)

        # Create a new dictionary where the keys are the lemmatized and lowercased versions of the column names in sql_schema_dict, and the values are the original column names
        sql_schema_dict_lemmatized = {lemmatizer.lemmatize(column.lower().replace('_', ' ')): column for table in sql_schema_dict for column in sql_schema_dict[table]}

        # Split the user input into words, but keep the operators
        user_input_words = re.findall('\w+|[^\w\s]+', user_input.lower())

        # Replace 'id' with 'current_tab_ID' in the user input
        user_input_words = [current_tab.lower() + ' id' if word == 'id' else word for word in user_input_words]
        
        # For each word or pair of words in the user input, try to find a match in the dictionaries else delete the word
        new_user_input_words = []
        i = 0
        operators = ['=', '>', '<', '>=', '<=', '!=']  # List of operators
        while i < len(user_input_words):
            word = user_input_words[i]
            if '_' in word:  # If the word contains an underscore, lemmatize each part separately
                word = ' '.join(lemmatizer.lemmatize(part) for part in word.split('_'))
            else:
                word = lemmatizer.lemmatize(word)
            if word in sql_schema_dict_lemmatized:  # Check if the lemmatized word exists in the dictionary keys
                new_user_input_words.append(sql_schema_dict_lemmatized[word])
                i += 1
            else:
                pair = ' '.join(lemmatizer.lemmatize(word) for word in user_input_words[i:i+2]) if i < len(user_input_words) - 1 else None
                if pair and pair in sql_schema_dict_lemmatized:
                    new_user_input_words.append(sql_schema_dict_lemmatized[pair])
                    i += 2  # Skip the next word because it's part of the pair
                elif word in human_to_sql:
                    new_user_input_words.append(human_to_sql[word])
                    i += 1
                elif word in operators or (i > 0 and user_input_words[i-1] in operators) or word.isdigit():  # If the word is an operator, a value following an operator, or a numeric value
                    new_user_input_words.append(word)
                    i += 1
                else:
                    i += 1  # Skip the word if it's not in the dictionaries

        user_input_words = new_user_input_words


        user_input = ' '.join(word for word in user_input_words if word)
        user_input += " FROM " + current_tab.strip()
        
        # If 'WHERE' is in the user input, move it to the end
        if 'WHERE' in user_input:
            parts = user_input.split(' FROM ')
            subparts = parts[0].split(' WHERE ')
            user_input = ' FROM '.join([subparts[0].strip(), parts[1].strip()]) + ' WHERE ' + subparts[1].strip()
        
        return user_input
        
        
    # Method that reads sql command files and insert them in the listbox
    def sql_queries_upload(self,table_name):
        """
        Uploads SQL queries It reads the files from .sql files located in the "Queries" directory, splits the content by ';', 
        cleans the lines, extracts the query info, and if the table name matches the provided table name, it appends the query to the list.
        Args:
            table_name (str): The name of the table for which to upload the queries.

        Returns:
            List: A list of SQL queries related to the provided table name. 
            If no queries are found, it shows an error message and returns None.
        """
        sql_queries = {}
        for file in os.listdir(self.sql_files_path):
            if file.endswith(".sql"):
                with open (os.path.join(self.sql_files_path,file), "r", encoding="UTF-8") as f:
                    lines = f.read().split(';')
                    for line in lines:
                        cleaned_line = line.strip()
                        if cleaned_line:
                            query_info = self.query_info_extraction(cleaned_line)
                            if table_name in query_info["table_names"]: 
                                phrases = self.sql_to_phrases(cleaned_line)
                                for phrase in phrases:
                                    sql_queries[phrase] = cleaned_line
                                
                                
        if not sql_queries:
            messagebox.showerror("Error", "No SQL queries were found!")
            return
        return sql_queries    
    
    # Method for extracting the information of each query
    def query_info_extraction(self, selection):
        """
        Extracts information from a SQL query. It finds the table names, columns, and conditions in the query based on some conditions.

        Args:
            selection (str): The SQL query from which to extract information.

        Returns:
            dict: A dictionary containing the table names, columns, and conditions found in the query.
        """
        query_info = {}
        words = selection.split()

        # Find the table names
        query_info["table_names"] = []
        for word in words:
            if word in SQL_schema_dict.keys():
                query_info["table_names"].append(word)

        # Find the columns
        query_info["columns"] = []
        SQL_keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'AS', 'AND', 'OR', 'NOT', 'IN', 
                        'IS', 'NULL', 'LIKE', 'BETWEEN', 'EXISTS', 'ALL', 'ANY', 'SOME', 'INNER', 'LEFT', 'RIGHT', 
                        'JOIN', 'ON', 'OUTER', 'DISTINCT', 'UNION', 'INTERSECT', 'MINUS', 'EXCEPT', 'ASC', 'DESC']

        select_index = words.index('SELECT')
        from_index = words.index('FROM')

        for i in range(select_index + 1, from_index):
            word = words[i].rstrip(',')

            # Check for 'SELECT *' case
            if word == '*' or word == 'ALL':
                for table_name in query_info["table_names"]:
                    query_info["columns"].extend(list(SQL_schema_dict[table_name].keys()))
                break

            if any(word.startswith(func) for func in ['COUNT(*)', 'MAX(', 'MIN(', 'AVG(', 'SUM(', 'DATE(']):
                func_index = i
                if func_index < len(words) - 2 and words[func_index + 1].upper() == 'AS':  # Check for 'AS' clause after the function
                    query_info["columns"].append(words[func_index + 2].rstrip(','))  # Add the word after 'AS' to the columns list, removing any trailing comma
                else:
                    query_info["columns"].append(word)  # Add the function call itself as the column name
            elif '.' in word and word.upper() not in SQL_keywords:
                table_name, column_name = word.split('.', 1) 
                if table_name in SQL_schema_dict.keys() and column_name in SQL_schema_dict[table_name].keys():
                    query_info["columns"].append(column_name)  # Remove trailing comma from column name
            elif word.upper() not in SQL_keywords:
                query_info["columns"].append(word)  # Add the word to the columns list

        query_info["columns"] = list(dict.fromkeys(query_info["columns"]))
        
        
        # Find the conditions
        query_info["conditions"] = []
        operators = ['=', '>', '<', '<=', '>=']
        for i in range(len(words)):  
            for operator in operators:
                if operator in words[i]:
                    previous_word = words[i - 1]
                    next_word = words[i + 1]
                    if '.' in previous_word:
                        table_name, column_name = previous_word.split('.')
                        if table_name in SQL_schema_dict.keys() and column_name in SQL_schema_dict[table_name].keys():
                            query_info["conditions"].append(previous_word)
                            query_info["conditions"].append(operator)
                            query_info["conditions"].append(next_word)

        return query_info
    
    # Read the sql queries and turn them into regular expressions
    def sql_to_phrases(self, sql_query):
        def handle_select(query):
            parts = query.split('FROM')
            select_part = parts[0].replace('SELECT', '').strip()
            replacements = [
                ('COUNT(*)', 'count of all the lines'),
                ('*', 'all records'),
                ('MAX(', 'maximum value of '),
                ('MIN(', 'minimum value of '),
                ('AVG(', 'average value of '),
                ('SUM(', 'sum of '),
                ('DATE(', '')
            ]
            for old, new in replacements:
                select_part = select_part.replace(old, new).replace(')', '')
            select_part = ', '.join([col.split('.')[1].strip() if '.' in col else col.strip() for col in select_part.split(',')])
            from_part = parts[1].split(';')[0].strip() if len(parts) > 1 else parts
            query = f'Get {select_part} from {from_part}.'
            return query, select_part, from_part

        def handle_conditions(query, select_part, from_part):
            conditions = query.split('WHERE')[1].split(';')[0].strip()
            conditions = conditions.split('AND') if 'AND' in conditions else conditions.split('OR')
            conditions_phrases = []
            for condition in conditions:
                if 'AVG' in condition:
                    operator, operator_phrase = handle_average(condition)
                    subquery_part = condition.split(operator)[1].strip()
                    avg_column = subquery_part.split('AVG(')[1].split(')')[0]
                    condition = condition.split(operator)[0].strip() + ' ' + operator_phrase + ' ' + avg_column
                replacements = [
                    ('AND', 'and'),
                    ('=', 'is'),
                    ('>', 'greater than'),
                    ('<', 'less than')
                ]
                for old, new in replacements:
                    condition = condition.replace(old, new)
                conditions_phrases.append(condition.strip())
            conditions = ' and '.join(conditions_phrases) if 'AND' in conditions else ' or '.join(conditions_phrases)
            query = f'Get {select_part} from {from_part} where {conditions}.'
            return conditions, select_part, from_part

        def handle_average(conditions):
            operators = {
                '>': 'is greater than the average value of',
                '=': 'is equal to the average value of',
                '<': 'is less than the average value of'
            }
            for operator, operator_phrase in operators.items():
                if operator in conditions:
                    return operator, operator_phrase

        def handle_join(query, select_part, from_part):
            join_types = ['INNER JOIN', 'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN', 'NATURAL JOIN']
            join_phrases = ['joined with', 'left joined with', 'right joined with', 'full outer joined with', 'naturally joined with']
            join_parts = []
            for join_type, join_phrase in zip(join_types, join_phrases):
                while join_type in query:
                    join_index = query.index(join_type)
                    on_index = query.index('ON', join_index)
                    next_join_index = len(query)
                    for jt in join_types:
                        if jt in query[on_index:]:
                            next_join_index = min(next_join_index, query.index(jt, on_index))
                    join_part = query[join_index + len(join_type):on_index].strip()
                    on_part = query[on_index + 2:next_join_index].strip()
                    on_part = on_part.split('=')[0].strip()  # Extract the join condition
                    on_part = on_part.split('.')[1]  # Remove the table name from the join condition
                    join_parts.append(f'{join_phrase} {join_part} on condition {on_part}')
                    query = query[:join_index] + query[next_join_index:]
            from_part = from_part.split('WHERE')[0].strip() if 'WHERE' in from_part else from_part
            for join_type in join_types:  # loop over each join_type
                from_part = from_part.replace(join_type, '')  # replace each join_type individually
            from_part = from_part.replace('ON', '')
            from_part = from_part.split()[0]  # Take the first word from from_part which is the table name
            query = f'Get {select_part} from {from_part} {" ".join(join_parts)}.' if join_parts else f'Get {select_part} from {from_part}.'
            query = query.rstrip('.') + '.'
            return query, select_part, from_part

        def handle_union(query, select_part, from_part):
            union_parts = query.split('UNION')
            union_phrases = []
            for part in union_parts:
                union_phrases.append(rephrase_query(part.strip()))
            query = 'Combine the results of: ' + ' and '.join(union_phrases)
            return query, select_part, from_part
        
        def handle_group_by(query, select_part, from_part):
            group_by_part = query.split('GROUP BY')[1].split(';')[0].strip()
            group_by_part = ' '.join([col.split('.')[1].strip() if '.' in col else col.strip() for col in group_by_part.split('.')])
            from_part = from_part.split('GROUP BY')[0].strip()
            query = f'Get {select_part} from {from_part} grouped by {group_by_part}.'
            return query, select_part, from_part

        def handle_order_by(query, select_part, from_part):
            order_by_part = query.split('ORDER BY')[1].split(';')[0].strip()
            order_by_part = ' '.join([col.split('.')[1].strip() if '.' in col else col.strip() for col in order_by_part.split('.')])
            from_part = from_part.split('ORDER BY')[0].strip()
            query = f'Get {select_part} from {from_part} ordered by {order_by_part}.'
            return query, select_part, from_part

        def handle_distinct(query, select_part, from_part):
            distinct_part = select_part.replace('DISTINCT', '').strip()
            query = f'Get distinct {distinct_part} from {from_part}.'
            return query, select_part, from_part

        def handle_intersect(query, select_part, from_part):
            intersect_parts = query.split('INTERSECT')
            intersect_phrases = []
            for part in intersect_parts:
                intersect_phrases.append(rephrase_query(part.strip()))
            query = 'Get ' + ' and also get '.join(intersect_phrases)
            return query, select_part, from_part

        def handle_except(query, select_part, from_part):
            except_parts = query.split('EXCEPT')
            except_phrases = []
            for part in except_parts:
                except_phrases.append(rephrase_query(part.strip()))
            query = 'Get ' + ' but not '.join(except_phrases)
            return query, select_part, from_part

        def handle_like(query, select_part, from_part):
            like_parts = query.split('LIKE')
            like_phrases = []
            for part in like_parts:
                like_phrases.append(rephrase_query(part.strip()))
            query = 'Get ' + ' that matches the pattern '.join(like_phrases)
            return query, select_part, from_part

        def handle_between(query, select_part, from_part):
            between_parts = query.split('BETWEEN')
            between_phrases = []
            for part in between_parts:
                between_phrases.append(rephrase_query(part.strip()))
            query = 'Get ' + ' that is between '.join(between_phrases)
            return query, select_part, from_part

        def handle_partition_by(query, select_part, from_part):
            partition_by_parts = select_part.split('OVER (PARTITION BY')
            before_partition = partition_by_parts[0].strip()  # Use all the part before 'OVER (PARTITION BY'
            partition_by_phrases = []
            alias = ""
            for part in partition_by_parts[1:]:
                if 'AS' in part:
                    field, alias = part.split('AS')
                    field = field.split(')')[0].strip()
                    alias = alias.strip()
                else:
                    field = part.split(')')[0].strip()
                partition_by_phrases.append(f'for each distinct {field}')
            query = 'Get ' + before_partition + ' as ' + (alias if alias else field) + ', ' + ', '.join(partition_by_phrases)
            return query, select_part, from_part

        def handle_aggregate_functions(query, select_part, from_part):
            functions = [
                ('MAX', 'maximum value of'),
                ('MIN', 'minimum value of'),
                ('SUM', 'sum of'),
                ('COUNT', 'count of')
            ]
            for function_name, phrase in functions:
                if function_name in query:
                    part = select_part.replace(f'{function_name}(', f'{phrase} ').replace(')', '')
                    query = f'Get {part} from {from_part}.'
            return query, select_part, from_part

        def rephrase_query(query):
            handlers = [
                ('GROUP BY', handle_group_by),
                ('ORDER BY', handle_order_by),
                ('DISTINCT', handle_distinct),
                ('UNION', handle_union),
                ('INTERSECT', handle_intersect),
                ('EXCEPT', handle_except),
                ('LIKE', handle_like),
                ('BETWEEN', handle_between),
                ('OVER (PARTITION BY', handle_partition_by)
            ]

            query, select_part, from_part = handle_select(query)
            
            if any(x in query for x in ['INNER JOIN', 'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN', 'NATURAL JOIN']):
                query, select_part, from_part = handle_join(query, select_part, from_part)

            for keyword, handler in handlers:
                if keyword in query:
                    query, select_part, from_part = handler(query, select_part, from_part)

            if 'WHERE' in query:
                conditions = query.split('WHERE')[1].split(';')[0].strip()
                from_part = from_part.split('WHERE')[0].strip()
                conditions, select_part, from_part = handle_conditions(query, select_part, from_part)
                query = f'Get all records from {from_part} where {conditions}.'

            if any(x in query for x in ['MAX', 'MIN', 'SUM', 'AVG', 'COUNT']):
                query = handle_aggregate_functions(query, select_part, from_part)

            return query

        phrases = []
        lines = sql_query.split('\n')

        for line in lines:
            if line.strip() == '':
                continue
            phrases.append(rephrase_query(line))
        return phrases

    # Custom method for creating a table inside the textbox
    def insert_table_into_textbox(self, textbox, columns, data):
        """
        Inserts a table into a textbox. If the data is None, it inserts a message indicating that no matching record was found. 
        If the columns list is empty, it inserts the data into the textbox. Otherwise, it creates a table with headers and rows 
        and inserts it into the textbox.

        Args:
            textbox (crk.CTkTextbox): The textbox into which to insert the table.
            columns (list): The list of column names for the table.
            data (list): The data to be inserted into the table. Each item in the list represents a row in the table.

        Returns:
            None
        """
        
        textbox.configure(font=('Courier',12), wrap='none')
        # Temporarily set the state to "normal"
        textbox.configure(state="normal") 
        # Clear the textbox
        textbox.delete(1.0, "end")
        
        # If data is None, return immediately
        if data is None:
            textbox.insert('end', "The specific query did not find any matching record!")
            return

        # If columns is an empty list, just insert the data into the textbox
        if not columns:
            textbox.insert('end', '\n'.join(str(item[0]) for item in data) + '\n')
        else:
            # Calculate the maximum width for each column
            widths = [max(len(str(value)) for value in col) for col in zip(*data)]
            widths = [max(width, len(column)) for width, column in zip(widths, columns)]

            # Create the table header
            header = "      ".join("{:<{}}".format(header, width) for header, width in zip(columns, widths))
            textbox.insert('end', header + '\n\n')

            # Create the table rows
            for row in data:
                row_str = "      ".join("{:<{}}".format(value, width) for value, width in zip(row, widths))
                textbox.insert('end', row_str + '\n\n')
        
        
        # Disable the textbox after inserting all rows
        textbox.configure(state='disabled')

################################################################################################################################

################# Functions for New Entry button ###############################################################################

    # Event handler for selecting from the listbox in the entry window
    def on_entry_listbox_select(self, event=None):
        self.get_selected_value_from_listbox(self.entry_window, self.entry_listbox)
    
    # Method that is responsible for creating the entry window
    def new_entry_button_event(self, event=None):
        """
        Handles the event when the 'New Entry' button is clicked. It clears the widgets input, disables the scrolled listbox, 
        and opens a new entry window where the user can select a table from a listbox and either select it or go back.

        Args:
            event (optional): The event information. Defaults to None.
        """
        self.clear_widgets_input([self.parent_frame,self.middle_frame,self.table_frame])
        self.scrolled_listbox.disable()
        self.selected_value = None # Reset the older values
        self.entry_window = ctk.CTkToplevel(self.root)
        width, height = 400, 450
        self.entry_window.geometry(f"{width}x{height}+600+150")
        self.entry_window.resizable(False, False)
        self.entry_window.title("New Entry Window")  
        table_names_var = ctk.StringVar(value=self.table_names) 
        if self.table_names is None:
            self.entry_window.destroy()
            return
        self.entry_listbox = self.create_scrolled_listbox(window=self.entry_window, listvariable=table_names_var, width=35, height=3)
        self.entry_listbox.place(relx=0.27, rely=0.20)
        if self.entry_listbox:
            self.entry_listbox.enable()
        self.entry_listbox.set_select_callback(self.on_entry_listbox_select)
        self.select_button = ctk.CTkButton(self.entry_window, text="Select")
        self.select_button.place(relx=0.35, rely=0.48)
        self.select_button.bind("<Button-1>", lambda event: self.refresh(event))
        self.go_back_button = ctk.CTkButton(self.entry_window, text="Go Back")
        self.go_back_button.place(relx=0.35, rely=0.60)
        self.go_back_button.bind("<Button-1>", lambda event: self.go_backwards(self.entry_window))
        self.entry_window.focus_set()
        self.entry_window.bind("<Return>", lambda event: self.refresh(event))
        self.entry_window.grab_set() # Make the current window the only clickable one

    # Method that refreshes the window when the user clicks/presses the selection button on the entry window
    def refresh(self, event=None):
        """
        Refreshes the entry window based on the selected value in the entry listbox. If no selection was made, it shows an error message. 
        If a selection was made it clears all widgets from the window, creates new entry boxes based on the selection, and binds 
        the necessary events.

        Args:
            event (optional): The event information. Defaults to None.
        """
        selection = self.selected_value if self.entry_listbox else None
        
        if selection is None:
            messagebox.showerror("Error", "No selection was made")
            return
        # Clear all the Widgets from the window
        for widget in self.entry_window.winfo_children():
            widget.place_forget()
        
        text = "All the unfilled attributes will take their default value!"
        self.entries,widgets = self.Automate_EntryBox_creation(working_window=self.entry_window,
                                                               table_name=selection, entry_text="Default value:" ,text=text, show_switch=True)
        height = len(widgets)*self.height/12+80
        self.entry_window.geometry(f"{400}x{height}+600+150")
        self.backwards_button.bind("<Button-1>",lambda event: self.go_backwards(self.entry_window,
                                self.new_entry_button_event))
        self.enter_button.bind("<Button-1>",  self.enter_pressed_and_update_on_entry_window)
        self.entry_window.bind("<Return>", self.enter_pressed_and_update_on_entry_window)

    # Method that handles the event when the user presses the enter button on the entry window
    def enter_pressed_and_update_on_entry_window(self, event=None):
        table_name = self.selected_value
        values = self.enter_pressed(self.entry_window)
        self.selected_value = None
        if values is None:
            return
        data = [tuple(values)] 
        self.entry_window.destroy()
        self.clear_widgets_input([self.middle_frame])
        existence = self.check_existence(table=table_name, values=values, where=values[0])
        if existence:
            # If the ID exists, ask the user what they want to do
            text = " ".join(["Do you want to update the existing values, or cancel?\n",
                            "Type: Update or Cancel respectively."])
            action = ctk.CTkInputDialog(text=text, title=f"{list(SQL_schema_dict[table_name].keys())[0]} = {values[0]} exists!")
            user_input = action.get_input().lower()
            if user_input == "update":
                # Update the existing record with the new values
                self.insert_text_into_textbox_generic(widget_name=self.search_entry,
                                                table_name=table_name, 
                                                data=data, operation="update")
                self.update(table=table_name, values = values)
            else:
                # Cancel the operation
                return False
        else:
            self.insert_text_into_textbox_generic(widget_name=self.search_entry,
                                                table_name=table_name, 
                                                data=data, operation="insert")   
            self.insert(table=table_name, values = values)
        return values

################################################################################################################################

################# Functions for the right/table frame ##########################################################################

    # Method for creating scrolledlistboxes 
    def create_scrolled_listbox(self, window, listvariable, font = None, width=None, height=None):
        """
        Creates a scrolled listbox with the given parameters and sets focus to it.

        Args:
            window (ctk.CTk): The parent window for the scrolled listbox.
            listvariable (ctk.StringVar): The variable that the listbox displays.
            font (str, optional): The font to be used in the listbox. Defaults to None.
            width (int, optional): The width of the listbox. Defaults to None.
            height (int, optional): The height of the listbox. Defaults to None.

        Returns:
            ScrolledListbox: The created scrolled listbox.
        """
        fg_color = self.change_fg_color(self.change_appearance_mode)  
        listbox = ScrolledListbox(
            window,width=width, height=height, font=font, fg=fg_color, listvariable=listvariable)
        listbox.focus_set()  # Set focus to the ScrolledListbox
        return listbox

    # Method for inserting text into the textbox
    def on_scrolled_listbox_select(self, event):
        """
        Handles the event when a selection is made in the scrolled listbox. It gets the selected value from the listbox, 
        selects the corresponding data from the database, and inserts the data into the search entry textbox.

        Args:
            event (tkinter.Event): The event information.
        """
        self.get_selected_value_from_listbox(self.table_frame, self.scrolled_listbox)
        data = self.select(table_name=self.last_pressed_button, where=self.selected_value)
        self.insert_text_into_textbox_generic(widget_name=self.search_entry, 
                                            table_name=self.last_pressed_button, 
                                            data=data, operation="select")

    # Method for updating the values at the listbox
    def update_listbox(self, listbox, listvariable):
        listbox.delete(0, 'end')
        listbox.listvariable(listvariable)
    
    # Custom method for extracting only the ID's of the records
    def select_table_id_by_name(self, name):
        """
        Selects and returns the IDs of the records from the table with the given name. It also configures the color of the buttons 
        in the button-table map based on whether their name matches the given name.

        Args:
            name (str): The name of the table from which to select the IDs.

        Returns:
            list: The list of IDs from the selected table.
        """
        # Loop over the dictionary and configure each button
        for button_name, data in self.button_table_map.items():
            data["button"].configure(fg_color=("gray75", "gray25") if name == button_name else "transparent")
        # display the ids of the selected table
        if name in self.button_table_map:
            Id = self.button_table_map[name]["column"]
            ID = [id[0] for id in self.select(table_name=name, columns=[Id], order=Id)]
        return ID

    # Method for getting the selected value from the listbox
    def get_selected_value_from_listbox(self, window, listbox):
        """
        Gets the selected value from the given listbox. If the listbox is destroyed, it creates a new one and gets the selected value from it.

        Args:
            window (tkinter.Tk): The parent window of the listbox.
            listbox (ScrolledListbox): The listbox from which to get the selected value.

        Returns:
            str: The selected value from the listbox, or None if no value is selected or the listbox doesn't exist.
        """
        # Check if listbox exists and is not destroyed
        if listbox is not None:
            try:
                selection = listbox.curselection()
                if selection:
                    # Store the selected value
                    self.selected_value = listbox.listbox.get(selection[0])
                return self.selected_value
            except tk.TclError:
                # Handle the case where the listbox widget has been destroyed
                listbox = self.create_scrolled_listbox(window,
                                            self.select_table_id_by_name(self.last_pressed_button.upper()))
                self.get_selected_value_from_listbox(window,listbox)
        else:
            return None

    # Method that functions as a filter for the Entrybox creation
    def filter_columns(self, default_values, iter):
        """
        Filters the given dictionary of default values based on the given iteration number. 
        It includes only the 'itered' items in the dictionary.

        Args:
            default_values (dict): The dictionary of default values to filter. The keys are column names and the values are the default values.
            iter (int): The number of items to include in the filtered dictionary.

        Returns:
            dictionary: The filtered dictionary of default values.
        """
        filtered_values = {}
        for i, (column_name, default_value) in enumerate(default_values.items()):
            if i < iter:
                filtered_values[column_name] = default_value
        return filtered_values

    # Method for creating and inserting the labels and the entry boxes in the windows automatically
    def Automate_EntryBox_creation(self, working_window, table_name, entry_text=None, text=None, iter=None, show_switch=True):
        """
        Automates the creation of EntryBox widgets in the given window for each column in the given table. 
        If 'iter' is provided, only the 'itered' columns are considered.

        Args:
            working_window (ctk.CTk): The window in which to create the EntryBox widgets.
            table_name (str): The name of the table whose columns should be used to create the EntryBox widgets.
            iter (int, optional): The number of columns to consider. If None, all columns are considered. Defaults to None.

        Returns:
            list: A list of the created EntryBox widgets and other widgets like labels and buttons.
        """
        default_values = self.sql_command(table_name)
        widgets = [] 
        entry_widgets = []
        if iter is not None:
            default_values = self.filter_columns(default_values,iter)    
        for column_name, column_info in default_values.items():
            default_value = column_info['default_value']
            if '*' in column_name: 
                self.label = ctk.CTkLabel(working_window, text=column_name)
                self.label.grid(row=list(default_values.keys()).index(column_name), column=0, padx=10, pady=10)
                self.entry = ctk.CTkEntry(working_window, corner_radius=20)
                self.entry.grid(row=list(default_values.keys()).index(column_name), column=1, padx=10, pady=10)
                self.entry.insert(0, "Enter here:")
                self.entry.bind("<FocusIn>", lambda event, 
                            entry=self.entry: self.clear_entry_input(event=event, entry=entry))
                self.entry.bind("<FocusOut>", lambda event, 
                            entry=self.entry: self.insert_default_text_in_widget(event=event, text="Enter here:", entry=entry))
                self.label_entry_dict[self.entry] = self.label  # Add the entry and label to the dictionary
                entry_widgets.append(self.entry) # Append the ctk.CTkEntry widget to the list
                widgets.append(self.entry)
            if '*' not in column_name:
                self.label = ctk.CTkLabel(working_window, text=column_name)
                self.label.grid(row=list(default_values.keys()).index(column_name), column=0, padx=10, pady=10)
                self.entry = ctk.CTkEntry(working_window, corner_radius=20)
                self.entry.grid(row=list(default_values.keys()).index(column_name), column=1, padx=10, pady=10)
                insert_text = f"{entry_text} {default_value}" if working_window == self.entry_window else f"{entry_text}"

                self.entry.insert(0, insert_text)
                self.entry.bind("<FocusIn>", lambda event, entry=self.entry: self.clear_entry_input(event=event, entry=entry))
                self.entry.bind("<FocusOut>", lambda event, entry=self.entry: self.insert_default_text_in_widget(event=event, text=insert_text, entry=entry))
                self.label_entry_dict[self.entry] = self.label  # Add the entry and label to the dictionary
                entry_widgets.append(self.entry)
                widgets.append(self.entry)
        
        # Add Warning Label
        self.warning1_label = ctk.CTkLabel(working_window, font = ("Arial", 14, "bold"), 
                                    text_color="red", text="- All fields with * must be filled!")
        self.warning1_label.grid(row=len(default_values)+1, column=0, columnspan=2)
        widgets.append(self.warning1_label)
        self.warning2_label = ctk.CTkLabel(working_window, font = ("Arial", 14, "bold"), 
                                text_color="red", text=text)
        self.warning2_label.grid(row=len(default_values)+3, column=0, columnspan=2)
        widgets.append(self.warning2_label)
        # Add enter button
        self.enter_button = ctk.CTkButton(working_window,
                                    text="Enter",
                                    font=("Arial", 12),)
        # Place the enter button at the center bottom of the window
        self.enter_button.place(relx=0.7, rely=0.85, anchor='center')
        
        # Add Back Button
        self.backwards_button = ctk.CTkButton(working_window, font=("Arial", 12), text="Go Back")
        self.backwards_button.place(relx = 0.3, rely=0.85, anchor='center')
        
        # Create a switch
        column_names=[]
        for column_name, column_info in default_values.items():
            column_names.append(column_name)
        if show_switch:
            self.format_switch = ctk.CTkSwitch(working_window, text="Entry Formats", command=lambda: self.format_switch_event(column_names), 
                                variable=self.switch_var, onvalue="on", offvalue="off")
            self.format_switch.place(relx=0.83, rely=0.95, anchor='center')
        
        # Bind the Escape key to the on_closing method for the temp_window
        working_window.bind("<Escape>", lambda event: self.on_closing(event))
        return entry_widgets, widgets

    def format_switch_event(self, entry_names, event=None):
        self.format_window = ctk.CTkToplevel(self.root)
        width, height = 400, 200
        self.format_window.geometry(f"{width}x{height}+600+200")
        self.format_window.resizable(False, False)
        self.format_window.grid_rowconfigure((0,1,2), weight=0)
        self.format_window.grid_rowconfigure(3, weight=1)
        self.format_window.grid_columnconfigure((0,1,2,3), weight=1)
        self.format_window.title("Entries Format Window")
        self.format_window.focus_force()
        self.format_window.grab_set() # Make the current window the only clickable one
        self.format_window.lift()  # Raise this window above all others
        date_label = ctk.CTkLabel(self.format_window, font = ("Courier", 12), 
                                    text="Date Format:")
        date_label.place(relx=0.1, rely=0.12)
        date_format_label = ctk.CTkLabel(self.format_window, font = ("Arial", 12, "bold"), 
                                    text="YYYY-MM-DD")
        date_format_label.place(relx=0.34 + len("Date Format:") * 0.01, rely=0.12) 
        time_label = ctk.CTkLabel(self.format_window, font = ("Courier", 12), 
                                    text="Hour Format:")
        time_label.place(relx=0.1, rely=0.32)
        time_format_label = ctk.CTkLabel(self.format_window, font = ("Arial", 12, "bold"), 
                                    text="HH-MM-SS")
        time_format_label.place(relx=0.34 + len("Hour Format:") * 0.01, rely=0.32) 
        for entry_name in entry_names:
            if entry_name=='Time':
                datetime_label = ctk.CTkLabel(self.format_window, font = ("Courier", 12), 
                                        text="Datetime Format:")
                datetime_label.place(relx=0.1, rely=0.52)
                datetime_format_label = ctk.CTkLabel(self.format_window, font = ("Arial", 12, "bold"), 
                                    text="YYYY-MM-DD HH-MM-SS")
                datetime_format_label.place(relx=0.32 + len("Datetime Format:") * 0.01, rely=0.52) 
        back_button = ctk.CTkButton(self.format_window, font=("Arial", 12), text="Go Back")
        back_button.place(relx=0.51, rely=0.74, anchor='center')
        back_button.bind("<Button-1>", lambda event: self.go_backwards(self.format_window))
        # Toggle the switch off
        self.switch_var.set("off")


    # Method for creating the edit window
    def edit_button_event(self):
        """
        Creates a new window for editing a selected record. The window contains EntryBox widgets for each column in the table 
        associated with the last pressed button. The ID of the selected record is inserted into the first EntryBox and is not editable. 
        The "backwards" and "enter" buttons are bound to the `go_backwards` and `enter_pressed_and_update` methods, respectively. 
        The "Return" key event of the new window is also bound to the `enter_pressed_and_update` method. The new window is made modal.

        Raises:
            Error: If no selection was made in the listbox.
        """
        selection = self.get_selected_value_from_listbox(self.edit_window, self.scrolled_listbox)
        
        if selection is None:
            messagebox.showerror("Error", "No selection was made")
            return
        self.edit_window = ctk.CTkToplevel(self.root)
        width, height = 500, 500
        self.edit_window.geometry(f"{width}x{height}+580+120")
        self.edit_window.resizable(False,False)
        self.edit_window.title(f"Edit record with ID: {selection}")    
        self.edit_window.focus_force()
        text = "All the unfilled attributes will take their previous values!"
        entries,widgets = self.Automate_EntryBox_creation(working_window=self.edit_window, 
                                                          table_name=self.last_pressed_button, entry_text="Enter here:" ,text=text, show_switch=True)
        self.scrolled_listbox.unselect_current_item()
        height = len(widgets)*self.height/12+68
        self.edit_window.geometry(f"{500}x{height}+700+400")
        
        id_entry = entries[0]
        if id_entry:
            id_entry.configure(state="normal")
            id_entry.delete(0, "end")
            id_entry.insert(0, selection)
            id_entry.configure(state="disabled")
            
        self.backwards_button.bind("<Button-1>",lambda event: self.go_backwards(self.edit_window))
        self.enter_button.bind("<Button-1>", lambda event: self.enter_pressed_and_update(event))
        self.edit_window.bind("<Return>", lambda event: self.enter_pressed_and_update(event)) 
        self.edit_window.grab_set() # Make the current window the only clickable one
        
        # Add this line to handle the window close event
        self.edit_window.protocol("WM_DELETE_WINDOW", lambda: self.go_backwards(self.edit_window))
    
    # Method that handles the event when the user clicks/presses the enter button on the edit window
    def enter_pressed_and_update(self, event=None):  
        """
        Handles the event of the Enter key being pressed in the edit window. It gets the values from the EntryBox widgets in the 
        edit window, destroys the edit window, inserts the values into the search entry, and updates the database.

        Args:
            event (Event, optional): The event information. Defaults to None.

        Returns:
            None: If no values were entered in the EntryBox widgets.
        """
        values = self.enter_pressed(self.edit_window)
        self.selected_value = None 
        if values is None:
            return
        data = [tuple(values)]
        if values:
            self.edit_window.destroy()
            # Clear the textbox
            self.clear_widgets_input([self.middle_frame])
            self.insert_text_into_textbox_generic(widget_name=self.search_entry, 
                                            table_name=self.last_pressed_button, 
                                            data=data, operation="update")
            self.update(table=self.last_pressed_button, values=values)
            self.selected_value = None
        
        
################################################################################################################################

################# Functions for the middle frame ###############################################################################

    # Generic method for inserting text into the textboxes
    def insert_text_into_textbox_generic(self, widget_name, data=None, table_name=None, 
                                        operation=None,listbox_selection=None):
        """
        Inserts text into a given textbox widget. The text is either the provided listbox selection or is generated based on the 
        provided data, table name, and operation. The textbox is temporarily set to "normal" state, cleared, and then set back to 
        "disabled" state after the text is inserted.

        Args:
            widget_name (ctk.CTkTextbox): The textbox widget into which to insert the text.
            data (list, optional): The data to be processed into a string. Defaults to None.
            table_name (str, optional): The name of the table to be used in generating the text. Defaults to None.
            operation (str, optional): The operation to be used if needed in the database for generating the text. Defaults to None.
            listbox_selection (str, optional): The selected value from listbox to be inserted into the textbox. Defaults to None.

        Returns:
            None: If no operation is included.
        """
        self.clear_widgets_input([self.middle_frame])
        # Temporarily set the state to "normal"
        widget_name.configure(state="normal") 
        # Change the font style
        widget_name.configure("bold", font=("Helvetica", 14, "italic"))
        
        # If listbox_selection is not None, set text to listbox_selection
        if listbox_selection is not None:
            text = listbox_selection
        else:
            # Process the data into a string
            if operation == "insert":
                text = f"New entry in table {table_name} with the following characteristics:\n"
            elif operation == "select":
                text = f"Chosen entry from {table_name} with the following characteristics:\n"
            elif operation == "update":
                text = f"Updated entry from {table_name} with the following characteristics:\n"
            else:
                widget_name.configure(state="disabled")
                return

            if data is not None and data:
                for _ in data:
                    # Convert the tuple to a dictionary using the column names from the entity_map
                    row_dict = dict(zip(SQL_schema_dict[table_name].keys(), _))
                    for column in SQL_schema_dict[table_name]:
                        if column in row_dict:
                            text += f"{column}: {row_dict[column]}\n"
                    #text += "\n"  # Add a newline between rows 
            else:
                text += "No data found.\n"

        # Insert the text
        widget_name.insert("0.0", "Result:\n\n" + text)
        # Set the state back to "disabled"
        widget_name.configure(state="disabled")

################################################################################################################################     

################# Generic Purpose Functions for clearing or inserting in the widgets ###########################################

    # Clear box inputs
    def clear_widget(self, widget):
        if isinstance(widget, ScrolledListbox):
            widget.delete(0, ctk.END)
        if isinstance(widget, ctk.CTkTextbox):
            widget.configure(state="normal")
            widget.delete(1.0, "end")
            widget.configure(state="disabled")

    # Clear widgets input
    def clear_widgets_input(self, frames, window=None):
        if window is None:
            for frame in frames:
                for widget in frame.winfo_children():
                    self.clear_widget(widget)
        else:
            for widget in window.winfo_children():
                self.clear_widget(widget)
                
    # Clear Entry inputs
    def clear_entry_input(self, event, entry=None):
        entry.delete(0, 'end')

    # Default text in widgets
    def insert_default_text_in_widget(self, event, text, entry=None):
        if isinstance(entry, ctk.CTkEntry) and not entry.get():
            entry.insert(0, text)

    def toggle_entry_state(self, event, entry, other_entry):
        """
        Toggles the state of the other entry based on the focus state of the current entry.

        Args:
            event: The event that occurred.
            entry: The entry that is currently focused or just lost focus.
            other_entry: The other entry to enable or disable.
        """
        if entry.focus_get() == entry:
            other_entry.configure(state="disabled")
        else:
            other_entry.configure(state="normal")


################################################################################################################################           

################# Generic Purpose Functions that deal with SQL.py ##############################################################    

    # Method for select
    def select(self, table_name, columns=None, where=None, order=None):
        """
        Selects records from the specified table. If the 'where' argument is provided, it selects records that satisfy the condition.
        If the 'columns' argument is provided, it selects only the specified columns. If no records are found, it shows an error message.

        Args:
            table_name (str): The name of the table from which to select the records.
            columns (List[str], optional): The list of columns to select. If None, all columns are selected. Defaults to None.
            where (str, optional): The condition for selecting records. If None, all records are selected. Defaults to None.

        Returns:
            List[dict]: The selected records as a list of dictionaries, where each dictionary represents a record. 
            If no records are found, returns None.
        """
        if where is not None:
            where_clause = f'{self.button_table_map[table_name]["column"]} = {where}'
            data = self.sql.select_from_db(table=table_name, where=where_clause, order=order) 
            if not data:
                messagebox.showerror("Error", f"No  record with {where_clause} found!")
                return
            else:  
                return data     
        elif order is not None:
            data = self.sql.select_from_db(table=table_name, columns=columns, order=order)
            if not data:
                messagebox.showerror("Error", f"No record with {order} found!")
                return
            else:
                return data       
        elif columns is not None:
            data = self.sql.select_from_db(table=table_name, columns=columns)
            if not data:
                messagebox.showerror("Error", f"No record with {columns} found!")
                return
            else:
                return data
    
    # Method for update
    def update(self, table, values):
        """
        Updates a record in the database. The record is identified by the first value in the provided list, which is the ID. 
        The table and column for the WHERE clause of the UPDATE statement are determined based on the last pressed button.

        Args:
            values (list): The values to be used in the UPDATE statement. The first value is assumed to be the ID of the record to 
            update.
        """
        self.sql.update_db(table=table, values=values, where=values[0])
    
    # Method for insert
    def insert(self, table, values):
        """
        Inserts a new record into the database. The table into which the record is inserted is determined by the selected value.

        Args:
            values (list): The values to be inserted into the database.

        Returns:
            int: The ID of the inserted record.
        """
        self.sql.insert_into_db(table=table, values=values) 

    # Method for delete
    def delete(self):
        """
        Deletes a selected record from the database. The record is identified by the selected value in the listbox. If no value is 
        selected, an error message is displayed. After the record is deleted from the database, it is also removed from the listbox.
        """
        id_value = self.get_selected_value_from_listbox(self.table_frame, self.scrolled_listbox)
        if id_value is None:
            messagebox.showerror("Error", "No selection was made!")
            return  
        button_name = self.last_pressed_button
        table = button_name
        id_name =  self.button_table_map[button_name].get("column")
        self.sql.delete_from_db(table, id_name, id_value)
        self.scrolled_listbox.delete_selected()
        self.selected_value = None

    # Check if the ID exists in DB
    def check_existence(self, table, values, where):
        # Check if the ID exists in the database
        where = f'{list(SQL_schema_dict[table].keys())[0]} = {values[0]}'
        try:
            sql_select = self.sql.select_from_db(table, [values[0]], where)
        except Exception as e:
            messagebox.showerror("Error", {e})
            print(f"Error: {e}")
            sql_select = None

        if sql_select:
            return True
        else:
            return False

    # Method that finds the default values of each attribute in the DB
    def sql_command(self, selection): 
        """
        Finds the SQL command for creating the specified table and extracts the default values and types for the table's columns. The SQL 
        commands are split by semicolon. The default values and types are then extracted from this command and returned as an OrderedDict.

        Args:
            selection (str): The name of the table for which to find the CREATE TABLE command and extract the default values and types.

        Returns:
            OrderedDict: The default values and types for the table's columns, with the column names as keys and the default 
            values and types as values.
        """
        sql_commands = self.sql.sql_commands.split(";")
        sql_command = [command for command in sql_commands if f'CREATE TABLE IF NOT EXISTS "{selection}"' in command]
        # Join the commands back into a single string
        sql_command = ';'.join(sql_command)
        default_values_and_types = self.sql.find_default_values(sql_command)
        return default_values_and_types
        
################################################################################################################################

################# Generic Purpose Functions for enter/back buttons #############################################################         
    def enter_pressed(self, window, event=None):
        """
        Handles the event of the Enter key being pressed in a window. It resets flags, gets the entry widgets in the window, and 
        checks if the window's parent is the tabview. If it is, it handles the tabview widgets. Otherwise, it handles the
        widgets in the other window.

        Args:
            window (ctk.CTkToplevel): The window in which the Enter key was pressed.
            event (optional): The event information. Defaults to None.

        Returns:
            list: The values entered in the entry widgets. If no values were entered, raises an error.
        """
        self.reset_flags()
        entry_widgets = self.get_entry_widgets(window)
        parent_window = window._nametowidget(window.winfo_parent())

        if parent_window == self.tabview:  # Check if the window is self.tabview
            return self.handle_tabview_widgets(parent_window, entry_widgets)
        else:
            return self.handle_other_widgets(window, entry_widgets)

    # Set and reset flags to its initial values
    def reset_flags(self):
        self.all_fields_are_filled_with_valid_values = True
        self.empty_field_found = False
        self.enter_here_found = False
        self.type_here_found = False

    # Get all the entry widgets from the window
    def get_entry_widgets(self, window):
        """
        It iterates through all the widgets in the frame and if it is of type Entry it append's it to the list and calls 
        calls the update_flags_based_on_widget method, passing the widget as an argument.

        Args:
            window (ctk.CTkToplevel): The window in which the Enter key was pressed and in which the entries have been created

        Returns:
            list: The widgets that are of type ctk.CTkEntry.
        """
        entry_widgets = []
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                entry_widgets.append(widget)
                self.update_flags_based_on_widget(widget)
        return entry_widgets

    # Update the flags based on the widget
    def update_flags_based_on_widget(self, widget):
        """
        Checks the value of the provided widget. If the widget's value is empty or contains "Enter here:", it sets the 
        all_fields_are_filled_with_valid_values flag to False and sets the appropriate flag (empty_field_found or enter_here_found) 
        to True.

        Args:
            widget (ctk.CTkEntry): The widget whose value to check.
        """
        # Get the label text associated with this entry
        label_widget = self.label_entry_dict.get(widget)  # Use the dictionary to get the label widget
        if label_widget is not None:
            label_text = label_widget.cget("text")  # Get the text of the label widget
            if widget.get() == "" or "Enter here:" in widget.get() and label_text.endswith("*"):
                self.all_fields_are_filled_with_valid_values = False
                if widget.get() == "":
                    self.empty_field_found = True
                if "Enter here:" in widget.get():
                    self.enter_here_found = True


    # Handle the widgets in the tabview window
    def handle_tabview_widgets(self, parent_window, entry_widgets):
        """
        Handles the widgets in the tabview. It checks each widget's value and sets the type_here_found flag to True if the value 
        starts with "Type here to". It then checks the flags and returns the appropriate values.

        Args:
            parent_window (ctk.CTkToplevel): The parent window of the entry widgets.
            entry_widgets (list): The entry widgets to handle.

        Returns:
            list: The values entered in the entry widgets, excluding any prefix. If no values were entered or if an invalid value 
            was entered, returns None and displays an error message.
        """
        for widget in entry_widgets:
            if widget.get().startswith("Type here to"):
                self.type_here_found = True

        if self.type_here_found and not self.enter_here_found:
            return self.get_values_excluding_prefix(entry_widgets, "Type here to")
        elif not self.type_here_found and self.enter_here_found:
            return self.get_values_excluding_prefix(entry_widgets, "Enter here:")
        elif not self.type_here_found and not self.enter_here_found:
            return self.get_entry_value(parent_window, entry_widgets)
        else:
            messagebox.showerror("Error", "All fields must be filled with a valid value!")

    # Handle the widgets in the other windows
    def handle_other_widgets(self, window, entry_widgets):
        """
        Handles the widgets in a window that is not the tabview. It checks the flags and displays an error message or returns the 
        entered values as appropriate.

        Args:
            window (ctk.CTkToplevel): The window containing the entry widgets.
            entry_widgets (list): The entry widgets to handle.

        Returns:
            list: The values entered in the entry widgets. If no values were entered or if an invalid value was entered, returns 
            None and displays an error message.
        """
        if self.enter_here_found:
            messagebox.showerror("Error", "No field should contain 'Enter here:'!\n")
        elif self.empty_field_found:
            messagebox.showerror("Error", "No field should be empty!'!\n")
        elif self.all_fields_are_filled_with_valid_values:
            return self.get_entry_value(window, entry_widgets)
        else:
            messagebox.showerror("Error", "All fields must be filled with a valid value!")

    # Get the values from the entry widgets excluding the ones that start with a prefix
    def get_values_excluding_prefix(self, entry_widgets, prefix):
        """
        Iterates over the provided entry widgets and gets their values, excluding any that start with the provided prefix. It 
        checks if each value is valid and, if it is, appends it to a list. If a value is not valid, it displays an error message.

        Args:
            entry_widgets (list): The entry widgets to get values from.
            prefix (str): The prefix to exclude from the values.

        Returns:
            list: The valid values from the entry widgets, excluding any that start with the prefix.
        """
        valid_values = []
        for i, widget in enumerate(entry_widgets):
            value = widget.get()
            if not value.startswith(prefix):
                if self.is_valid_value(value, i):
                    valid_values.append(value)
                else:
                    if i == 0:
                        messagebox.showerror("Error", f"Invalid value: {value} give a numeric value!")
                    elif i == 1:
                        messagebox.showerror("Error", f"Invalid value: {value} give an alphabetic value!")
                    else:   
                        messagebox.showerror("Error", f"Invalid value: {value} give a value!")
        return valid_values

    # Check if a value is valid
    def is_valid_value(self, value, widget_index):
        """
        Checks if the provided value is valid based on the widget index. For the first widget (index 0), the value is valid if it 
        is numeric. For the second widget (index 1), the value is valid if it is not a single digit number. For other widgets, the value is valid 
        if it is not empty.

        Args:
            value (str): The value to check.
            widget_index (int): The index of the widget that the value comes from.

        Returns:
            bool: True if the value is valid, False otherwise.
        """
        # Check if the value is not empty
        if value == "":
            return False
        # Check if the value is numeric for the first widget
        if widget_index == 0 and not value.isdigit():
            return False
        # Check if the value is not a single digit number for the second widget
        if widget_index == 1 and value.isdigit() and len(value) == 1:
            return False
        return True

    # Go backwards
    def go_backwards(self, window, button_name_event=None, event=None):
        # Close the current window
        self.selected_value = None
        window.destroy()
        # Get the method from its string name and call it
        if button_name_event is not None:
            button_name_event()
        
    def get_entry_value(self, window, entry_widgets):
        """
        Retrieves and validates the values from a list of entry fields.

        This method iterates over the given entry widgets, retrieves the value from each one, and validates it.
        If the value from any entry field is None, it stops processing and returns None.
        Otherwise, it appends the value to a list and returns the list after processing all entry fields.

        Args:
            window (tkinter.Tk): The window that contains the entry fields.
            entry_widgets (list): A list of tkinter.Entry objects to get the values from.

        Returns:
            list: A list of validated values from the entry fields, or None if any value is None.
        """
        values = []
        for entry in entry_widgets:
            label_widget = self.label_entry_dict[entry]
            label_text = label_widget.cget("text")
            table_name = self.last_pressed_button if window == self.edit_window else self.selected_value
            type = self.sql_command(table_name).get(label_text).get('type')
            value = self.get_value(window, entry, label_text, type)
            if value is None:
                return
            values.append(value)
        return values

    def get_value(self, window, entry, label_text, type):
        """
        Retrieves the value from the given entry field and validates it.

        This method fetches the value from the entry field and checks if it matches the expected type.
        If the value starts with "Enter here:" and the label does not end with "*", it returns the previous value.
        If the value starts with "Default value:", it returns the default value.

        Args:
            window (tkinter.Tk): The window that contains the entry field.
            entry (tkinter.Entry): The entry field to get the value from.
            label_text (str): The text of the label associated with the entry field.
            type (str): The expected type of the value.

        Returns:
            str: The validated value from the entry field, or the previous or default value.
        """
        while True:  # Keep asking for input until a valid value is entered
            entry_value = entry.get()
            table_name = self.last_pressed_button if window == self.edit_window else self.selected_value
            if entry_value.startswith("Type here to"):
                return entry_value
            if not label_text.endswith("*") and entry_value.startswith("Enter here:"):
                return self.get_previous_values().get(label_text)
            elif entry_value.startswith("Default value:"):
                return self.sql_command(table_name).get(label_text).get('default_value')
            else:
                if not self.check_type(type, entry_value):
                    messagebox.showerror("Error", f"Incorrect value type for {label_text}. Expected {type}.")
                    entry.delete(0, 'end')  # Clear the entry field
                    return
                else:
                    return entry_value
            
    # Get the previous values of a record
    def get_previous_values(self):
        """
        Retrieves the previous values of a record from the database.

        This method fetches the record from the database that corresponds to the last pressed button and the selected value.
        It then constructs a dictionary mapping column names to their respective values in the fetched record.

        Returns:
            dict: A dictionary where the keys are column names and the values are the corresponding values in the record.
        """
        table_name = self.last_pressed_button
        table_name_id = self.selected_value
        # Get the data from the database
        data = self.sql.select_from_db(table=table_name, where=f'{self.button_table_map[table_name]["column"]} = {table_name_id}') 
        # Create a dictionary to store the previous values
        previous_values = {}
    
        for row in data:
            # Convert the tuple to a dictionary using the column names from the entity_map
            row_dict = dict(zip(SQL_schema_dict[table_name].keys(), row))
            for column in SQL_schema_dict[table_name]:
                if column in row_dict:
                    # Store the column name and value in the previous_values dictionary
                    previous_values[column] = row_dict[column]

        # Store the previous_values dictionary as an attribute of the object
        self.previous_values = previous_values
        return previous_values

    def check_date_format(self, value, date_format):
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            return False

    def check_type(self, type, value):
        if type == 'integer':
            return value.isdigit()
        elif type.startswith('varchar'):
            return isinstance(value, str)
        elif type == 'date':
            return self.check_date_format(value, '%Y-%m-%d')
        elif type == 'time':
            return self.check_date_format(value, '%H:%M:%S')
        elif type == 'datetime':
            return self.check_date_format(value, '%Y-%m-%d %H:%M:%S')
        # Add more type checks as needed
        return True

################################################################################################################################

########## Functions for the appearance of the main window and functions for opening/closing the app  ##########################

    # Method that changes foreground color
    def change_fg_color(self, mode):
        if mode == 'Light':
            return 'black'
        elif mode == 'Dark':
            return 'white'
        else:  # System
            return 'white' if self.get_system_fg_color() == 'black' else 'black' 
    
    # Method that gets the system foreground color based on the brightness of the background
    def get_system_fg_color(self):
        """
        Retrieves the background color of the root window, calculates its brightness, and returns a suitable foreground color. 
        If the background color is dark (brightness less than 100), it returns 'black'. Otherwise, it returns 'white'.

        Returns:
            str: The foreground color ('black' or 'white') based on the brightness of the background color.
        """
        # Get the background color
        bg_color = self.root.cget('bg')
        # Convert the color to RGB
        r, g, b = self.root.winfo_rgb(bg_color)
        # Calculate the brightness
        brightness = ((r * 299 + g * 587 + b * 114) / 1000)/257
        # Return 'white' if the color is dark, 'black' otherwise
        return 'black' if brightness < 100 else 'white'    

    # Method that handles the appearance mode button
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        # Get the background color of the root window
        bg_color = self.root.cget('bg')
        # Get the new foreground color
        fg_color = self.change_fg_color(new_appearance_mode)
        # Set the color of each listbox
        self.scrolled_listbox.configure(bg=bg_color, fg=fg_color)

    # Method for changing the scale of the window
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    # Method that starts the application
    def start(self):
    # For Windows
        if os.name == 'nt':
            _ = os.system('cls')
            # For Mac and Linux
        else:
            _ = os.system('clear') 
        self.root.mainloop()
    
    # Method that handles the closing of the app
    def on_closing(self, event=None):
        self.sql.close()
        self.root.destroy()

################################################################################################################################ 

if __name__ == '__main__':
    ZOO = GUI()
    ZOO.start()