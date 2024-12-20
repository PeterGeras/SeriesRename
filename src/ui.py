import tkinter as tk
from tkinter import filedialog, messagebox
from logic import rename_series, execute_changes


def select_folder_and_rename():
    """
    Opens a folder selection dialog and triggers the renaming logic.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Prompt the user to select a folder
    series_path = filedialog.askdirectory(title="Select TV Series Folder")
    if not series_path:
        return

    # Extract series name from the folder name
    series_name = series_path.split("/")[-1] or series_path.split("\\")[-1]

    # Generate renaming suggestions
    try:
        changes = rename_series(series_path, series_name)
        if not changes:
            messagebox.showinfo("No Changes", "No files to rename in the selected folder.")
            return

        # Confirm and execute renaming
        execute_changes(series_path, changes)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
