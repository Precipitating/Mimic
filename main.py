import subprocess
import sys
import os



def main():
    video_path = os.getcwd() + "/video_input/lol.mp4"
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
        "smpl_to_blender.py"
     ]
    subprocess.run(video_to_animation, cwd='GVHMR')
    print("Converted to SMPL animation")
    subprocess.run(animation_to_blender)








if __name__ == "__main__":
    main()