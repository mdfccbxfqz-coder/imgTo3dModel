import gradio as gr
import os
from imgTo3dModel import images_to_mesh, DEFAULT_PIPELINE, DEFAULT_FORMAT


def run_pipeline(input_images, pipeline, fmt):
    output_dir = "outputs"
    image_paths = []
    for img in input_images:
        path = os.path.join(output_dir, os.path.basename(img.name))
        img.save(path)
        image_paths.append(path)

    images_to_mesh(image_paths, output_dir, pipeline, fmt)
    result_file = os.path.join(output_dir, f"output_mesh.{fmt}")
    return result_file


with gr.Blocks(title="Img to 3D Model Generator") as demo:
    gr.Markdown("## 🧩 Image to 3D Mesh Generator")

    with gr.Row():
        input_images = gr.File(
            label="Upload Input Images", file_count="multiple", type="filepath"
        )

    with gr.Row():
        pipeline = gr.Radio(
            ["triposr", "instant-ngp"],
            value=DEFAULT_PIPELINE,
            label="Select Mesh Pipeline",
        )
        fmt = gr.Dropdown(
            ["obj", "fbx", "glb"], value=DEFAULT_FORMAT, label="Output Format"
        )

    generate_btn = gr.Button("Generate 3D Model")
    result_view = gr.File(label="Generated 3D Mesh")

    generate_btn.click(
        fn=run_pipeline, inputs=[input_images, pipeline, fmt], outputs=result_view
    )

demo.launch()
