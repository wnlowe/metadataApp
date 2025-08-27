import tkinter
from tkinter import filedialog
import os
from os.path import isfile, join
import configManager
import configparser # <--- ADDED: Import configparser for getSelectedFile

# --- GLOBAL VARIABLES (initialized at module level) ---
# These must be initialized here so they always exist, even if None initially.
currentDir = os.path.dirname(__file__) # Initialize currentDir globally
configMan = None
isConfig = False

def config():
    """
    Initializes or loads the ConfigManager.
    Ensures configMan and isConfig are always set.
    """
    global currentDir, configMan, isConfig # Explicitly declare globals

    # Ensure currentDir is set (it's already done at module level, but good practice)
    currentDir = os.path.dirname(__file__)

    config_path = os.path.join(currentDir, "config.ini")

    if not os.path.exists(config_path):
        print(f"Config file not found at {config_path}. Creating default config.")
        configMan = configManager.ConfigManager(config_path)
        configMan.create_default_config()
    else:
        print(f"Config file found at {config_path}. Loading existing config.")
        configMan = configManager.ConfigManager(config_path)
        configMan.load_config() # <--- IMPORTANT: Load existing config

    isConfig = True
    print("Metadata.config() completed. configMan is now initialized.")


def fileNames():
    """
    Reads file names from 'src/files.txt' and returns their basenames.
    """
    # Ensure currentDir is defined (it should be by the global init or config() call)
    if not currentDir:
        config() # Ensure config is run to set currentDir
    
    files_txt_path = os.path.join(currentDir, "src", "files.txt")
    
    if not os.path.exists(files_txt_path):
        print(f"Warning: {files_txt_path} not found.")
        return []

    file_names_list = []
    try:
        with open(files_txt_path, "r") as f:
            files = f.readlines()
        for file_line in files:
            # Use os.path.basename and strip whitespace
            file_names_list.append(os.path.basename(file_line.strip()))
    except Exception as e:
        print(f"Error reading files.txt: {e}")
    return file_names_list

def setSelectedFile(file):
    """
    Sets the 'Selected File' value in the 'USER' section of the config.
    """
    global configMan, isConfig # Explicitly declare globals

    if not isConfig or configMan is None: # Ensure config is loaded
        config()

    if configMan: # Check if configMan is successfully initialized
        if configMan.add_section('USER', 'UI'):
            configMan.set_value('USER', 'Selected File', file)
            configMan.save_config()
            print(f"Set 'Selected File' to '{file}' in config.")
        else:
            print(f"Could not add/find 'USER' section in config for file '{file}'.")
    else:
        print("Error: configMan is not initialized. Cannot set selected file.")


def getSelectedFile():
    """
    Retrieves the 'Selected File' value from the 'USER' section of the config.
    Uses configMan for consistency.
    """
    global configMan, isConfig # Explicitly declare globals

    if not isConfig or configMan is None: # Ensure config is loaded
        config()

    if configMan: # Check if configMan is successfully initialized
        return configMan.get_value('USER', 'Selected File')
    else:
        print("Error: configMan is not initialized. Cannot get selected file.")
        return None

def setCatIDforFile(catID):
    """
    This function is currently empty.
    If it's meant to interact with config, it should use configMan.
    """
    global configMan, isConfig # Explicitly declare globals
    if not isConfig or configMan is None:
        config()
    print(f"setCatIDforFile called with: {catID} (function is currently empty)")
    # Example: configMan.set_value('SOME_SECTION', 'CatID', catID)
    # configMan.save_config()


# --- Initial call to config() when Metadata.py is imported ---
# This ensures configMan and isConfig are set up immediately.
config()
