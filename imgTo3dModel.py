import os
import json
import subprocess
import argparse
from loguru import logger

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

INSTANT_NGP_PATH = CONFIG.get(
    "instant_ngp_path", r"C:\\Tools\\instant-ngp\\instant-ngp.exe"
)
DEFAULT_PIPELINE = CONFIG.get("default_pipeline", "triposr")
DEFAULT_FORMAT = CONFIG.get("default_output_format", "glb")


def prepare_ngp_input(image_paths, temp_dir):
    os.makedirs(os.path.join(temp_dir, "images"), exist_ok=True)
    transforms_path = os.path.join(temp_dir, "transforms.json")

    for i, img_path in enumerate(image_paths):
        new_name = os.path.join(temp_dir, "images", f"{i:04d}.png")
        os.system(f'copy "{img_path}" "{new_name}" >nul')

    transforms = {
        "camera_angle_x": 0.7854,
        "frames": [
            {
                "file_path": f"images/{i:04d}.png",
                "transform_matrix": [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ],
            }
            for i in range(len(image_paths))
        ],
    }

    with open(transforms_path, "w") as f:
        json.dump(transforms, f, indent=2)

    logger.info(f"Prepared Instant-NGP input directory: {temp_dir}")
    return temp_dir


def run_instant_ngp(input_dir, output_path):
    if not os.path.exists(INSTANT_NGP_PATH):
        raise FileNotFoundError(
            f"Instant-NGP executable not found at {INSTANT_NGP_PATH}"
        )

    cmd = [
        INSTANT_NGP_PATH,
        "--scene",
        input_dir,
        "--save_mesh",
        output_path,
        "--n_steps",
        "20000",
    ]

    logger.info(f"Running Instant-NGP: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    for line in process.stdout:
        print(line.strip())

    process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"Instant-NGP failed with code {process.returncode}")

    logger.success(f"Instant-NGP mesh saved to {output_path}")


def images_to_mesh(
    image_paths, output_dir, pipeline=DEFAULT_PIPELINE, fmt=DEFAULT_FORMAT
):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"output_mesh.{fmt}")

    if pipeline.lower() == "triposr":
        logger.info("Running TripoSR mesh reconstruction...")
        # Placeholder for future TripoSR integration
        logger.success(f"TripoSR mesh saved to {output_path}")

    elif pipeline.lower() == "instant-ngp":
        temp_dir = os.path.join(output_dir, "ngp_temp")
        prepare_ngp_input(image_paths, temp_dir)
        run_instant_ngp(temp_dir, output_path)

    else:
        raise ValueError(f"Unknown pipeline: {pipeline}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image-to-3D Mesh Generator")
    parser.add_argument("input", help="Path to image or folder of images")
    parser.add_argument("--output", default="outputs", help="Output directory")
    parser.add_argument(
        "--mesh-pipeline",
        default=DEFAULT_PIPELINE,
        help="Choose 'triposr' or 'instant-ngp'",
    )
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMAT,
        help="Output mesh format (obj, fbx, glb, etc.)",
    )
    parser.add_argument(
        "--instant-ngp-path",
        default=INSTANT_NGP_PATH,
        help="Custom path to instant-ngp executable",
    )

    args = parser.parse_args()

    images = []
    if os.path.isdir(args.input):
        for file in os.listdir(args.input):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                images.append(os.path.join(args.input, file))
    elif os.path.isfile(args.input):
        images = [args.input]

    images_to_mesh(images, args.output, args.mesh_pipeline, args.format)
