import os
import pandas as pd

df = pd.read_csv("bounding_box_annotations_modified.csv")
df['file_path'] = df['file_path'].apply(lambda x: x.split("/")[-1].split("_")[0])
case_list = df['file_path'].unique()
for i, row in enumerate(case_list):
    for j in range(0,30):
        if i % 30 == j:
            with open(f"divided_cases/{j}.txt", 'a') as file_open:
                file_open.write(row+"\n")
            
