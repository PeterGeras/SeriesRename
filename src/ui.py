import tkinter as tk
from tkinter import filedialog, messagebox
from logic import rename_series, execute_changes
import os


def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    series_path = filedialog.askdirectory(title="Select TV Series Folder")
    if not series_path:
        return

    series_name = os.path.basename(series_path.strip("/\\"))

    try:
        changes = rename_series(series_path, series_name)
        if not changes:
            messagebox.showinfo("No Changes", "No files or folders need renaming.")
            return

        display_suggestions(series_path, changes, root)

        # Start the event loop so that the suggestions window is shown
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")


def display_suggestions(series_path, changes, parent):
    suggestions_win = tk.Toplevel(parent)
    suggestions_win.title("Suggested Renames")

    text_widget = tk.Text(suggestions_win, wrap="none")
    text_widget.pack(fill="both", expand=True)

    text_widget.tag_configure("old", foreground="red", overstrike=True)
    text_widget.tag_configure("new", foreground="green")

    for old_path, new_path in changes:
        rel_old = os.path.relpath(old_path, series_path)
        rel_new = os.path.relpath(new_path, series_path)
        if old_path != new_path:
            text_widget.insert("end", rel_old, "old")
            text_widget.insert("end", " -> ")
            text_widget.insert("end", rel_new + "\n", "new")
        else:
            text_widget.insert("end", rel_old + " (no change)\n")

    button_frame = tk.Frame(suggestions_win)
    button_frame.pack(fill="x", pady=5)

    confirm_button = tk.Button(button_frame, text="Confirm", command=lambda: do_renames(series_path, changes, suggestions_win))
    confirm_button.pack(side="left", padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", command=suggestions_win.destroy)
    cancel_button.pack(side="right", padx=5)


def do_renames(series_path, changes, window):
    try:
        execute_changes(series_path, changes)
        messagebox.showinfo("Success", "Renaming completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during renaming:\n{e}")
    finally:
        window.destroy()
