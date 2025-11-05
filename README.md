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
Run from CLI:
python imgTo3dModel.py path/to/image_or_folder --backend triposr --format obj
Start the GUI:
python gui.py

Output Options
Default: TripoSR single-image mesh reconstruction ( .obj )
Optional: Instant-NGP for multi-view reconstruction ( --backend instantngp )
Choose output format via --format {obj, fbx, glb}

Notes
Ensure Instant-NGP binary is in your system PATH.
TripoSR works best for single images; Instant-NGP provides smoother, higher-fidelity meshes when trained on multi-view outputs.
