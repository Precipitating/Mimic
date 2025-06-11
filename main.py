from decord import VideoReader, cpu



def main():
    input = "video_input/lol.mp4"
    vr = VideoReader(input, ctx=cpu())



if __name__ == "__main__":
    main()