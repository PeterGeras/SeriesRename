import os
import sys
from pathlib import Path
from collections import Counter
import tkinter
from tkinter import filedialog
from itertools import takewhile


# ----- CONFIG ----- #

WRITE_NAMES = True
sys.stdout = open('rename.log', 'w')

# ------------------ #

NAME_STRUCTURE = 'E{:02d}'
FOLDER_PATH = os.getcwd()
FILETYPE_FOLDER = 'folder'


def rename_files(filetype: str):
    filenames = os.listdir(FOLDER_PATH)
    counter = 1

    for filename in sorted(filenames):  # all files and folders
        path_from = os.path.join(os.path.abspath(FOLDER_PATH), filename)
        filename_new = NAME_STRUCTURE.format(counter)

        if filetype == FILETYPE_FOLDER and os.path.isdir(path_from):  # folders
            pass
        elif filetype == Path(filename).suffix and not os.path.isdir(path_from):  # files
            filename_new += filetype
        else:
            continue

        path_to = os.path.join(os.path.abspath(FOLDER_PATH), filename_new)
        print(f'{filename_new=} - {path_from=} - {path_to=}')
        if WRITE_NAMES:
            os.rename(path_from, path_to)
        counter += 1

    return


def get_items_with_max_count(dct):
    data = dct.most_common()
    val = data[1][1] #get the value of n-1th item
    #Now collect all items whose value is greater than or equal to `val`.
    return list(takewhile(lambda x: x[1] >= val, data))


def count_filetypes(filenames: list):
    filetypes = Counter()
    for filename in filenames:  # all files and folders
        if os.path.isdir(os.path.join(os.path.abspath("."), filename)):  # folders
            filetypes[FILETYPE_FOLDER] += 1
        else:
            filetypes[Path(filename).suffix] += 1

    print(f"{'-'*5} counts {'-'*5}")
    print(*filetypes, sep='\n', end='\n\n')

    top_2 = filetypes.most_common(2)  # top_2 == [('.mp4', 10), ('.srt', 10)]
    # If subs then hopefully video filetype and srt filetype have same amount
    if len(top_2) == 2 and top_2[0][1] == top_2[1][1]:
        most_common = [top_2[0][0], top_2[1][0]]
    else:
        most_common = [top_2[0][0]]

    return most_common


def print_file_info(filenames: list):
    file_info = []
    for file in filenames:
        file_info.append(f'{file} - {Path(file).suffix}')

    print(f"{'-'*5} Files - FileTypes {'-'*5}")
    print(*file_info, sep='\n', end='\n\n')

    return


def ui():
    tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
    folder_path = filedialog.askdirectory()

    return folder_path


def main():
    global FOLDER_PATH
    FOLDER_PATH = ui()
    if FOLDER_PATH == '':
        print('No path chosen, aborting...')
        return

    filenames = os.listdir(FOLDER_PATH)  # get all files' and folders' names in the directory
    print_file_info(filenames)
    filetypes_most_common = count_filetypes(filenames)

    for filetype in filetypes_most_common:
        rename_files(filetype)


if __name__ == '__main__':
    main()
