## Prerequisites

- **Blender 3.4** — Add the exe folder to your `PATH`  
- **CUDA 12.1** — Add to your `PATH`  
- **Rokoko's Blender plugin** — Installed  
- **Python 3.10**

---

## Packages required:

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
# In the GVHMR folder, install the requirements:
pip install -r requirements.txt

# Ensure the 'av' package is version 13.0.0:
pip install av==13.0.0

# Inside the GVHMR folder, run:
pip install -e .

# Then, go inside the python3d folder and run:
python setup.py install




