import gradio as gr
from transformers import pipeline
from PIL import Image

# Load the Hugging Face image classification model
image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")

# Define function for Gradio
def classify_image(img):
    image = Image.fromarray(img)  # Convert numpy array to PIL image
    predictions = image_classifier(image)
    return {pred["label"]: float(pred["score"]) for pred in predictions}

# Create Gradio Interface
demo = gr.Interface(
    fn=classify_image,
    inputs=gr.Image(type="numpy", label="Upload an Image"),
    outputs=gr.Label(num_top_classes=5, label="Predictions"),
    title=" Hugging Face Image Classifier",
    description="Upload an image and let the Hugging Face Vision Transformer classify it."
)

# Launch locally (will also work in Hugging Face Spaces)
demo.launch()
