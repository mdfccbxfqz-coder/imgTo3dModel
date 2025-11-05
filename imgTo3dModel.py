import os
import sys
import torch
import logging
import argparse
import subprocess
from pathlib import Path
from diffusers import DiffusionPipeline

# Optional imports for mesh reconstruction
try:
    import triposr
except ImportError:
    triposr = None

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_zero123_pipeline(model_id="sudo-ai/zero123plus-v1.1"):
    logger.info(f"Loading Zero123++ pipeline from {model_id}...")
    pipe = DiffusionPipeline.from_pretrained(
        model_id,
        custom_pipeline="sudo-ai/zero123plus-pipeline",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    ).to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe


def generate_views(pipe, image_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Generating novel views for {image_path}...")
    try:
        image = pipe(image_path).images[0]
        output_file = output_dir / (Path(image_path).stem + "_views.png")
        image.save(output_file)
        return output_file
    except Exception as e:
        logger.error(f"Error generating views for {image_path}: {e}")
        return None


def reconstruct_mesh_triposr(image_path, output_dir, fmt="obj"):
    if not triposr:
        logger.error("TripoSR not installed. Please install it with `pip install triposr`.\n")
        return
    logger.info(f"Reconstructing mesh with TripoSR for {image_path}...")
    try:
        mesh = triposr.reconstruct(image_path)
        out_path = Path(output_dir) / (Path(image_path).stem + f".{fmt}")
        mesh.export(out_path, file_type=fmt)
        logger.info(f"Mesh saved to {out_path}")
        return out_path
    except Exception as e:
        logger.error(f"TripoSR reconstruction failed: {e}")
        return None


def reconstruct_mesh_instantngp(image_folder, output_dir, fmt="obj"):
    logger.info("Running Instant-NGP for mesh reconstruction...")
    try:
        mesh_path = Path(output_dir) / f'instantngp_mesh.{fmt}'
        cmd = [
            "instant-ngp",
            f"--scene={image_folder}",
            "--train",
            "--save_mesh",
            f"--mesh_path={mesh_path}"
        ]
        subprocess.run(cmd, check=True)
        logger.info(f"Instant-NGP mesh reconstruction completed successfully: {mesh_path}")
        return mesh_path
    except Exception as e:
        logger.error(f"Instant-NGP reconstruction failed: {e}")
        return None


def process_input(input_path, output_dir, backend="triposr", fmt="obj"):
    input_path = Path(input_path)
    pipe = load_zero123_pipeline()

    if input_path.is_file():
        generated = generate_views(pipe, input_path, output_dir)
        if backend == "instantngp":
            reconstruct_mesh_instantngp(output_dir, output_dir, fmt=fmt)
        else:
            reconstruct_mesh_triposr(generated, output_dir, fmt=fmt)
    elif input_path.is_dir():
        for file in input_path.iterdir():
            if file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                generated = generate_views(pipe, file, output_dir)
                if backend == "instantngp":
                    reconstruct_mesh_instantngp(output_dir, output_dir, fmt=fmt)
                else:
                    reconstruct_mesh_triposr(generated, output_dir, fmt=fmt)
    else:
        logger.error("Invalid input path.")


def main():
    parser = argparse.ArgumentParser(description="Zero123++ Wrapper for Image-to-3D Mesh Conversion")
    parser.add_argument("input", help="Path to image file or folder")
    parser.add_argument("--output", default="outputs", help="Output directory")
    parser.add_argument("--backend", choices=["triposr", "instantngp"], default="triposr", help="Mesh reconstruction backend")
    parser.add_argument("--format", choices=["obj", "fbx", "glb"], default="obj", help="Output mesh file format")
    args = parser.parse_args()

    process_input(args.input, args.output, backend=args.backend, fmt=args.format)


if __name__ == "__main__":
    main()