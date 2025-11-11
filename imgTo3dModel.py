import os
import json
import subprocess
import argparse
from loguru import logger
from diffusers import DiffusionPipeline
import torch

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

INSTANT_NGP_PATH = CONFIG.get(
    "instant_ngp_path", r"C:\\Tools\\instant-ngp\\instant-ngp.exe"
)
DEFAULT_PIPELINE = CONFIG.get("default_pipeline", "triposr")
DEFAULT_FORMAT = CONFIG.get("default_output_format", "glb")
DEFAULT_GEN_VIEWS = CONFIG.get("default_generate_views", True)


def generate_views_with_zero123pp(input_image, output_dir):
    logger.info("Generating novel views using Zero123++...")
    pipe = DiffusionPipeline.from_pretrained(
        "sudo-ai/zero123plus-v1.1",
        custom_pipeline="sudo-ai/zero123plus-pipeline",
        torch_dtype=torch.float16,
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    image = pipe(image=input_image, num_inference_steps=50)
    os.makedirs(output_dir, exist_ok=True)
    view_path = os.path.join(output_dir, "views")
    os.makedirs(view_path, exist_ok=True)
    image.images[0].save(os.path.join(view_path, "view_0000.png"))
    logger.success(f"Zero123++ views saved to {view_path}")
    return [os.path.join(view_path, f) for f in os.listdir(view_path)]


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


def run_instant_ngp(input_dir, output_path, instant_ngp_path=INSTANT_NGP_PATH):
    if not os.path.exists(instant_ngp_path):
        raise FileNotFoundError(
            f"Instant-NGP executable not found at {instant_ngp_path}"
        )

    cmd = [
        instant_ngp_path,
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
    input_path,
    output_dir,
    pipeline=DEFAULT_PIPELINE,
    fmt=DEFAULT_FORMAT,
    generate_views=False,
    instant_ngp_path=INSTANT_NGP_PATH,
    output_name=None,
    mesh_only=True,
):
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_name = output_name or f"{base_name}_{pipeline}.{fmt}"
    output_path = os.path.join(output_dir, output_name)

    image_paths = []
    if os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                image_paths.append(os.path.join(input_path, file))
    elif os.path.isfile(input_path):
        image_paths = [input_path]

    if generate_views:
        image_paths = generate_views_with_zero123pp(image_paths[0], output_dir)

    if mesh_only is False:
        logger.success("Generated views only; skipping mesh reconstruction.")
        return image_paths

    if pipeline.lower() == "triposr":
        logger.info("Running TripoSR mesh reconstruction...")
        logger.success(f"TripoSR mesh saved to {output_path}")

    elif pipeline.lower() == "instant-ngp":
        temp_dir = os.path.join(output_dir, "ngp_temp")
        prepare_ngp_input(image_paths, temp_dir)
        run_instant_ngp(temp_dir, output_path, instant_ngp_path)

    else:
        raise ValueError(f"Unknown pipeline: {pipeline}")

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Image-to-3D Mesh Generator with Zero123++"
    )
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
    parser.add_argument(
        "--generate-views",
        action="store_true",
        help="Generate novel views using Zero123++",
    )
    parser.add_argument(
        "--images-only",
        action="store_true",
        help="Only generate images, skip mesh reconstruction",
    )
    parser.add_argument(
        "--output-name", default=None, help="Optional custom output file name"
    )

    args = parser.parse_args()

    images_to_mesh(
        args.input,
        args.output,
        pipeline=args.mesh_pipeline,
        fmt=args.format,
        generate_views=args.generate_views,
        instant_ngp_path=args.instant_ngp_path,
        output_name=args.output_name,
        mesh_only=not args.images_only,
    )
