import tkinter as tk
from tkinter import filedialog
import os


# Function to select a folder
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory()
    return folder_path

def is_folder_empty(folder_path):
    return len(os.listdir(folder_path)) == 0