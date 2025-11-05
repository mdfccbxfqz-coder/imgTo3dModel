import gradio as gr
from imgTo3dModel import process_input


def run_pipeline(input_path, backend, fmt):
    process_input(input_path, output_dir="outputs", backend=backend, fmt=fmt)
    return f"Processing complete. Mesh saved as .{fmt} in outputs folder."


demo = gr.Interface(
    fn=run_pipeline,
    inputs=[
        gr.Textbox(label="Image or Folder Path"),
        gr.Radio(["triposr", "instantngp"], value="triposr", label="Backend"),
        gr.Dropdown(["obj", "fbx", "glb"], value="obj", label="Output Format"),
    ],
    outputs="text",
    title="Img to 3D Model Wrapper",
)


demo.launch()