# imgTo3dModel — zero123plus wrapper

## Overview

Project to create a 3D model from a provided image or images.

Overview:
This tool enables single-image or multi-image to 3D mesh generation. It uses Zero123++ for novel view synthesis and TripoSR or Instant-NGP for mesh reconstruction.

Key Features:
Optional view generation via Zero123++
TripoSR and Instant-NGP mesh reconstruction
Automatic output naming (inputname_triposr.glb)
Configurable Instant-NGP path
Live progress logs for Instant-NGP
Full CLI and GUI interfaces

Project structure:
imgTo3dModel/
├── imgTo3dModel.py # Main wrapper script (CLI + core logic)
├── gui.py # Gradio GUI interface
├── config.json # Configuration file
├── requirements.txt # Python dependencies
├── README.md # Documentation
└── outputs/ # Generated image & mesh outputs

## Setup

config.json defines:
Path to the prebuilt Instant-NGP executable
Default mesh export format
Default mesh pipeline
Whether to auto-generate new views with Zero123++

1. Create a Python venv (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt

   ```

1. Clone or install zero123plus correctly. If using remote weights, your from_pretrained call may try to download from Hugging Face.

1. (Optional) Install zero123plus in editable mode if you cloned it locally:
   pip install -e ../zero123plus

Setting up Instant-NGP

1.  Download a prebuilt binary from https://github.com/NVlabs/instant-ngp/releases
2.  Extract it to a folder (e.g., C:\Tools\instant-ngp\)
3.  Update the config.json path accordingly.

Expected Directory Structure:
ngp_temp/
│── images/
│ ├── 0000.png
│ ├── 0001.png
│ └── ...
│── transforms.json

Usage

Run from CLI:

## Generate both images and mesh (TripoSR)

python imgTo3dModel.py input.jpg --generate-views

# Generate images only

python imgTo3dModel.py input.jpg --generate-views --images-only

# Use Instant-NGP and specify format + custom name

python imgTo3dModel.py input_folder/ --mesh-pipeline instant-ngp --format obj --output-name sample_mesh

Start the GUI:
python gui.py

GUI features:
Upload images
Select pipeline (TripoSR / Instant-NGP)
Choose format (obj / fbx / glb)
Toggle view generation (Zero123++)
Toggle mesh generation
Custom output name support

Output Options
Default: TripoSR single-image mesh reconstruction ( .obj )
Optional: Instant-NGP for multi-view reconstruction ( --backend instantngp )
Choose output format via --format {obj, fbx, glb}

Notes
Ensure Instant-NGP binary is in your system PATH.
TripoSR works best for single images; Instant-NGP provides smoother, higher-fidelity meshes when trained on multi-view outputs.
