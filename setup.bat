@echo off

echo Installing packages...
pip install torch==2.3.0+cu121 torchvision==0.18.0+cu121 torchaudio==2.3.0 --extra-index-url https://download.pytorch.org/whl/cu121
pip install fvcore iopath
pip install av==13.0.0

echo Installing GVHMR requirements
cd /d "%~dp0GVHMR"
pip install -r requirements.txt
echo Installing GVHMR as editable
pip install -e .

echo Installing pytorch3d
cd /d pytorch3d
python setup.py install

echo Done!
pause
