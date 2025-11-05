# imgTo3dModel — zero123plus wrapper

## Overview

Project to create a 3D model from a provided image or images.

This repo provides a starter wrapper to run the Zero123Plus diffusion-based
multi-view generator and glue it into a small pipeline that can batch-process
folders, optionally export meshes (placeholder), and provide a simple Gradio
GUI.

## Setup

1. Create a Python venv (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt

   ```

1. Clone or install zero123plus correctly. If using remote weights, your from_pretrained call may try to download from Hugging Face.

1. (Optional) Install zero123plus in editable mode if you cloned it locally:
   pip install -e ../zero123plus

Usage
Single image:
python imgTo3dModel.py path/to/image.jpg outputs/ --steps 50
Folder (batch):
python imgTo3dModel.py path/to/folder outputs/ --mesh --batch-size 2
Start the GUI:
python gui.py
