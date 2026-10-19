import os
import re

INCLUDE = re.compile(r"\.(c|cc|cpp|h|hpp|java|py)$")
EXCLUDE_DIRECTORY=re.compile(r"\.[a-z]*")

def dfs(file_list, parent_dir):
    for path in os.listdir(parent_dir):
        if(os.path.isdir(os.path.join(parent_dir, path))) and not EXCLUDE_DIRECTORY.search(path):
            dfs(file_list, os.path.join(parent_dir, path))
        elif(INCLUDE.search(path)):
            file_list.append(os.path.join(parent_dir, path))