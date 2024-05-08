# python v2-process-COUNT_per_hour.py /media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/sample-output/Danvers-NN-VehSeg-Workzone/20230605_204359.mp4
# python v2-process-COUNT_per_hour.py /media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/sample-output/Danvers-NN-VehSeg-Workzone/20230601_014414.mp4
# # Saving frames with traj
# Change video_name.split('_')[0]) etc accordingly.
import cv2
import os
import argparse
import numpy as np
import glob
import copy
import math
import datetime

height, width = 0, 0
fps = -1.0
frame_number = 0

dict_veh_FramesLoc = {} #key: trackID. Value: List of list [[(frameNo, [(x1, y1), (x2, y2), ...])], [], [], ..., catID]
dict_category = {0:"Small", 1:"Medium", 2:"Large", 3:"Person"} #{0:"unk", 1:"Small", 2:"Medium", 3:"Large", 4:"Person"}

def save_frame_with_dot(video_path, frame_number, center_coord, listSegments, output_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Check if the requested frame number is within valid range
    if frame_number < 0 or frame_number >= total_frames:
        print(f"Error: Invalid frame number. Must be between 0 and {total_frames - 1}")
        cap.release()
        return

    # Set the capture to the desired frame number
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frame
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read frame")
        cap.release()
        return
    # Draw dot
    # Draw a circle with blue line borders of thickness of 2 px 
    frame = cv2.circle(frame, center_coord, radius=5, color=(255,255,0), thickness=-1)

    #Draw trajectory points: listSegments: [[f, [(seg pt lst), ..], cat], ...]
    g = 255
    for items in listSegments:
        pt_lst = items[1]
        pt = max(pt_lst, key=lambda point: point[1])
        if g > 0:
            g -= 3
        frame = cv2.circle(frame, pt, radius=2, color=(255,g,255), thickness=-1)
    # Draw vehicle seg poly in bright color
    seg_pts = np.asarray(listSegments[int(0.65 * fps)-4][1]) # same f_no as in main
    if len(listSegments[int(0.65 * fps)-4][1]) > 3: # sanity check
        frame = cv2.polylines(frame, np.int32([seg_pts]), isClosed=True, color=(48,200,135), thickness=2)

    # Save the modified frame as a JPG image
    cv2.imwrite(output_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80]) # jpg quality: [0, 100]

    # Release the video capture object
    cap.release()
    #print(f"Frame {frame_number} saved as {output_path}")

#len(dict_veh_FramesLoc[trkID][0]) = 3 -> [frame_no, [mask points], catID]
def create_dict_veh_FramesLoc(veh_labels_dir, dict_veh_FramesLoc):
    #global dict_veh_FramesLoc
    #Note: In opencv frame no. starts from 0.
    for item in os.listdir(veh_labels_dir):
        item_path = os.path.join(veh_labels_dir, item)
        if os.path.isfile(item_path) and item.lower().endswith('.txt'):
            f_no = int(item_path.split('_')[-1][:-4])
            #print(f_no)
            with open(item_path, 'r') as file:
                for line in file:
                    # YOLO format: clsID x1 y1 x2 y2 x3 y3... trackID
                    num_list = line.split()
                    # If trackID not present in line, ignore.
                    if '.' in num_list[-1]: # last item is not an integer trackID
                        continue
                    
                    trackID = int(num_list[-1])
                    catID = int(num_list[0])
                    pts_lst = num_list[1:-1]
                    pts_lst_tpl = [(int(float(pts_lst[i]) * width), int(float(pts_lst[i + 1]) * height)) for i in range(0, len(pts_lst), 2)]
                    #print(pts_lst_tpl) #[(080.1562, 044.5312), (0.810938, 0.457031), (0.810938, 0.447266), (0.809375, 0.445312)]
                    #TO DO: Maybe check if polygon is single blob
                    #Check if detectiton not spurrious
                    if len(pts_lst_tpl) > 280 or len(pts_lst_tpl) < 3:
                        continue
                    if trackID in dict_veh_FramesLoc:
                        dict_veh_FramesLoc[trackID].append([f_no, pts_lst_tpl, catID]) 
                    else:
                        dict_veh_FramesLoc[trackID] = [[f_no, pts_lst_tpl, catID]]
    return dict_veh_FramesLoc #working
    

# Create an argument parser
parser = argparse.ArgumentParser(description="Save a specific frame from a video with a horizontal line.")
# Add arguments to the parser
parser.add_argument("veh_folder_path", help="Path to the input video file")

# Parse the command-line arguments
args = parser.parse_args()

# Input parameters
veh_folder_path = args.veh_folder_path


video_name = veh_folder_path.split('/')[-1] #Video file name: because foldername is same as video name.
video_path = os.path.join(veh_folder_path, video_name)

output_folder = "out-count-Danvers_MA-ALL-Unity-v3" #must exist
#Folder by 30 min or hour
# Check if the folder already exists: date_dir/hour_dir
output_folder = os.path.join(output_folder, video_name.split('_')[0])
#checking date folder
if not os.path.exists(output_folder):
    # Create the folder
    os.mkdir(output_folder)
    print(f"Folder '{output_folder}' created successfully.")
else:
    print(f"Folder '{output_folder}' already exists.")
#check hour folder
output_folder = os.path.join(output_folder, video_name.split('_')[1][:2])
#_hr = (int(video_name.split('_')[1][:2]) + 1)%24
#output_folder = os.path.join(output_folder, str(_hr)) #increasing the hour by (_+1)%24. to adjust the 15 min, For this camera only, Danvers-NN
#checking date folder
if not os.path.exists(output_folder):
    # Create the folder
    os.mkdir(output_folder)
    print(f"Folder '{output_folder}' created successfully.")
else:
    print(f"Folder '{output_folder}' already exists.")

output_txt_file = os.path.join(output_folder, "count.txt")
outputDetails_txt_file = os.path.join(output_folder, "count-"+video_name+"-DETAILED.txt")
with open(outputDetails_txt_file, "w") as file:
    file.write(f"FrameNo,Time,Category,TrackID\n")

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video file")
else:
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    cap.release()
print(f"Video name: {video_name}")
print(f"Width = {width}\nHeight = {height}\nFPS = {fps}\n")


# Process vehicle labels folder 
veh_label_folder = os.path.join(veh_folder_path, "labels") #labelsV-few #44002 count
'''
file_count = 0
# Iterate through all items in the veh folder
for item in os.listdir(veh_label_folder):
    item_path = os.path.join(veh_label_folder, item)
    if os.path.isfile(item_path):
        file_count += 1
print(f'Items in vehicle labels folder= {file_count}.')
file_count = 0
'''
dict_veh_FramesLoc = create_dict_veh_FramesLoc(veh_label_folder, dict_veh_FramesLoc) #key: trackID. Value: List of list [[(frameNo, [(x1, y1), (x2, y2),...])], [],..., catID]; [[frame_no, [mask points], catID], ...]
print(f'dict_veh_FramesLoc len = {len(dict_veh_FramesLoc.keys())}')
# COUNT vehicles moving from left to right.
countVehRelevant = 0
countVehAll = 0
countNeg = 0
countVehCategory = [0, 0, 0, 0] #small, med, large, person
wait_frame = int(0.65 * fps)
for trkID in sorted(dict_veh_FramesLoc.keys()):#dict_veh_FramesLoc.keys():
    countVehAll += 1
    if len(dict_veh_FramesLoc[trkID]) > wait_frame: #int(2 * fps):
        # Checking if vehicle going bottom to top:
        points_secHalf = dict_veh_FramesLoc[trkID][int(fps/4)][1]
        points_sec2 = dict_veh_FramesLoc[trkID][int(wait_frame-5)][1]
        topmost_point_secHalf = min(points_secHalf, key=lambda point: point[1])
        topmost_point_sec2 = min(points_sec2, key=lambda point: point[1])
        last_seg_ptsOfTraj = dict_veh_FramesLoc[trkID][-3][1]
        last_top_ptsOfTraj = min(last_seg_ptsOfTraj, key=lambda point: point[1])
        #print(f'topmost_point_sec2: {topmost_point_sec2}')
        # Lowest point of vehicle at 0.5 second
        lowest_point_secHalf = max(points_secHalf, key=lambda point: point[1]) #Ignore vehicles taking exit
        # Vehicle (Topmost point of) is moving left to right in from 0.3 sec to sec 2 of trajectory AND yVal_lowestPoint of vehicle above exit thresh (not taking exit)
        # vehicle moving up or vehicle moving right (exiting vehicles) 
        if (topmost_point_secHalf[1] < topmost_point_sec2[1]) or (last_top_ptsOfTraj[0] - topmost_point_secHalf[0] > 75): # 0: horizontal, [1]: vertical; #topmost_point_secHalf[0]>175 and
            countVehRelevant += 1
            #print("counted\n")
            #print(len(dict_veh_FramesLoc[trkID]))
            #print(len(dict_veh_FramesLoc[trkID][int(fps*2)]))
            #print(dict_veh_FramesLoc[trkID][int(fps*2)][2])
            if int(dict_veh_FramesLoc[trkID][wait_frame][2]) in [1, 2, 3, 4]:
                categoryID = int(dict_veh_FramesLoc[trkID][wait_frame][2]) - 1 # -1 to adjust for  0:unk; 0: small, 1:Med, 2: Large, 3: person
                countVehCategory[categoryID] += 1 # Considering vehicle category at 2 second mark.
                save_frame_with_dot(video_path, frame_number=dict_veh_FramesLoc[trkID][int(wait_frame-5)][0], center_coord=topmost_point_sec2, listSegments=dict_veh_FramesLoc[trkID], output_path=os.path.join(output_folder, str(f"{trkID:07d}")+"-"+str(dict_category[categoryID])+"-"+str(int(dict_veh_FramesLoc[trkID][int(fps/4)][0]/fps*60))+".jpg"))
                with open(outputDetails_txt_file, "a") as file:
                    file.write(f"{str(dict_veh_FramesLoc[trkID][int(wait_frame-5)][0])},{str(datetime.timedelta(seconds=int((dict_veh_FramesLoc[trkID][int(wait_frame-5)][0])/29.0)))},{str(dict_category[categoryID])},{str(trkID)}\n")
        else:
            countNeg += 1
            #dict_veh_FramesLoc[trkID][0][2]

print(f"countVehAll = {countVehAll}")    
print(f"countVehRelevant = {countVehRelevant}")
print(f"Vehicles not counted = {countNeg}")


with open(output_txt_file, "a") as file:
    file.write(f"Small:{countVehCategory[0]}\nMedium:{countVehCategory[1]}\nLarge:{countVehCategory[2]}\nPerson:{countVehCategory[3]}" + "\n")



