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

        # Build a tree structure from the changes
        tree = build_tree(series_path, changes)

        display_suggestions(series_path, tree, changes, root)

        # Start the event loop so that the suggestions window is shown
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

def build_tree(series_path, changes):
    """
    Build a hierarchical structure (tree) of directories and files from the changes.
    Each node in the tree:
    {
        'old_name': str,
        'new_name': str,
        'children': dict() of name->node,
        'is_dir': bool
    }
    """
    # We'll store nodes in a nested dict structure keyed by their paths.
    # For convenience, we will build a tree starting from a root node.
    root = {
        'old_name': os.path.basename(series_path),
        'new_name': os.path.basename(series_path), # root likely unchanged name
        'children': {},
        'is_dir': True
    }

    # Process each change
    for old_path, new_path in changes:
        rel_old = os.path.relpath(old_path, series_path)
        rel_new = os.path.relpath(new_path, series_path)

        old_parts = rel_old.split(os.sep)
        new_parts = rel_new.split(os.sep)

        # Navigate down the tree structure, creating nodes if necessary
        current_node = root
        for i, part in enumerate(old_parts):
            is_last = (i == len(old_parts)-1)

            # If the node doesn't exist yet, create it
            if part not in current_node['children']:
                # Initially assume no rename (old_name = part, new_name = part)
                # We'll fill in correct new_name after comparing with new_parts
                current_node['children'][part] = {
                    'old_name': part,
                    'new_name': part,
                    'children': {},
                    'is_dir': False  # Assume file by default; if not last step, it's a dir
                }

            node = current_node['children'][part]

            # If this is not the last part, this node is a directory
            if not is_last:
                node['is_dir'] = True

            # If this is the last part, update old_name/new_name from the actual rename
            if is_last:
                node['old_name'] = part
                node['new_name'] = new_parts[-1]
                # Determine if it's a directory or file by checking if old_path and new_path exist
                # This might not always be accurate at this stage since we haven't renamed yet.
                # We'll rely on the logic that season directories and parent directories
                # were part of changes from rename_series, so they should be directories.
                # If it's listed as a rename in rename_series at the directory level, it's a dir.
                if os.path.splitext(part)[1] == '':
                    # No extension, likely a directory (heuristic)
                    node['is_dir'] = True
                else:
                    # Has an extension, it's a file
                    node['is_dir'] = False

            # Move down the tree
            current_node = node

    return root

def display_suggestions(series_path, tree, changes, parent):
    suggestions_win = tk.Toplevel(parent)
    suggestions_win.title("Suggested Renames")

    text_widget = tk.Text(suggestions_win, wrap="none")
    text_widget.pack(fill="both", expand=True)

    text_widget.tag_configure("old", foreground="red", overstrike=True)
    text_widget.tag_configure("new", foreground="green")

    # Recursively insert the tree into the text widget
    insert_tree(text_widget, tree, indent_level=0)

    button_frame = tk.Frame(suggestions_win)
    button_frame.pack(fill="x", pady=5)

    confirm_button = tk.Button(button_frame, text="Confirm", command=lambda: do_renames(series_path, changes, suggestions_win))
    confirm_button.pack(side="left", padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", command=suggestions_win.destroy)
    cancel_button.pack(side="right", padx=5)

def insert_tree(text_widget, node, indent_level):
    indent = "  " * indent_level

    # Print this node's name
    old_name = node['old_name']
    new_name = node['new_name']

    # If old_name != new_name, show old in red strike-through and new in green
    # Otherwise just show the name
    if old_name != new_name:
        # old
        text_widget.insert("end", indent)
        text_widget.insert("end", old_name, "old")
        text_widget.insert("end", " -> ")
        text_widget.insert("end", new_name + "\n", "new")
    else:
        text_widget.insert("end", indent + old_name + "\n")

    # If directory, print children with one more indentation level
    if node['is_dir']:
        for child in sorted(node['children'].keys()):
            insert_tree(text_widget, node['children'][child], indent_level + 1)

def do_renames(series_path, changes, window):
    try:
        execute_changes(series_path, changes)
        messagebox.showinfo("Success", "Renaming completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during renaming:\n{e}")
    finally:
        window.destroy()
