cd ../..
export VIDEO_DIR="/work/pi_yuanchang_xie_uml_edu/zubin/DATA/THERMAL/VIDEOS/Medford/Non-workzone-L3-S"
FILES=$(ls "$VIDEO_DIR"/*.mp4 | tr " " "?")
echo BEGIN
for f in $FILES
do
  echo "Processing $f file..."

  dest_file="runs/TRACK-Medford-NON-workZ-DictL"
  echo $(basename "$f")

  if [ -d "$dest_file/$(basename "$f")" ]; then
    # Destination file already exists, skip to the next file
    echo "Destination folder $dest_file already exists. Skipping."
    continue
  fi
  echo
  echo
  echo "$f"
  echo "yolo track model=/work/pi_yuanchang_xie_uml_edu/zubin/CODE/yolov8.0.137/runs/TRAIN_Medford_noMask-grndTherm/segVeh-Med_noMskTLD_n-grnTh-ep180/weights/best.pt source="$f" save=True save_txt=True conf=0.66 line_width=2 project="$dest_file"  name="$(basename "$f")" verbose=False"
  echo
  yolo track model=/work/pi_yuanchang_xie_uml_edu/zubin/CODE/yolov8.0.137/runs/TRAIN_Medford_noMask-grndTherm/segVeh-Med_noMskTLD_n-grnTh-ep180/weights/best.pt source="$f" save=True save_txt=True conf=0.66 line_width=2 project="$dest_file"  name="$(basename "$f")" verbose=False
  #OP_Vid=$(ls "$dest_file/$(basename "$f")"/*.avi| head -1)
  # Destination file does not exist, run ffmpeg command
  echo
  echo "ffmpeg -i "$dest_file/$(basename "$f")"/$(basename "$f" .mp4)".avi" -preset slow -crf 30 "$dest_file/$(basename "$f")"/$(basename "$f")""" -loglevel warning
  echo
  echo Parallely ffmpeg converting video and creating dict_labels
  ffmpeg -i "$dest_file/$(basename "$f")"/$(basename "$f" .mp4)".avi" -preset slow -crf 30 "$dest_file/$(basename "$f")"/$(basename "$f")"" -loglevel warning&
  { python yoloLabels2dict.py "$dest_file/$(basename "$f")"; rm -r "$dest_file/$(basename "$f")"/labels; echo "Deleted labels dir"; } &
  wait
  
  rm "$dest_file/$(basename "$f")"/$(basename "$f" .mp4)".avi"
  echo Done.. "$(basename "$f")"
  echo
  echo
done