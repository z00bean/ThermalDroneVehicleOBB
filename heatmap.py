# DID not work for OBB. 
# Seg, BB.
# conda activate yv8.1.224
from ultralytics import YOLO
from ultralytics.solutions import heatmap
import cv2

'''
/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/05312023_North-videos/DJI_20230531200344_0001_T-1_45-2_15.MP4
/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/Medford-South_05232023_FL4_1059/DJI_20230523223312_0003_T-10_55-11_55.MP4
/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/South_05312023_FL0_0000-comp/DJI_0001.mov
/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/SOUTH-6-6-2023SouthDroneDanvers-comp/DJI_0009-5_55-6_30.mp4
'''

model = YOLO("yv8.1.224/runs/segment/train-seg-m-p2/weights/best.pt")
#cap = cv2.VideoCapture("/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/SOUTH-6-6-2023SouthDroneDanvers-comp/DJI_0009-5_55-6_30.mp4")
#cap = cv2.VideoCapture("/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/South_05312023_FL0_0000-comp/DJI_0001.mov")
#cap = cv2.VideoCapture("/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/Medford-South_05232023_FL4_1059/DJI_20230523223312_0003_T-10_55-11_55.MP4")
cap = cv2.VideoCapture("/media/zubin/Stuff1/DATA/TRANSPORT/THERMAL/DRONE-Workzone/Thermal-drone/v1/VIDEOS/05312023_North-videos/DJI_20230531200344_0001_T-1_45-2_15.MP4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Video writer
video_writer = cv2.VideoWriter("DJI_20230531200344_0001_T-1_45-2_15-nodecay.mp4",
                               cv2.VideoWriter_fourcc(*'mp4v'),
                               fps,
                               (w, h))

# Init heatmap
heatmap_obj = heatmap.Heatmap()
heatmap_obj.set_args(colormap=cv2.COLORMAP_PARULA,
                     imw=w,
                     imh=h,
                     view_img=True,
                     shape="circle",
                     decay_factor=1.0,#0.99,
                     classes_names=model.names)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    tracks = model.track(im0, persist=True, show=False)

    im0 = heatmap_obj.generate_heatmap(im0, tracks)
    video_writer.write(im0)

cap.release()
video_writer.release()
cv2.destroyAllWindows()
