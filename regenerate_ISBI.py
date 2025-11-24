#from generate_deepdrr import Generate
import os
import requests
import pandas as pd
import shutil
from generate_deepdrr import Generate

# Function to extract case number
def extract_case_number(path):
    parts = path.split('/')
    for part in parts:
        if part.startswith('case'):
            return part

mysql_url = 'https://jjung2.w3.uvm.edu/uvmmc/api/read.php'

# Make a get request to insert data into the MySQL table
response = requests.get(mysql_url)

table = pd.DataFrame(response.json()['data'])
table['case_number'] = table['target'].apply(extract_case_number)

file_path = "/netfiles/vaillab/test_datasets"
output_path = "regenerated_new2"
 
x_coor = []
y_coor = []
z_coor = []
patient = []
mark = []
landmark = []
operator = []
file_path_list = []
body_part = []


if os.path.exists(output_path):
    try:
        shutil.rmtree(output_path)
    except OSError as e:
        print(f"Error: {output_path} : {e.strerror}")
else:
    try:
        os.makedirs(output_path)
    except OSError as e:
        print(f"Error: {output_path} : {e.strerror}")

for location in range(1,21):
    os.makedirs(f"{output_path}/{location}")

for location in range(1,21):
    os.makedirs(f"{output_path}/{location}/H")
    os.makedirs(f"{output_path}/{location}/T")

for i in range(0, len(table)):
    try:
        if table.iloc[i]['sample_name'] == 'BONE_H-N-UXT_3X3':
            sample_name = "sample_datasets/" + table.iloc[i]['target'] + "_" + table.iloc[i]['sample_name'] + ".nii.gz"
            g = Generate(file = f"{file_path}/{sample_name}", path=f"{output_path}/{table.iloc[i]['item_order']}/H/{table.iloc[i]['case_number']}_{table.iloc[i]['group_id']}.png")
            g.deepdrr_regenerate(table.iloc[i]['x'],table.iloc[i]['y'],table.iloc[i]['z'],table.iloc[i]['a'],table.iloc[i]['b'])
            file_path_list.append(f"{output_path}/{table.iloc[i]['item_order']}/H/{table.iloc[i]['case_number']}_{table.iloc[i]['group_id']}.png")
            body_part.append('upper')
        elif "H-N" in table.iloc[i]['sample_name']:
            g = Generate(file = f"{file_path}/{table.iloc[i]['sample_name']}", path=f"{output_path}/{table.iloc[i]['item_order']}/H/{table.iloc[i]['case_number']}_{table.iloc[i]['group_id']}.png")
            g.deepdrr_regenerate(table.iloc[i]['x'],table.iloc[i]['y'],table.iloc[i]['z'],table.iloc[i]['a'],table.iloc[i]['b'])
            file_path_list.append(f"{output_path}/{table.iloc[i]['item_order']}/H/{table.iloc[i]['case_number']}_{table.iloc[i]['group_id']}.png")
            body_part.append('upper')
        elif "TORSO" in table.iloc[i]['sample_name']:
            g = Generate(file = f"{file_path}/{table.iloc[i]['sample_name']}", path=f"{output_path}/{table.iloc[i]['item_order']}/T/{table.iloc[i]['case_number']}_{table.iloc[i]['group_id']}.png")
            g.deepdrr_regenerate(table.iloc[i]['x'],table.iloc[i]['y'],table.iloc[i]['z'],table.iloc[i]['a'],table.iloc[i]['b'])        
            file_path_list.append(f"{output_path}/{table.iloc[i]['item_order']}/T/{table.iloc[i]['case_number']}_{table.iloc[i]['group_id']}.png")
            body_part.append('lower')
        x_coor.append(table.iloc[i]['x'])
        y_coor.append(table.iloc[i]['y'])
        z_coor.append(table.iloc[i]['z'])
        operator.append(table.iloc[i]['group_id'])
        landmark.append(table.iloc[i]['item_order'])
        patient.append(table.iloc[i]['target'])
        
    except Exception as e:

        print(e)

df = {'x_coor' : x_coor,
      'y_coor' : y_coor,
      'z_coor' : z_coor,
      'operator_ID' : operator,
      'landmark' : landmark,
      'patient_ID' : patient,
      'image_path_file' : file_path_list,
      'body_type' : body_part}


df = pd.DataFrame(df)

df.to_csv("regenerated_new.csv")
