'''
Convert the oriented bounding box (OBB) parameters from the format class_id, x, y, length, breadth, angle to the format class_id, x1, y1, x2, y2, x3, y3, x4, y4.
'''

import os
import math

def convert_obb_to_corners(input_folder, output_folder):
    # Create the output directory if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # List all .txt files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            with open(input_path, 'r') as file:
                lines = file.readlines()
            
            with open(output_path, 'w') as file:
                for line in lines:
                    data = line.strip().split()
                    class_id = int(data[0])
                    cx, cy = float(data[1]), float(data[2])
                    length, breadth = float(data[3]), float(data[4])
                    angle = float(data[5])

                    # Convert angle to radians
                    angle_rad = math.radians(angle)

                    # Calculate the half dimensions
                    half_length = length / 2
                    half_breadth = breadth / 2

                    # Calculate corners
                    # Corner 1 (top-left)
                    x1 = cx - half_length * math.cos(angle_rad) + half_breadth * math.sin(angle_rad)
                    y1 = cy - half_length * math.sin(angle_rad) - half_breadth * math.cos(angle_rad)
                    # Corner 2 (top-right)
                    x2 = cx + half_length * math.cos(angle_rad) + half_breadth * math.sin(angle_rad)
                    y2 = cy + half_length * math.sin(angle_rad) - half_breadth * math.cos(angle_rad)
                    # Corner 3 (bottom-right)
                    x3 = cx + half_length * math.cos(angle_rad) - half_breadth * math.sin(angle_rad)
                    y3 = cy + half_length * math.sin(angle_rad) + half_breadth * math.cos(angle_rad)
                    # Corner 4 (bottom-left)
                    x4 = cx - half_length * math.cos(angle_rad) - half_breadth * math.sin(angle_rad)
                    y4 = cy - half_length * math.sin(angle_rad) + half_breadth * math.cos(angle_rad)

                    # Write the reformatted data to the new file
                    file.write(f"{class_id} {x1:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x3:.6f} {y3:.6f} {x4:.6f} {y4:.6f}\n")

if __name__ == "__main__":
    input_folder = 'val/labels-OLD'
    output_folder = 'val/labels'
    convert_obb_to_corners(input_folder, output_folder)

