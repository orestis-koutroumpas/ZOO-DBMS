import tkinter as tk
from tkinter import messagebox


class ScrolledListbox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes a new instance of the class. This instance includes a listbox with both vertical and horizontal scrollbars. 
        The listbox is initially disabled.

        Args:
            parent (tkinter object): The parent widget to which this scrolled listbox belongs.
        """
        tk.Frame.__init__(self, parent)
        self.listbox = tk.Listbox(self, *args, **kwargs)
        # Vertical Scrollbar
        self.v_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=self.update_v_scrollbar)
        # Horizontal Scrollbar
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.listbox.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.listbox.configure(xscrollcommand=self.update_h_scrollbar)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.selected_item = None
        ### Key Bindings
        self.listbox.bind('<Enter>', self.enter)
        self.listbox.bind('<Leave>', self.leave)
        self.listbox.bind("<Button-3>", self.copy_to_clipboard)
        # Bind mouse button click event to a custom method
        self.listbox.bind('<Button-1>', self.on_click)
        #self.listvariable(kwargs.get('listvariable',None))
        self.configure()
        # Set the state of the listbox to "disabled" by default
        self.listbox.configure(state="disabled")


    def configure(self, **kwargs):
        """
        Configures the listbox with the provided keyword arguments. If no value is provided for a particular option, a default 
        value is used. The options include 'listvariable', 'bg', 'fg', 'highlightcolor', 'selectbackground', and 'exportselection'.

        Keyword Args:
            listvariable (tkinter.Variable): The variable that the listbox is linked to.
            bg (str): The background color of the listbox.
            fg (str): The foreground color of the listbox.
            highlightcolor (str): The color of the focus highlight when the listbox has focus.
            selectbackground (str): The color of the background of the selected item.
            exportselection (bool): Whether to export the selection to the clipboard when the listbox loses focus.
        """
        self.listvariable(kwargs.get('listvariable',None))
        self.setbackground(kwargs.get('bg', self.master['background']))
        self.setforeground(kwargs.get('fg',None))
        self.sethighlight(kwargs.get('highlightcolor',None))
        self.setselectbackground(kwargs.get('selectbackground',None))
        self.setexportselection(kwargs.get('exportselection',1))
    
    # It handles the selection from the listbox.
    def set_select_callback(self, callback):
        """
        Sets the function to be called.

        Args:
            callback (function): The function to call when a selection is being made
        """
        self.listbox.bind('<<ListboxSelect>>', callback)
        
    def update_v_scrollbar(self, *args):
        """
        Updates the vertical scrollbar of the listbox.
        """
        self.v_scrollbar.set(*args)
        self.check_scrollbars()

    def update_h_scrollbar(self, *args):
        """
        Updates the horizontal scrollbar of the listbox.
        """
        self.h_scrollbar.set(*args)
        self.check_scrollbars()
        
    def check_scrollbars(self):
        """
        Checks if the scrollbars are needed and packs them accordingly.
        """
        # Check if vertical scrollbar is needed
        if self.listbox.yview() == (0.0, 1.0):
            self.v_scrollbar.pack_forget()
        else:
            self.v_scrollbar.pack(side="right", fill="y")

        # Check if horizontal scrollbar is needed
        if self.listbox.xview() == (0.0, 1.0):
            self.h_scrollbar.pack_forget()
        else:
            self.h_scrollbar.pack(side="bottom", fill="x")

    def listvariable(self, item_list):
        """
        Populates the listbox with the items in the provided list. Each item in the list is inserted at the end of the listbox.

        Args:
            item_list (List): The list of items to insert into the listbox.
        """
        if item_list != None:
            for item in item_list:
                self.listbox.insert(tk.END, item)

    def setexportselection(self, exportselection):
        """
        Sets the 'exportselection' option of the listbox. If 'exportselection' is set to True, the selected text is exported 
        to the clipboard when the listbox loses focus.

        Args:
            exportselection (bool): Whether to export the selection to the clipboard when the listbox loses focus.
        """
        self.listbox.configure(exportselection = exportselection)

    def copy_to_clipboard(self, event):
        """
        Copies the currently selected value to the clipboard.

        Args:
            event (tkinter.Event): The event information.
        """
        try:
            # Get the current selection
            selection = self.listbox.get(self.listbox.curselection())

            # Clear the clipboard and append the selection
            self.listbox.clipboard_clear()
            self.listbox.clipboard_append(selection)
            
            # Show a message box with the copied text
            messagebox.showinfo("Copied to clipboard", f"'{selection}' has been copied to the clipboard.")
        except tk.TclError:
            # No selection, do nothing
            pass

    def setbackground(self, bg):
        """
        Sets the background color of the listbox, if a color is provided

        Args:
            bg (str): The color to set as the background
        """
        if bg != None:
            self.listbox.configure(bg = bg)
        
    def setforeground(self, fg):
        """
        Sets the foreground color of the listbox, if a color is provided

        Args:
            fg (str): The color to set as the foreground
        """
        if fg != None:
            self.listbox.configure(fg = fg)
            
    def sethighlight(self, highlightcolor):
        """
        Sets the highlight color of the listbox, if a color is provided

        Args:
            highlightcolor (str): The color to set as highlight color.
        """
        if highlightcolor != None:
            self.listbox.configure(highlightcolor = highlightcolor)

    def setselectbackground(self, selectbackground):
        """
        Sets the background color of the selected item in the listbox, if a color is provided.

        Args:
            selectbackground (str): The color to set as the background color of the selected item in the listbox.
        """
        if selectbackground != None:
            self.listbox.configure(selectbackground = selectbackground)

    def enter(self, event):
        """
        Changes the cursor to a hand cursor when the mouse enters the listbox. This method is bound to the '<Enter>' event.

        Args:
            event (tkinter.Event): The event object passed by the '<Enter>' event.
        """
        self.listbox.config(cursor="hand2")

    def leave(self, event):
        """
        Resets the cursor to the default cursor when the mouse leaves the listbox. This method is bound to the '<Leave>' event.

        Args:
            event (tkinter.Event): The event object passed by the '<Leave>' event.
        """
        self.listbox.config(cursor="")

    # Add a new method to enable the listbox
    def enable(self):
        """
        Enables the listbox.
        """
        self.listbox.configure(state="normal")
        
    # Add a new method to disable the listbox
    def disable(self):
        """
        Disables the listbox by making it unclickable.
        """
        self.listbox.configure(state="disabled")

    def insert(self, location, item):
        """
        Inserts an item into the listbox at the specified location.

        Args:
            location (int or str): The index at which to insert the new item. This can be an integer or the string 'end'.
            item (str): The item to insert into the listbox.
        """
        self.listbox.insert(location, item)

    def curselection(self):
        """
        Returns the indices of the currently selected item(s) in the listbox.

        Returns:
            tuple: A tuple containing the indices of the currently selected item(s).
        """
        return self.listbox.curselection()
    
    def get_selected_item(self, event):
        """
        Retrieves the currently selected item in the listbox and stores it in the 'selected_item' attribute. This method is typically 
        bound to a selection event in the listbox.

        Args:
            event (tkinter.Event): The event object passed by the selection event.
        """
        selection = event.widget.curselection()
        if selection:
            self.selected_item = event.widget.get(selection[0])
            

    def on_click(self, event):
        """
        Handles mouse button click event in the listbox.

        Args:
            event (tkinter.Event): The event object passed by the click event.
        """
        # Check if the Ctrl key is pressed
        if event.state & 0x0004:  # 0x0004 is the state code for the Ctrl key
            # Get the item under the mouse
            clicked_item = self.listbox.nearest(event.y)
            # Check if the item is already selected
            if clicked_item in self.listbox.curselection():
                # If the item is already selected, unselect it
                self.listbox.selection_clear(clicked_item)
            else:
                # If the item is not selected, select it
                self.listbox.selection_set(clicked_item)
        else:
            # If the Ctrl key is not pressed, clear the selection and select the item under the mouse
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(self.listbox.nearest(event.y))

    def unselect_current_item(self):
        """
        Unselects the currently selected item in the listbox.
        """
        selected_indices = self.listbox.curselection()
        if selected_indices:  # if there is a selection
            self.listbox.selection_clear(selected_indices[0])  # unselect the first selected item
        
    def delete(self, first, last=None):
        """
        Deletes items from the listbox. If 'last' is not provided, only the item at index 'first' is deleted. If 'last' is provided, 
        all items from 'first' to 'last' are deleted.

        Args:
            first (int): The index of the first item to delete.
            last (int, optional): The index of the last item to delete. If not provided, only the 'first' item is deleted.
        """
        self.listbox.delete(first, last)

    def delete_selected(self, event=None):
        """
        Deletes the currently selected items from the listbox. The method takes into account the shift in indices that occurs 
        when an item is deleted.
        """
        selected_item = self.listbox.curselection()
        idx_count = 0
        for item in selected_item:
            self.listbox.delete(item - idx_count)
            idx_count += 1

    ################################## Currently not in use for that app #####################################

    def delete_unselected(self):
        """
        Deletes the unselected items from the listbox. The method takes into account the shift in indices that occurs 
        when an item is deleted.
        """
        selected_item = self.listbox.curselection()
        idx_count = 0
        for i, listbox_entry in enumerate(self.listbox.get(0, tk.END)):
            if not listbox_entry in selected_item:
                self.listbox.delete(i - idx_count)
                idx_count += 1