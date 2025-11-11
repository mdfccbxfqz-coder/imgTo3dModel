import gradio as gr
import os
from imgTo3dModel import images_to_mesh, DEFAULT_PIPELINE, DEFAULT_FORMAT


def run_pipeline(input_images, pipeline, fmt, generate_views, mesh_only, output_name):
    output_dir = "outputs"
    image_paths = []
    for img in input_images:
        path = os.path.join(output_dir, os.path.basename(img.name))
        img.save(path)
        image_paths.append(path)

    result = images_to_mesh(
        image_paths[0] if len(image_paths) == 1 else output_dir,
        output_dir,
        pipeline=pipeline,
        fmt=fmt,
        generate_views=generate_views,
        output_name=output_name,
        mesh_only=not mesh_only,
    )

    if isinstance(result, list):
        return "\n".join(result)
    return result


with gr.Blocks(title="Img to 3D Model Generator") as demo:
    gr.Markdown("## 🧩 Image to 3D Mesh Generator (Zero123++, TripoSR, Instant-NGP)")

    with gr.Row():
        input_images = gr.File(
            label="Upload Input Image(s)", file_count="multiple", type="filepath"
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

    with gr.Row():
        generate_views = gr.Checkbox(label="Generate Views (Zero123++)", value=True)
        mesh_only = gr.Checkbox(
            label="Generate Mesh (unchecked = images only)", value=True
        )
        output_name = gr.Textbox(
            label="Custom Output Name (optional)",
            placeholder="Leave blank for auto-naming",
        )

    generate_btn = gr.Button("Generate")
    result_view = gr.File(label="Generated Output")

    generate_btn.click(
        fn=run_pipeline,
        inputs=[input_images, pipeline, fmt, generate_views, mesh_only, output_name],
        outputs=result_view,
    )

demo.launch()
