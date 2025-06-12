import subprocess
import sys
import os


def main():
    video_path = os.getcwd() + "/video_input/lol.mp4"
    command = [
        sys.executable,
        "tools/demo/demo.py",
        "-s",
        f"--video={video_path}"
    ]

    subprocess.run(command, cwd='GVHMR')




if __name__ == "__main__":
    main()