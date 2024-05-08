#!/bin/bash

# Define the directory containing the subdirectories
# srun -c 16 -G 1 --mem=64G -p gpu-preempt --pty bash
# conda activate yolov8.0.137
parent_dir="/work/pi_yuanchang_xie_uml_edu/zubin/CODE/yolov8.0.137/runs/TRACK-Danvers-NN-VehSeg-NON_Workzone-DICT"

# Loop through all subdirectories in the parent directory
for sub_dir in "$parent_dir"/*; do
    if [ -d "$sub_dir" ]; then
        # Check if the item is a directory
        echo "Running process-COUNT_per_hour.py on directory: $sub_dir"
        python v3-process-COUNT_per_hour-NON_WZ.py "$sub_dir"
    fi
done
