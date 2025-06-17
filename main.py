import subprocess
import sys
import flet as ft
from flet import *
import cv2
import os

def run_program(page, button, spinner, smpl_model_path, video_path, target_model_path, map_json_path, in_place_checkbox, output_dir):
    # Error checking
    if any(x[1] is None for x in [smpl_model_path, video_path, target_model_path, map_json_path]):
        print("[ERROR] One or more required inputs are missing.")
        return

    if output_dir[0] is None:
        print("[ERROR] Output directory not set.")
        return


    spinner.visible = True
    button.disabled = True
    page.update()
    # Construct path to pre-converted file
    video_basename = os.path.splitext(video_path[0])[0]  # filename without extension
    already_converted_path = os.path.join(
        os.getcwd(), 'GVHMR', 'outputs', 'demo', video_basename, 'hmr4d_results.pt_person-0.pkl'
    )

    print(f"[INFO] Checking for existing conversion: {already_converted_path}")

    # Get video frame count
    cap = cv2.VideoCapture(video_path[1])
    if not cap.isOpened():
        print(f"[ERROR] Failed to open video: {video_path[1]}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Convert video to SMPL animation if not already done
    if not os.path.exists(already_converted_path):
        video_to_animation = [
            sys.executable,
            "tools/demo/demo.py",
            "-s",
            f"--video={video_path[1]}"
        ]

        print("[INFO] Running video-to-animation conversion...")
        subprocess.run(video_to_animation, cwd='GVHMR', check=True)
        print("[INFO] Video successfully converted to SMPL animation.")
    else:
        print("[INFO] SMPL animation already exists. Skipping conversion.")

    # Retarget animation in Blender
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
        map_json_path[1],
        str(in_place_checkbox),
        output_dir
    ]

    print("[INFO] Running Blender animation retargeting...")
    subprocess.run(animation_to_blender, check=True)
    print("[INFO] Retargeting complete.")
    button.disabled = False
    spinner.visible = False
    page.update()

def main(page: ft.Page) -> None:
    page.title = "Mimic"
    page.window.width = 450
    page.window.height = 650
    page.window.resizable = False
    page.window.maximizable = False
    page.window.alignment = ft.alignment.center

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


    output_folder_text = Text("Output Folder:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    output_folder_path = [None]
    output_folder_picker = FilePicker(on_result= lambda e: on_dir_selected(e, output_folder_path, output_folder_text))
    output_folder_button = ElevatedButton(text= "Choose Output Directory",
                                          on_click= lambda _: output_folder_picker.get_directory_path(),
                                          icon= ft.Icons.FOLDER)


    in_place_checkbox_component = ft.Checkbox(label="In Place?", value=False)
    in_place_checkbox = Row([in_place_checkbox_component], alignment=MainAxisAlignment.CENTER)

    run_button = ElevatedButton(text= "Run", on_click= lambda e: run_program(page,
                                                                             run_button,
                                                                             spinner,
                                                                             smpl_model_path,
                                                                             video_file_path,
                                                                             target_model_path,
                                                                             bone_mapping_path,
                                                                             in_place_checkbox_component.value,
                                                                             output_folder_path[0]))

    spinner = ft.ProgressRing(height= 25, width = 25, visible = False)
    spinner_formatted = Container(content=Column([spinner],
                                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding= padding.only(top=10))

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

    # directory picker handler
    def on_dir_selected(e: ft.FilePickerResultEvent, path_store, title_ref):
        if e.path:
            path_store[0] = e.path
            print(e.path)
            title_ref.color = ft.Colors.GREEN
        else:
            if path_store[0] is None:
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

                output_folder_text,
                output_folder_picker,
                output_folder_button,

                ft.Divider(thickness=2),
                in_place_checkbox,
                ft.Divider(thickness=2),
                run_button,

                spinner_formatted




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