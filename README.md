# Basic automation of video to 3D animation of your chosen rig, based on GVHMR, using Flet GUI
![image](https://github.com/user-attachments/assets/3f894ea4-b4f4-4020-9c36-6f5833e5cd8d)


## Prerequisites

- **Blender 3.4** — Add the exe folder to your `PATH`  
- **CUDA 12.1** — Add to your `PATH`  
- **Rokoko's Blender plugin** — Installed  
- **Python 3.10**

---

## Packages required (setup.bat does this automatically, place in same folder as exe):

```bash
conda install pytorch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 pytorch-cuda=12.1 -c pytorch -c nvidia
OR
pip install torch==2.3.0+cu121 torchvision==0.18.0+cu121 torchaudio==2.3.0 --extra-index-url https://download.pytorch.org/whl/cu121
```
```bash
conda install -c fvcore -c iopath -c conda-forge fvcore iopath
OR
pip install fvcore iopath
```

```bash
# In the GVHMR folder, install the requirements:
pip install -r requirements.txt

# Ensure the 'av' package is version 13.0.0:
pip install av==13.0.0

# Inside the GVHMR folder, run:
pip install -e .

# Then, go inside the python3d folder and run:
python setup.py install
```
# TARGET MODEL MUST BE IN T-POSE, NOT A-POSE
Mappings can be customized using this as a template:
```bash
[
    ["m_avg_root", ""],
    ["m_avg_Pelvis", "mixamorig:Hips"],
    ["m_avg_L_Hip", "mixamorig:LeftUpLeg"],
    ["m_avg_L_Knee", "mixamorig:LeftLeg"],
    ["m_avg_L_Ankle", "mixamorig:LeftFoot"],
    ["m_avg_L_Foot", "mixamorig:LeftToeBase"],
    ["m_avg_R_Hip", "mixamorig:RightUpLeg"],
    ["m_avg_R_Knee", "mixamorig:RightLeg"],
    ["m_avg_R_Ankle", "mixamorig:RightFoot"],
    ["m_avg_R_Foot", "mixamorig:RightToeBase"],
    ["m_avg_Spine1", "mixamorig:Spine"],
    ["m_avg_Spine2", "mixamorig:Spine1"],
    ["m_avg_Spine3", "mixamorig:Spine2"],
    ["m_avg_Neck", "mixamorig:Neck"],
    ["m_avg_Head", "mixamorig:Head"],
    ["m_avg_L_Collar", "mixamorig:LeftShoulder"],
    ["m_avg_L_Shoulder", "mixamorig:LeftArm"],
    ["m_avg_L_Elbow", "mixamorig:LeftForeArm"],
    ["m_avg_L_Wrist", "mixamorig:LeftHand"],
    ["m_avg_R_Collar", "mixamorig:RightShoulder"],
    ["m_avg_R_Shoulder", "mixamorig:RightArm"],
    ["m_avg_R_Elbow", "mixamorig:RightForeArm"],
    ["m_avg_R_Wrist", "mixamorig:RightHand"]

```
# Acknowledgements:
carlosedubarreto - SMPL to blender conversion script \
Rokoko - Blender animation retarget plugin  \
[GVHMR](https://github.com/zju3dv/GVHMR) - Video to SMPL animation







