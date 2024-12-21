import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from logic import rename_series, execute_changes


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

        display_suggestions(tree, changes, root)

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
        'children': dict(),
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


def display_suggestions(tree, changes, parent):
    suggestions_win = tk.Toplevel(parent)
    suggestions_win.title("Suggested Renames")
    suggestions_win.protocol("WM_DELETE_WINDOW", lambda: close_all(parent, suggestions_win))

    style = ttk.Style(suggestions_win)
    style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
    style.map("TButton", 
              foreground=[('!disabled', 'black')],
              background=[('!disabled', '#e1e1e1'), ('active', '#d4d4d4')],
              relief=[('pressed', 'ridge'), ('!disabled', 'flat')])

    text_widget = tk.Text(suggestions_win, wrap="none")
    text_widget.pack(fill="both", expand=True)

    text_widget.tag_configure("old", foreground="red", overstrike=True)
    text_widget.tag_configure("new", foreground="green")

    insert_tree(text_widget, tree, prefix="", is_last=True)

    button_frame = ttk.Frame(suggestions_win)
    button_frame.pack(fill="x", pady=5, padx=5)

    cancel_button = ttk.Button(
        button_frame,
        text="Cancel",
        command=lambda: close_all(parent, suggestions_win),
        style="TButton"
    )
    cancel_button.pack(side="left", padx=(0, 10))

    confirm_button = ttk.Button(
        button_frame,
        text="Confirm",
        command=lambda: do_renames(changes, suggestions_win, parent),
        style="TButton"
    )
    confirm_button.pack(side="right")


def insert_tree(text_widget, node, prefix="", is_last=True):
    """
    Recursively insert tree structure into the text widget with a tree-like visualization.
    prefix: The string prefix to show before the node (with lines).
    is_last: If this node is the last child in its directory, affects drawing lines.
    """

    # Choose the branch character based on whether it's the last child
    branch = "└── " if is_last else "├── "

    # If this is the root node, don't display the branch (just the name)
    display_name = node['old_name'] if node['old_name'] == node['new_name'] else f"{node['old_name']} {node['new_name']}"
    if node['old_name'] == node['new_name']:
        # No rename
        if prefix:
            text_widget.insert("end", prefix + branch + display_name + "\n")
        else:
            text_widget.insert("end", display_name + "\n")
    else:
        # Renamed, show old in red and new in green
        if prefix:
            text_widget.insert("end", prefix + branch)
        old_name = node['old_name']
        new_name = node['new_name']
        text_widget.insert("end", old_name, "old")
        text_widget.insert("end", " ")
        text_widget.insert("end", new_name + "\n", "new")

    # If directory, show children
    if node['is_dir'] and node['children']:
        # For each child, determine the new prefix and whether it's the last child
        children_keys = sorted(node['children'].keys())
        for i, child_key in enumerate(children_keys):
            child = node['children'][child_key]
            # If not last, we add a vertical line to show continuation
            child_prefix = prefix + ("\t" if is_last else "│\t")
            insert_tree(text_widget, child, prefix=child_prefix, is_last=(i == len(children_keys) - 1))


def do_renames(changes, window, parent):
    try:
        execute_changes(changes)
        messagebox.showinfo("Success", "Renaming completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during renaming:\n{e}")
    finally:
        close_all(parent, window)


def close_all(parent, window):
    window.destroy()
    parent.quit()
