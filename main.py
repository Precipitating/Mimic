import subprocess
import sys
import os
import flet as ft
from flet import *
import cv2

def run_program(smpl_model_path, video_path, target_model_path, map_json_path):
    if any(None in x for x in [smpl_model_path, video_path, target_model_path, map_json_path]):
        print("Not all inputs filled")
        return

    cap = cv2.VideoCapture(video_path[1])
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_to_animation = [
        sys.executable,
        "tools/demo/demo.py",
        "-s",
        f"--video={video_path[1]}"
    ]

    animation_to_blender = [
        "blender",
        "--background",
        "--python",
        "smpl_to_blender.py",
        "--",
        str(frame_count),
        video_path[0],
        smpl_model_path[1],
        target_model_path[1],
        map_json_path[1]


    ]
    subprocess.run(video_to_animation, cwd='GVHMR')
    print("Converted to SMPL animation")
    subprocess.run(animation_to_blender)

def main(page: ft.Page) -> None:
    page.title = "Mimic"
    page.window.width = 400
    page.window.height = 500
    page.window.resizable = False
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # TITLE
    title= Text("Mimic", theme_style=ft.TextThemeStyle.TITLE_LARGE, color= ft.Colors.WHITE)

    # INPUTS
    video_file_input = Text("Input Video:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    video_file_path = [None, None]
    video_file_picker = FilePicker(on_result= lambda e: on_file_selected(e,video_file_path, video_file_input))
    video_picker_button = ElevatedButton(text= "Choose Video",
                                         on_click= lambda _: video_file_picker.pick_files(
                                         allow_multiple=False,
                                         allowed_extensions=["mp4","avi","mov",'mkv','webm']),
                                         icon= ft.Icons.FOLDER)

    target_model_input = Text("Target Model:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    target_model_path = [None, None]
    target_model_picker = FilePicker(on_result= lambda e: on_file_selected(e,target_model_path, target_model_input))
    target_model_button = ElevatedButton(text= "Choose Model",
                                         on_click= lambda _: target_model_picker.pick_files(
                                         allow_multiple=False,
                                         allowed_extensions=["fbx"]),
                                         icon= ft.Icons.FOLDER)
    bone_mapping_input = Text("Bone Map:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    bone_mapping_path = [None, None]
    bone_mapping_picker = FilePicker(on_result= lambda e: on_file_selected(e,bone_mapping_path, bone_mapping_input))
    bone_mapping_button = ElevatedButton(text= "Choose Bone Map ",
                                         on_click= lambda _: bone_mapping_picker.pick_files(
                                         allow_multiple=False,
                                         allowed_extensions=["json"]),
                                         icon= ft.Icons.FOLDER)

    smpl_model_input = Text("SMPL Model:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    smpl_model_path = [None, None]
    smpl_model_picker = FilePicker(on_result= lambda e: on_file_selected(e,smpl_model_path, smpl_model_input))
    smpl_model_button = ElevatedButton(text= "Choose SMPL Model",
                                       on_click= lambda _: smpl_model_picker.pick_files(
                                       allow_multiple=False,
                                       allowed_extensions=["fbx"]),
                                       icon= ft.Icons.FOLDER)

    run_button = ElevatedButton(text= "Run", on_click= lambda _: run_program(smpl_model_path,video_file_path, target_model_path, bone_mapping_path))

    # file picker handler
    def on_file_selected(e: ft.FilePickerResultEvent, path, title_ref):
        if e.files:
            path[0] = e.files[0].name
            path[1] = e.files[0].path
            print(f'Path found: {path[1]}')
            print(path)
            title_ref.color = ft.Colors.GREEN
        else:
            if path is None:
                print("No path selected")
                title_ref.color = ft.Colors.RED

        page.update()



    main_container = Container(
        content = ft.Column(
    [
                title,
                ft.Divider(thickness= 2),

                smpl_model_input,
                smpl_model_picker,
                smpl_model_button,

                video_file_input,
                video_file_picker,
                video_picker_button,

                target_model_input,
                target_model_picker,
                target_model_button,


                bone_mapping_input,
                bone_mapping_picker,
                bone_mapping_button,

                ft.Divider(thickness=2),
                run_button


             ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing= 4

    ),
        expand=True,
        margin=10,
        border_radius=10,
        theme=ft.Theme(color_scheme_seed=ft.Colors.INDIGO),
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,



    )

    page.add(main_container)











if __name__ == "__main__":
    ft.app(target=main)