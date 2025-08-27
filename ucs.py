import customtkinter as ctk
import pandas as pd
import os
import sys
from tkinter import ttk
from CTkMessagebox import CTkMessagebox

class UCSPopup(ctk.CTkToplevel):
    def __init__(self, master, excel_path, catID_textbox, cat_textbox, sub_textbox, ucsAll, on_close_callback=None):
        super().__init__(master)

        print("UCSPopup: __init__ started")

        self.title("UCS List Selector")
        self.geometry("1000x600")
        self.grab_set()
        self._on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.master_app = master
        self.excel_path = excel_path
        self.catID_entry = catID_textbox
        self.cat_entry = cat_textbox
        self.sub_entry = sub_textbox
        self.ucsAll = ucsAll

        self.df = None
        self.filtered_df = None

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2b2b2b",
                        bordercolor="#3f3f3f",
                        lightcolor="#3f3f3f",
                        darkcolor="#3f3f3f"
                       )
        style.map('Treeview',
                  background=[('selected', '#524d77')],
                  foreground=[('selected', 'white')]
                 )
        style.configure("Treeview.Heading",
                        background="#3f3f3f",
                        foreground="white",
                        font=("", 10, "bold")
                       )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        self.search_label = ctk.CTkLabel(self.search_frame, text="Search:")
        self.search_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, placeholder_text="Enter search query...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_var.trace_add("write", self.on_search_change)

        self.results_label = ctk.CTkLabel(self.search_frame, text="Results: 0")
        self.results_label.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")

        self.tree_container_frame = ctk.CTkFrame(self)
        self.tree_container_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_container_frame.grid_rowconfigure(0, weight=1)
        self.tree_container_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.tree_container_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.vsb = ctk.CTkScrollbar(self.tree_container_frame, command=self.tree.yview)
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.hsb = ctk.CTkScrollbar(self.tree_container_frame, orientation="horizontal", command=self.tree.xview)
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=self.hsb.set)

        self.tree.bind("<Double-1>", self.on_double_click_table)

        self.select_button = ctk.CTkButton(self, text="Select Cat ID", command=self.on_select_button,
                                           fg_color="#9f005e", hover_color="#8a0051")
        self.select_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        print(f"UCSPopup: Calling load_excel_file with path: {self.excel_path}")
        self.load_excel_file(self.excel_path)
        print("UCSPopup: __init__ finished")

    def _on_closing(self):
        print("UCSPopup: Window closing via WM_DELETE_WINDOW protocol (e.g., 'X' button click).")
        # Call the external callback if it exists
        if self._on_close_callback:
            self._on_close_callback()
        self.destroy()

    def load_excel_file(self, path):
        print(f"load_excel_file: Attempting to load from {path}")
        try:
            # === IMPORTANT: Use the ACTUAL column name from Excel for reading ===
            actual_excel_columns = ['CatID', 'Category', 'SubCategory', 'Explanations', 'Synonyms - Comma Separated']
            # Specify header=2 because your data starts on the 3rd row (index 2)
            self.df = pd.read_excel(path, usecols=actual_excel_columns, header=2)

            # === RENAME the column AFTER loading ===
            if 'Synonyms - Comma Separated' in self.df.columns:
                self.df.rename(columns={'Synonyms - Comma Separated': 'Synonyms'}, inplace=True)
                print("load_excel_file: 'Synonyms - Comma Separated' column renamed to 'Synonyms'.")

            self.filtered_df = self.df.copy()
            print(f"load_excel_file: DataFrame loaded successfully. Shape: {self.df.shape}")
            print(f"load_excel_file: DataFrame columns after rename: {self.df.columns.tolist()}")
            self.populate_table()
        except FileNotFoundError:
            print(f"load_excel_file: FileNotFoundError: {path}")
            CTkMessagebox(title="Error", message=f"Excel file not found at: {path}", icon="cancel",
                              option_1="OK", master=self)
            self.destroy()
        except KeyError as e:
            print(f"load_excel_file: KeyError: Missing expected column: {e}")
            CTkMessagebox(title="Error", message=f"Missing expected column in Excel: {e}\n"
                                                      f"Ensure file contains: {actual_excel_columns}", # Use original names for error
                              icon="cancel", option_1="OK", master=self)
            self.destroy()
        except Exception as e:
            print(f"load_excel_file: General Exception: {e}")
            CTkMessagebox(title="Error", message=f"Error loading Excel file: {e}", icon="cancel",
                              option_1="OK", master=self)
            self.destroy()

    def populate_table(self):
        print("populate_table: called")
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.filtered_df is not None and not self.filtered_df.empty:
            print(f"populate_table: Filtered DataFrame is not empty. Rows: {len(self.filtered_df)}")
            columns = self.filtered_df.columns.tolist()
            self.tree["columns"] = columns
            self.tree["show"] = "headings"

            for col in columns:
                self.tree.heading(col, text=col, anchor="w")
                # Adjust widths for the new names if necessary
                if col == 'CatID':
                    self.tree.column(col, width=80, minwidth=50, stretch=False)
                elif col == 'Category':
                    self.tree.column(col, width=100, minwidth=70, stretch=False)
                elif col == 'SubCategory':
                    self.tree.column(col, width=120, minwidth=80, stretch=False)
                elif col == 'Synonyms': # Use the new, renamed column name here for width adjustment
                    self.tree.column(col, width=250, minwidth=100, stretch=True)
                else: # For 'Explanations'
                    self.tree.column(col, width=250, minwidth=100, stretch=True)


            for index, row in self.filtered_df.iterrows():
                self.tree.insert("", "end", values=list(row))
            print("populate_table: Data inserted into Treeview.")
        else:
            print("populate_table: Filtered DataFrame is empty or None.")
            self.tree["columns"] = ("No Data",)
            self.tree.heading("No Data", text="No data to display or no results found.", anchor="center")
            self.tree.column("No Data", width=980, stretch=True)

        self.update_results_count()
        print("populate_table: finished")

    def on_search_change(self, var_name, index, mode):
        print(f"on_search_change: Search query changed to '{self.search_var.get()}'")
        query = self.search_var.get().lower()
        if not query:
            self.filtered_df = self.df.copy()
        else:
            # === IMPORTANT: Use the RENAMED column name for searching ===
            search_cols = ['CatID', 'Category', 'SubCategory', 'Explanations', 'Synonyms']
            self.filtered_df = self.df[
                self.df[search_cols].astype(str).apply(lambda row: row.str.lower().str.contains(query).any(), axis=1)
            ].copy()
        self.populate_table()

    def update_results_count(self):
        if self.filtered_df is not None:
            count = len(self.filtered_df)
            self.results_label.configure(text=f"Results: {count}")
        else:
            self.results_label.configure(text="Results: 0")

    def get_selected_row_values(self):
        selected_item = self.tree.focus()
        if selected_item:
            return self.tree.item(selected_item, 'values')
        return None

    def populate_parent_entries_and_close(self, values):
        if values:
            try:
                # Based on the order of columns after rename: CatID, Category, SubCategory
                self.catID_entry.delete(0, ctk.END)
                self.catID_entry.insert(0, values[0]) # CatID

                self.cat_entry.delete(0, ctk.END)
                self.cat_entry.insert(0, values[1]) # Category

                self.sub_entry.delete(0, ctk.END)
                self.sub_entry.insert(0, values[2]) # SubCategory

            except IndexError:
                CTkMessagebox(title="Data Error", message="Selected row does not contain expected number of columns (at least 3 for CatID, Category, SubCategory).",
                                  icon="warning", option_1="OK", master=self)
            if self._on_close_callback:
                self._on_close_callback()
            self.destroy()

    def on_double_click_table(self, event):
        selected_values = self.get_selected_row_values()
        if selected_values:
            self.populate_parent_entries_and_close(selected_values)

    def on_select_button(self):
        selected_values = self.get_selected_row_values()
        if selected_values:
            self.populate_parent_entries_and_close(selected_values)
        else:
            CTkMessagebox(title="Selection Required", message="Please select a row from the table.",
                              icon="info", option_1="OK", master=self)