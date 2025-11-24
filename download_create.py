import dicom2nifti
import os
import threading
import zipfile
import sys

name_list = [sys.argv[1]]


file_to_process = ["BONE_H-N-UXT_3X3", "BONE_TORSO_3_X_3", "BONE_UEX-TOR_3X3"]
input_folder = "/netfiles/raylab_biplane/"
output_folder = "/netfiles/raylab_biplane/datasets/"

def process_file(file_path, name, case_name):
    try:

        dicom2nifti.dicom_series_to_nifti(file_path + name, output_folder + case_name + "_" + name, reorient_nifti=True) 
        
        os.system("gzip " + output_folder + case_name + "_" + name +".nii")
    except Exception as e:
        print(f"Attempt failed in {name}: {str(e)}")
        with open("log.txt", 'a') as log_file:
            log_file.write(f"Attempt failed in {name}: {str(e)}\n")


threads = []

for name in name_list:
    # zip file 

    name = str(name)
    try:
        
        
        if name[-3:] != 'zip' and '(1)' not in name:
            
            # check if it is already done
            file_path_spec = input_folder + name + "/omi/incomingdir/" + name + "/STANDARD_HEAD-NECK-U-EXT/"

            count = 0 
            for ct_name_bone in file_to_process:
                if not os.path.exists(f"{output_folder}{name}_{ct_name_bone}.nii.gz"):
                    count += 1
                    thread = threading.Thread(target=process_file, args=(file_path_spec, ct_name_bone, name))
                    thread.start()
                    threads.append(thread)
            if count == 0:
                with open("log.txt", 'a') as log_file:
                    log_file.write(f"{name}\n")
        # if zip file
        elif name[-3:] == 'zip' and '(1)' not in name:

            zip_path = input_folder + name
            # Extract the zip file
            if not os.path.exists(input_folder + name[:-4]):
                os.makedirs(input_folder + name[:-4])
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(input_folder + name[:-4])

            # check if it is already done
            file_path_spec = input_folder + name[:-4] + "/omi/incomingdir/" + name[:-4] + "/STANDARD_HEAD-NECK-U-EXT/"
            count = 0 
            for ct_name_bone in file_to_process:
                if not os.path.exists(f"{output_folder}{name[:-4]}_{ct_name_bone}.nii.gz"):
                    count += 1
                    thread = threading.Thread(target=process_file, args=(file_path_spec, ct_name_bone, name[:-4]))
                    thread.start()
                    threads.append(thread)
            if count == 0:
                with open("log.txt", 'a') as log_file:
                    log_file.write(f"{name}\n")
    except:
        with open("log.txt", 'a') as log_file:
            log_file.write(f"-{name}\n")

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All threads have finished.")

