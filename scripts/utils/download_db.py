import kagglehub
import os
import shutil

# Download latest version
path = kagglehub.dataset_download("terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database")

print("Path to dataset files:", path)

# Copy downloaded files into the current working directory
cwd = os.getcwd()
for name in os.listdir(path):
    src = os.path.join(path, name)
    dst = os.path.join(cwd, name)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)

print("Files copied to:", cwd)