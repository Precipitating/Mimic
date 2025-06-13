import subprocess
import sys
import os

import cv2


def main():
    video_path = os.getcwd() + "/video_input/kick.mp4"
    cap = cv2.VideoCapture(video_path)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_to_animation = [
        sys.executable,
        "tools/demo/demo.py",
        "-s",
        f"--video={video_path}"
    ]


    animation_to_blender = [
        "blender",
        "--background",
        "--python",
        "smpl_to_blender.py",
        "--",
        str(frame_count)
     ]
    #subprocess.run(video_to_animation, cwd='GVHMR')
    print("Converted to SMPL animation")
    subprocess.run(animation_to_blender)








if __name__ == "__main__":
    main()