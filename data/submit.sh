#!/bin/bash

#SBATCH --partition=dggpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --mem=2G
#SBATCH --cpus-per-task=4
#SBATCH --time=1-23:59:59
#SBATCH --job-name=carm

cd ${SLURM_SUBMIT_DIR}

source ~/.bashrc
module load cuda/cuda-11.2
conda activate new_UVMMC

cd ${SLURM_SUBMIT_DIR}

python3 generate_gaussian_xyzabg.py "$1"
