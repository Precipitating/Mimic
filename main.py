import subprocess
import sys
import flet as ft
from flet import *
import cv2
import os

"""
Returns the MEIPASS folder path if exists
Pyinstaller exe creates a temporary working directory in Temp, which houses
the code and packaged data.

Args:
    relative_path (string): The relative path converted from code directory to MEIPASS directory
Returns:
    string: MEIPASS path
"""
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

"""
Returns the ABSOLUTE path of where the exe is located
Returns:
    string: Absolute path of the exe directory
"""
def base_path():
    """Get path where the EXE is located"""
    return os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

"""
Responsible for the execution of the entire program
Converts SMPL animation data to blender
Then retargets the data to chosen target model
Imports a clone of target model and links the retargeted model animation data with clone
Exports the clone with the animation data - DONE
Args:
    debug_text (ft.Text):               Passed in to change the debug text to update progress of the conversion
    page (ft.Page):                     Used to update the program when any changes occur to debug_text, ElevatedButton or spinner
    button (ft.ElevatedButton):         Is the run program button, used to disable when running and re-enabled when done (or error)
    spinner (ft.ProgressRing):          Visible when program is running, and disabled is not
    smpl_model_path (string):           The path to the SMPL fbx model, passed through to blender processing for retargeting
    video_path (string):                Video path of the motion to mimic, passed through to video_to_animation to convert to SMPL data
    target_model_path (string):         The path to a custom user rig that the user wants to convert the animation to, used for blender processing
    map_json_path (string):             The json map that specifies the SMPL bone link to the custom rig (target_model_path), crucial for blender conversion via Rokoko
    in_place_checkbox (ft.Checkbox):    The checkbox which specifies if you want the animation to move around as the video shows, or stay in place
    output_dir (string):                The output directory, where the converted SMPL -> custom rig FBX file is outputted.
Returns:
    Nothing, early return if error

"""
def run_program(debug_text, page, button, spinner, smpl_model_path, video_path, target_model_path, map_json_path, in_place_checkbox, output_dir):
    # Error checking
    if any(x[1] is None for x in [smpl_model_path, video_path, target_model_path, map_json_path]):
        print("[ERROR] One or more required inputs are missing.")
        debug_text.value = "[ERROR] One or more required inputs are missing."
        page.update()
        return

    if output_dir is None:
        print("[ERROR] Output directory not set.")
        debug_text.value = "[ERROR] Output directory not set."
        page.update()
        return


    spinner.visible = True
    button.disabled = True

    # Construct path to pre-converted file
    video_basename = os.path.splitext(video_path[0])[0]  # filename without extension
    already_converted_path = os.path.join(
        base_path(), 'GVHMR', 'outputs', 'demo', video_basename, 'hmr4d_results.pt_person-0.pkl'
    )

    print(f"[INFO] Checking for existing conversion: {already_converted_path}")
    debug_text.value = f"[INFO] Checking for existing conversion: {already_converted_path}"
    page.update()

    # Get video frame count
    cap = cv2.VideoCapture(video_path[1])
    if not cap.isOpened():
        print(f"[ERROR] Failed to open video: {video_path[1]}")
        debug_text.value = f"[ERROR] Failed to open video: {video_path[1]}"
        page.update()
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Convert video to SMPL animation if not already done
    if not os.path.exists(already_converted_path):
        video_to_animation = [
            "python",
            os.path.join(base_path(),"GVHMR" ,"tools", "demo", "demo.py"),
            "-s",
            f"--video={video_path[1]}"
        ]

        print("[INFO] Running video-to-animation conversion...")
        debug_text.value = "[INFO] Running video-to-animation conversion..."
        page.update()

        try:
            subprocess.run(video_to_animation,cwd=os.path.join(base_path(), "GVHMR"), check=True)
        except Exception as e:
            debug_text.value = "ERROR"
            button.disabled = False
            spinner.visible = False
            return

        print("[INFO] Video successfully converted to SMPL animation.")
        debug_text.value = "[INFO] Video successfully converted to SMPL animation."
        page.update()
    else:
        print("[INFO] SMPL animation already exists. Skipping conversion.")
        debug_text.value = "[INFO] SMPL animation already exists. Skipping conversion."
        page.update()

    # Retarget animation in Blender
    animation_to_blender = [
        "blender",
        "--background",
        "--python",
        resource_path("smpl_to_blender.py"),
        "--",
        str(frame_count),
        video_path[0],
        smpl_model_path[1],
        target_model_path[1],
        map_json_path[1],
        str(in_place_checkbox),
        output_dir
    ]

    debug_text.value = "[INFO] Running Blender animation retargeting..."
    page.update()
    print("[INFO] Running Blender animation retargeting...")
    try:
        subprocess.run(animation_to_blender, check=True)
    except Exception as e:
        debug_text.value = "ERROR blender processing"
        button.disabled = False
        spinner.visible = False
        return
    debug_text.value = "[INFO] Retargeting complete."
    page.update()
    print("[INFO] Retargeting complete.")
    button.disabled = False
    spinner.visible = False
    page.update()


"""
The Flet GUI code
Args:
    page (ft.Page): The main entry point to display Flet components and modify properties.
"""
def main(page: ft.Page) -> None:
    page.title = "Mimic"
    page.window.width = 450
    page.window.height = 670
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
    ## TARGET MODEL
    target_model_input = Text("Target Model:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    target_model_path = [None, None]
    target_model_picker = FilePicker(on_result= lambda e: on_file_selected(e,target_model_path, target_model_input))
    target_model_button = ElevatedButton(text= "Choose Model",
                                         on_click= lambda _: target_model_picker.pick_files(
                                         allow_multiple=False,
                                         allowed_extensions=["fbx","obj"]),
                                         icon= ft.Icons.FOLDER)
    ## BONE MAPPING
    bone_mapping_input = Text("Bone Map:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    bone_mapping_path = [None, None]
    bone_mapping_picker = FilePicker(on_result= lambda e: on_file_selected(e,bone_mapping_path, bone_mapping_input))
    bone_mapping_button = ElevatedButton(text= "Choose Bone Map ",
                                         on_click= lambda _: bone_mapping_picker.pick_files(
                                         allow_multiple=False,
                                         allowed_extensions=["json"]),
                                         icon= ft.Icons.FOLDER)

    ## SMPL MODEL
    smpl_model_input = Text("SMPL Model:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    smpl_model_path = [None, None]
    smpl_model_picker = FilePicker(on_result= lambda e: on_file_selected(e,smpl_model_path, smpl_model_input))
    smpl_model_button = ElevatedButton(text= "Choose SMPL Model",
                                       on_click= lambda _: smpl_model_picker.pick_files(
                                       allow_multiple=False,
                                       allowed_extensions=["fbx"]),
                                       icon= ft.Icons.FOLDER)

    ## OUTPUT DIR
    output_folder_text = Text("Output Folder:", size=15, color= ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
    output_folder_path = [None]
    output_folder_picker = FilePicker(on_result= lambda e: on_dir_selected(e, output_folder_path, output_folder_text))
    output_folder_button = ElevatedButton(text= "Choose Output Directory",
                                          on_click= lambda _: output_folder_picker.get_directory_path(),
                                          icon= ft.Icons.FOLDER)


    ## IN PLACE CHECKBOX
    in_place_checkbox_component = Checkbox(label="In Place?", value=False)
    in_place_checkbox = Row([in_place_checkbox_component], alignment=MainAxisAlignment.CENTER)

    ## RUN BUTTON
    run_button = ElevatedButton(text= "Run", on_click= lambda e: run_program(
                                                                             error_text,
                                                                             page,
                                                                             run_button,
                                                                             spinner,
                                                                             smpl_model_path,
                                                                             video_file_path,
                                                                             target_model_path,
                                                                             bone_mapping_path,
                                                                             in_place_checkbox_component.value,
                                                                             output_folder_path[0]))


    ## DEBUG TEXT
    error_text = Text("Ready",visible=True, color = Colors.RED)

    ## PROGRESS SPINNER
    spinner = ProgressRing(height= 25, width = 25, visible= False)
    spinner_formatted = Container(content=Column([spinner],
                                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding= padding.only(top=10))

    """
    On file selected handler, stores the file path data in a List ([None,None]) 
    e.g [file name, file path]
    If no path has been outputted, title_ref will be red
    If selected before and cancelled, it won't change path.
    Args:
        e (ft.FilePickerResultEvent): The output result once the user has canceled or selected a file
        path (List): A list of None which is used to store the path and name of the selected file
        title_ref (ft.Text): Used to change the text color if selected file is correct (GREEN) or canceled (RED)
    """
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

    """
    On directory selected, stores the string in path_store[0] (List of [None])
    If no path has been outputted, title_ref will be red
    If selected before and cancelled, it won't change path.
    Args:
        e (ft.FilePickerResultEvent): The output result once the user has canceled or selected a file
        path_store (List): A list of None which is used to store the path and name of the selected file
        title_ref (ft.Text): Used to change the text color if selected directory (GREEN) or canceled (RED)
    """
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
                spinner_formatted,
                error_text




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