from generate_deepdrr import Generate
import pandas as pd
import numpy as np
import os
from PIL import Image
import sys


df = pd.read_csv("/gpfs2/scratch/jjung2/c-arm_projects/image_collections/bounding_box_annotations_modified.csv")
df['file_path'] = df['file_path'].apply(lambda x: x.split("/")[-1])
case_list = df['file_path'].unique()

head_identifier = "BONE_H-N-UXT_3X3"
input_path = "/netfiles/vaillab/upper_nifti/"
output_path = "/netfiles/vaillab/gaussian_xyzabg/"
filter = True


# devide and conquer
file_list = []
with open(f"../divided_cases/{sys.argv[1]}.txt", "r") as file_open:
    for row in file_open.readlines():
        file_list.append(row.strip() + f"_{head_identifier}.nii.gz")
image_info_csv = []

for file_name in file_list:
    if file_name in case_list:
        # create CT scan path
        file_path = os.path.join(input_path, file_name)
        patient_output_path = os.path.join(output_path, file_name.split("_")[0])

        patient_df = df[df['file_path'] == file_name]

        g = Generate(file_path)
        low, top = g.patient.get_bounding_box_in_world()

        center = [(top[0]-low[0]) / 2,(top[1]-low[1]) / 2,(top[2]-low[2]) / 2]
        head_pos =[patient_df[patient_df['plane'] == "yz"]['z'].values[0],
                    patient_df[patient_df['plane'] == "xz"]['x'].values[0],
                    patient_df[patient_df['plane'] == "yz"]['y'].values[0]]

        # get head position relative to ct image
        head_diff = (center[0] - head_pos[0], center[1] - head_pos[1],  center[2] - head_pos[2])
        
        # Create output directory
        if not os.path.exists(patient_output_path):
            os.makedirs(patient_output_path, exist_ok=True)

        # linear
        mu_xyz = [0, 0, 0]
        sigma_xyz = 8
        cov_xyz = [[sigma_xyz**2, 0, 0], [0, sigma_xyz**2, 0],[0, 0, sigma_xyz**2]] 

        # Angular
        mu_abg = [0, 0, 0]
        sigma_abg = 20
        cov_abg = [[sigma_abg**2, 0, 0], [0, sigma_abg**2, 0],[0, 0, sigma_abg**2]]
        

        num_linear = 2 ** 6
        num_angular = 2 ** 7

        samples_linear = np.random.multivariate_normal(mu_xyz, cov_xyz, num_linear)
        samples_angular = np.random.multivariate_normal(mu_abg, cov_abg, num_angular)

        for linear_comb in samples_linear:
            for angular_comb in samples_angular: 
                sampled_file_path = os.path.join(patient_output_path, f"{file_name.split('_')[0]}_{linear_comb[0]}_{linear_comb[1]}_{linear_comb[2]}_{angular_comb[0]}_{angular_comb[1]}_{angular_comb[2]}.png")
                # Because in Deep DRR, vertical is -x to +x... 
                g.deepdrr_run(x = head_diff[0] + linear_comb[0],
                                y = head_diff[1] + linear_comb[1],
                                z = head_diff[2] + linear_comb[2] ,
                                a = angular_comb[0],
                                b = angular_comb[1],
                                g = angular_comb[2],
                                file_path = sampled_file_path)
                image_info_csv.append([file_name.split("_")[0], linear_comb[0], linear_comb[1], linear_comb[2], angular_comb[0],angular_comb[1],angular_comb[2],sampled_file_path])

                    # sampled_file_side_path = os.path.join(patient_output_path, "side", f"{file_name.split('_')[0]}_side_{x}_{y}_{alpha + 90}_{beta}_{gamma}.png")
                    # g.deepdrr_run(x = head_diff[0] + x,
                    #                 y = head_diff[1] + y,
                    #                 z = head_diff[2],
                    #                 a = 90 + alpha,
                    #                 b = beta,
                    #                 g = gamma,
                    #                 file_path = sampled_file_side_path)      
                                
                    # image_info_csv.append([file_name.split("_")[0] , "side", head_diff[0] + x, head_diff[1] + y, head_diff[2], alpha + 90, beta, gamma, sampled_file_side_path])


        csv_path = os.path.join(output_path, f"simulated_angle_{sys.argv[1]}.csv")

        df_new = pd.DataFrame(image_info_csv, columns=['patient', 'x', 'y', 'z', 'a','b','g','file_path'])

        if os.path.exists(csv_path):
            df_new.to_csv(csv_path, mode='a', header=False, index=True)
        else:
            df_new.to_csv(csv_path, mode='w', header=True, index=True)