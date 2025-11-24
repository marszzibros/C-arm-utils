import dicom2nifti
import os
import logging
import sys
import concurrent.futures
import subprocess

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("process_log_lower.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)

source_list = ["/netfiles/vaillab/raylab_biplane/", "/netfiles/vaillab/raw_carm/", "/netfiles/raylab_biplane"]
file_to_process = "COR_ST_HEAD-NECK"
output_folder = "/netfiles/vaillab/head_neck/"

def process_file(file_path, case_name):
    try:
        output_path = os.path.join(output_folder, f"{case_name}_{file_to_process}.nii")
        dicom2nifti.dicom_series_to_nifti(file_path, output_path, reorient_nifti=True)
        subprocess.run(["gzip", output_path], check=True)
        logging.info(f"Successfully processed {case_name} from {file_path}")
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        with open("log_lower.txt", "a") as log_file:
            log_file.write(f"Error processing {file_path}: {str(e)}\n")

MAX_WORKERS = 4

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = []
    for source in source_list:
        try:
            for case_num in os.listdir(source):
                case_path = os.path.join(source, case_num)
                if not os.path.isdir(case_path) or "case" not in case_num:
                    continue

                try:
                    patient = case_num.split(" ")[0]
                    file_path_spec1 = os.path.join(source, case_num, "omi", "incomingdir", patient, "STANDARD_HEAD-NECK-U-EXT", file_to_process)
                    file_path_spec2 = os.path.join(source, case_num, "omi", "incomingdir", patient, "STANDARD_HEAD-NECK", file_to_process)

                    if os.path.exists(file_path_spec1):
                        futures.append(executor.submit(process_file, file_path_spec1, patient))
                    elif os.path.exists(file_path_spec2):
                        futures.append(executor.submit(process_file, file_path_spec2, patient))
                    else:
                        logging.warning(f"File {file_to_process} not found for patient {patient} in {source}")

                except Exception as e:
                    logging.error(f"Error processing case {case_num} in {source}: {str(e)}")

        except Exception as e:
            logging.error(f"Error accessing source {source}: {str(e)}")

concurrent.futures.wait(futures)

logging.info("All processing completed.")
