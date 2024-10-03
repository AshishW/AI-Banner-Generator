
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from PIL import Image
import io
import base64
import os
import random
import json
import logging
import math
from gradio_client import Client
import copy
import tempfile

from flask_cors import CORS
from huggingface_hub import login
login(token=os.environ.get("HF_TOKEN"))


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Enable CORS for all routes and origins
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


flux_client = Client("black-forest-labs/FLUX.1-schnell", hf_token=os.environ.get("HF_TOKEN"))



TEMPLATES = [
    # templates for 1360x800 resolution
    {
        "resolution": "1360x800",
        "num_images": 1,    
        "objects": [
        {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
        {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
        {"type":"image","left":"62%","bottom":"7%","width":"70%","height":"70%","src":""},
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 2,    
        "objects": [
            {"type":"text","left":"6.00%","bottom":"49.55%","width":"44.23%","height":"100%","fontSize":50,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Trebuchet MS"},
            {"type":"text","left":"6.00%","bottom":"33.03%","width":"45.91%","height":"100%","fontSize":60,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Verdana"},
            {"type":"image","left":"60.42%","bottom":"15.57%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"70.42%","bottom":"15.46%","width":"50%","height":"50%","src":""},
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 3,    
        "objects": [
            {"type":"text","left":"7.52%","bottom":"49.90%","width":"48.99%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.02%","bottom":"38.15%","width":"50.00%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"60.42%","bottom":"15.57%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"70.42%","bottom":"15.46%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"82.47%","bottom":"16.39%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 3,
        "objects": [
            {"type":"text","left":"25.62%","bottom":"82.94%","width":"50.55%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"25.50%","bottom":"71.60%","width":"50.30%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"50.00%","bottom":"11.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"30.00%","bottom":"10.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"41.00%","bottom":"11.00%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 4,
        "objects": [
            {"type":"text","left":"22.25%","bottom":"83.22%","width":"59.78%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"25.50%","bottom":"73.21%","width":"51.03%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"48.00%","bottom":"4.16%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"28.00%","bottom":"4.16%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"58.00%","bottom":"4.16%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"38.00%","bottom":"4.16%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 5,
        "objects": [
            {"type":"text","left":"28.50%","bottom":"83.55%","width":"48.00%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"30.00%","bottom":"70.96%","width":"48.00%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"23.00%","bottom":"10.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"33.00%","bottom":"10.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"55.25%","bottom":"10.43%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"44.00%","bottom":"10.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"51.50%","bottom":"9.20%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 6,
        "objects": [
            {"type":"text","left":"24.25%","bottom":"79.97%","width":"55.63%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"25.87%","bottom":"69.94%","width":"50.28%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"20.88%","bottom":"6.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"30.87%","bottom":"6.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"39.88%","bottom":"6.45%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"50.88%","bottom":"6.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"61.63%","bottom":"6.45%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"66.00%","bottom":"5.84%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1360x800",
        "num_images": 8,
        "objects": [
            {"type":"text","left":"19.25%","bottom":"81.76%","width":"65.31%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"21.25%","bottom":"71.73%","width":"59.44%","height":"100%","fontSize":64,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"12.63%","bottom":"4.16%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"22.63%","bottom":"4.16%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"31.88%","bottom":"4.61%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"42.63%","bottom":"4.16%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"52.63%","bottom":"4.61%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"62.00%","bottom":"4.00%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"71.38%","bottom":"4.61%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"80.63%","bottom":"4.16%","width":"40%","height":"40%","src":""}
        ]
    },
    # resolution 1920x600
    {
        "resolution": "1920x600",
        "num_images": 1,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":38,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":50,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"70%","bottom":"7%","width":"55%","height":"55%","src":""},
        ]
    },
    {
        "resolution": "1920x600",
        "num_images": 2,
        "objects": [
            {"type":"text","left":"7.52%","bottom":"49.90%","width":"48.99%","height":"100%","fontSize":38,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.02%","bottom":"38.15%","width":"48.00%","height":"100%","fontSize":50,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"65.00%","bottom":"9.00%","width":"50%","height":"50%","src":""},
            {"type":"image","left":"75.00%","bottom":"9.00%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1920x600",
        "num_images": 6,
        "objects": [
            {"type":"text","left":"32.49%","bottom":"83.35%","width":"58.46%","height":"100%","fontSize":30,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"35.13%","bottom":"73.31%","width":"53.78%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"30.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"36.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"42.69%","bottom":"7.45%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"48.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"54.44%","bottom":"7.45%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"60%","bottom":"6.84%","width":"35%","height":"35%","src":""}
        ]
    },
    {
        "resolution": "1920x600",
        "num_images": 5,
        "objects": [
            {"type":"text","left":"33.49%","bottom":"83.35%","width":"58.46%","height":"100%","fontSize":30,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"35.13%","bottom":"73.31%","width":"53.78%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"30.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"36.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"42.69%","bottom":"7.45%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"48.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"54.44%","bottom":"7.45%","width":"35%","height":"35%","src":""}
        ]
    },
    # resolution 1024x512
    {
        "resolution": "1024x512",
        "num_images": 2,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":30,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":40,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"60.42%","bottom":"15.57%","width":"45%","height":"45%","src":""},
            {"type":"image","left":"68.42%","bottom":"15.46%","width":"45%","height":"45%","src":""}
        ]
    },
    {
        "resolution": "1024x512",
        "num_images": 6,
        "objects": [
            {"type":"text","left":"32.00%","bottom":"83.31%","width":"58.46%","height":"100%","fontSize":20,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"35.63%","bottom":"73.27%","width":"53.78%","height":"100%","fontSize":32,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"25.69%","bottom":"6.00%","width":"30%","height":"30%","src":""},
            {"type":"image","left":"31.69%","bottom":"6.00%","width":"30%","height":"30%","src":""},
            {"type":"image","left":"37.69%","bottom":"6.45%","width":"30%","height":"30%","src":""},
            {"type":"image","left":"43.69%","bottom":"6.00%","width":"30%","height":"30%","src":""},
            {"type":"image","left":"49.44%","bottom":"6.45%","width":"30%","height":"30%","src":""},
            {"type":"image","left":"55.00%","bottom":"5.84%","width":"30%","height":"30%","src":""}
        ]
    },
    {
        "resolution": "1024x512",
        "num_images": 1,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":30,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":40,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"65%","bottom":"10%","width":"52%","height":"52%","src":""}
        ]
    },
    {
        "resolution": "1024x512",
        "num_images": 3,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":30,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":40,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"60.42%","bottom":"15.57%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"68.42%","bottom":"15.46%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"76.42%","bottom":"16.39%","width":"35%","height":"35%","src":""}
        ]
    },
    # res 1200x600
    {
        "resolution": "1200x600",
        "num_images": 1,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":36,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Gill Sans MT"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"65%","bottom":"10%","width":"50%","height":"50%","src":""}
        ]
    },
    {
        "resolution": "1200x600",
        "num_images": 5,
        "objects": [
            {"type":"text","left":"26.49%","bottom":"83.35%","width":"58.46%","height":"100%","fontSize":30,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"31.13%","bottom":"73.31%","width":"53.78%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"25.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"31.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"37.69%","bottom":"7.45%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"43.69%","bottom":"7.00%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"49.44%","bottom":"7.45%","width":"35%","height":"35%","src":""}
        ]
    },
    {
        "resolution": "1200x600",
        "num_images": 2,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":36,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Monotype Corsiva"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"60.42%","bottom":"15.57%","width":"40%","height":"40%","src":""},
            {"type":"image","left":"68.42%","bottom":"15.46%","width":"40%","height":"40%","src":""}
        ]
    },    
    {
        "resolution": "1200x600",
        "num_images": 3,
        "objects": [
            {"type":"text","left":"7.86%","bottom":"49.62%","width":"48%","height":"100%","fontSize":36,"fill":"","fontWeight":"bold","fontStyle":"","textAlign":"left","text":"","fontFamily":"Segoe Print"},
            {"type":"text","left":"7.44%","bottom":"36.78%","width":"48%","height":"100%","fontSize":48,"fill":"","fontWeight":"bold","fontStyle":"normal","textAlign":"left","text":"","fontFamily":"Arial Black"},
            {"type":"image","left":"60.42%","bottom":"15.57%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"68.42%","bottom":"15.46%","width":"35%","height":"35%","src":""},
            {"type":"image","left":"76.42%","bottom":"16.39%","width":"35%","height":"35%","src":""}
        ]
    } 
]




def generate_background(theme, color_palette, canvasWidth, canvasHeight):
    colors = ",".join(color_palette)
    prompt = f"abstract background image banner, background theme: {theme}, background colors: {colors}"
    print(f"Generating background image for: {prompt}")
    # flux_client = Client("black-forest-labs/FLUX.1-schnell")
    result = flux_client.predict(
        prompt=prompt,
        seed=0,
        randomize_seed=True,
        width=canvasWidth,
        height=canvasHeight,
        num_inference_steps=4,
        api_name="/infer"
    )
    return result

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def round_percentages(template):
    for obj in template['objects']:
        # Update 'left', 'top', 'width', 'height' values
        for key in ['left', 'bottom', 'width', 'height']:
            if key in obj:
                value = obj[key]
                if isinstance(value, str) and value.endswith('%'):
                    numeric_value = float(value.strip('%'))
                    rounded_value = math.ceil(numeric_value)
                    obj[key] = f"{rounded_value}%"
                elif isinstance(value, (int, float)):
                    # Assuming the value is in percentage and needs rounding
                    rounded_value = math.ceil(value)
                    obj[key] = f"{rounded_value}%"
    return template

def generate_template_with_gemini(resolution, num_images):
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )

    # structured prompt with few shot prompting
    response = model.generate_content([
    "For given resolution and number of images, generate fabricjs object template that positions the image and text objects as per resolution in JSON fomat: (Return JSON only)",
    "input: - resolution: 1360x800\n- num_images: 1",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 1,            \"objects\": [        {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},        {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},        {\"type\":\"image\",\"left\":\"62%\",\"bottom\":\"7%\",\"width\":\"70%\",\"height\":\"70%\",\"src\":\"\"},        ]    }",
    "input: - resolution: 1360x800\n- num_images: 1",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 1,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.52%\",\"bottom\":\"49.90%\",\"width\":\"48.99%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.02%\",\"bottom\":\"38.15%\",\"width\":\"48.00%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"70.34%\",\"bottom\":\"8.05%\",\"width\":\"70%\",\"height\":\"70%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1360x800\n- num_images: 2",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 2,            \"objects\": [            {\"type\":\"text\",\"left\":\"6.00%\",\"bottom\":\"49.55%\",\"width\":\"44.23%\",\"height\":\"100%\",\"fontSize\":50,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Trebuchet MS\"},            {\"type\":\"text\",\"left\":\"6.00%\",\"bottom\":\"33.03%\",\"width\":\"43.91%\",\"height\":\"100%\",\"fontSize\":60,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Verdana\"},            {\"type\":\"image\",\"left\":\"60.42%\",\"bottom\":\"15.57%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"70.42%\",\"bottom\":\"15.46%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},        ]    }",
    "input: - resolution: 1360x800\n- num_images: 3",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 3,            \"objects\": [            {\"type\":\"text\",\"left\":\"7.52%\",\"bottom\":\"49.90%\",\"width\":\"48.99%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.02%\",\"bottom\":\"38.15%\",\"width\":\"48.00%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"60.42%\",\"bottom\":\"15.57%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"70.42%\",\"bottom\":\"15.46%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"82.47%\",\"bottom\":\"16.39%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1360x800\n- num_images: 3",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 3,        \"objects\": [            {\"type\":\"text\",\"left\":\"31.37%\",\"bottom\":\"84.04%\",\"width\":\"48.00%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"29.13%\",\"bottom\":\"71.90%\",\"width\":\"48.00%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"49.25%\",\"bottom\":\"10.10%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"29.50%\",\"bottom\":\"9.82%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"40.88%\",\"bottom\":\"10.80%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1360x800\n- num_images: 3",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 5,        \"objects\": [            {\"type\":\"text\",\"left\":\"28.50%\",\"bottom\":\"83.55%\",\"width\":\"48.00%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"30.00%\",\"bottom\":\"70.96%\",\"width\":\"48.00%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"23.00%\",\"bottom\":\"10.00%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"33.00%\",\"bottom\":\"10.00%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"55.25%\",\"bottom\":\"10.43%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"44.00%\",\"bottom\":\"10.00%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"51.50%\",\"bottom\":\"9.20%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1360x800\n- num_images: 4",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 4,        \"objects\": [            {\"type\":\"text\",\"left\":\"22.25%\",\"bottom\":\"83.22%\",\"width\":\"59.78%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"25.50%\",\"bottom\":\"73.21%\",\"width\":\"51.03%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"48.00%\",\"bottom\":\"4.16%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"28.00%\",\"bottom\":\"4.16%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"58.00%\",\"bottom\":\"4.16%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"38.00%\",\"bottom\":\"4.16%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1360x800\n- num_images: 6",
    "output: {\n    \"resolution\": \"1360x800\",\n    \"num_images\": 6,\n    \"objects\": [\n        {\"type\":\"text\",\"left\":\"24.25%\",\"bottom\":\"79.97%\",\"width\":\"55.63%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Segoe Print\"},\n        {\"type\":\"text\",\"left\":\"25.87%\",\"bottom\":\"69.94%\",\"width\":\"50.28%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},\n        {\"type\":\"image\",\"left\":\"20.88%\",\"bottom\":\"6.00%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},\n        {\"type\":\"image\",\"left\":\"30.87%\",\"bottom\":\"6.00%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},\n        {\"type\":\"image\",\"left\":\"39.88%\",\"bottom\":\"6.45%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},\n        {\"type\":\"image\",\"left\":\"50.88%\",\"bottom\":\"6.00%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},\n        {\"type\":\"image\",\"left\":\"61.63%\",\"bottom\":\"6.45%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"},\n        {\"type\":\"image\",\"left\":\"66.00%\",\"bottom\":\"5.84%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"}\n    ]\n}",
    "input: - resolution: 1920x600\n- num_images: 6",
    "output: {        \"resolution\": \"1920x600\",        \"num_images\": 6,        \"objects\": [            {\"type\":\"text\",\"left\":\"32.49%\",\"bottom\":\"83.35%\",\"width\":\"58.46%\",\"height\":\"100%\",\"fontSize\":30,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Segoe Print\"},            {\"type\":\"text\",\"left\":\"35.13%\",\"bottom\":\"73.31%\",\"width\":\"53.78%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"30.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"36.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"42.69%\",\"bottom\":\"7.45%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"48.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"54.44%\",\"bottom\":\"7.45%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"60%\",\"bottom\":\"6.84%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1920x600\n- num_images: 1",
    "output: {        \"resolution\": \"1920x600\",        \"num_images\": 1,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":38,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":50,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"70%\",\"bottom\":\"7%\",\"width\":\"55%\",\"height\":\"55%\",\"src\":\"\"},        ]    }",
    "input: - resolution: 1024x512\n- num_images: 2",
    "output: {        \"resolution\": \"1024x512\",        \"num_images\": 2,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":30,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":40,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"60.42%\",\"bottom\":\"15.57%\",\"width\":\"45%\",\"height\":\"45%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"68.42%\",\"bottom\":\"15.46%\",\"width\":\"45%\",\"height\":\"45%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1024x512\n- num_images: 6",
    "output: {        \"resolution\": \"1024x512\",        \"num_images\": 6,        \"objects\": [            {\"type\":\"text\",\"left\":\"32.00%\",\"bottom\":\"83.31%\",\"width\":\"58.46%\",\"height\":\"100%\",\"fontSize\":20,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Segoe Print\"},            {\"type\":\"text\",\"left\":\"35.63%\",\"bottom\":\"73.27%\",\"width\":\"53.78%\",\"height\":\"100%\",\"fontSize\":32,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"25.69%\",\"bottom\":\"6.00%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"31.69%\",\"bottom\":\"6.00%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"37.69%\",\"bottom\":\"6.45%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"43.69%\",\"bottom\":\"6.00%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"49.44%\",\"bottom\":\"6.45%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"55.00%\",\"bottom\":\"5.84%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1024x512\n- num_images: 1",
    "output: {        \"resolution\": \"1024x512\",        \"num_images\": 1,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":30,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":40,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"65%\",\"bottom\":\"10%\",\"width\":\"52%\",\"height\":\"52%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1024x512\n- num_images: 3",
    "output: {        \"resolution\": \"1024x512\",        \"num_images\": 3,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":30,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":40,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"60.42%\",\"bottom\":\"15.57%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"68.42%\",\"bottom\":\"15.46%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"76.42%\",\"bottom\":\"16.39%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1024x480\n- num_images: 3",
    "output: {        \"resolution\": \"1024x480\",        \"num_images\": 3,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":28,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":36,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"60.42%\",\"bottom\":\"15.57%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"68.42%\",\"bottom\":\"15.46%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"76.42%\",\"bottom\":\"16.39%\",\"width\":\"30%\",\"height\":\"30%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1360x800\n- num_images: 8",
    "output: {        \"resolution\": \"1360x800\",        \"num_images\": 8,        \"objects\": [            {\"type\":\"text\",\"left\":\"19.25%\",\"bottom\":\"81.76%\",\"width\":\"65.31%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Segoe Print\"},            {\"type\":\"text\",\"left\":\"21.25%\",\"bottom\":\"71.73%\",\"width\":\"59.44%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"12.63%\",\"bottom\":\"4.16%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"22.63%\",\"bottom\":\"4.16%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"31.88%\",\"bottom\":\"4.61%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"42.63%\",\"bottom\":\"4.16%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"52.63%\",\"bottom\":\"4.61%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"62.00%\",\"bottom\":\"4.00%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"71.38%\",\"bottom\":\"4.61%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"80.63%\",\"bottom\":\"4.16%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1920x600\n- num_images: 5",
    "output: {        \"resolution\": \"1920x600\",        \"num_images\": 5,        \"objects\": [            {\"type\":\"text\",\"left\":\"33.49%\",\"bottom\":\"83.35%\",\"width\":\"58.46%\",\"height\":\"100%\",\"fontSize\":30,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Segoe Print\"},            {\"type\":\"text\",\"left\":\"35.13%\",\"bottom\":\"73.31%\",\"width\":\"53.78%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"30.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"36.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"42.69%\",\"bottom\":\"7.45%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"48.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"54.44%\",\"bottom\":\"7.45%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1200x600\n- num_images: 1",
    "output: {        \"resolution\": \"1200x600\",        \"num_images\": 1,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":36,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"65%\",\"bottom\":\"10%\",\"width\":\"50%\",\"height\":\"50%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1200x600\n- num_images: 5",
    "output: {        \"resolution\": \"1200x600\",        \"num_images\": 5,        \"objects\": [            {\"type\":\"text\",\"left\":\"26.49%\",\"bottom\":\"83.35%\",\"width\":\"58.46%\",\"height\":\"100%\",\"fontSize\":30,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Segoe Print\"},            {\"type\":\"text\",\"left\":\"31.13%\",\"bottom\":\"73.31%\",\"width\":\"53.78%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"25.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"31.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"37.69%\",\"bottom\":\"7.45%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"43.69%\",\"bottom\":\"7.00%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"49.44%\",\"bottom\":\"7.45%\",\"width\":\"35%\",\"height\":\"35%\",\"src\":\"\"}        ]    }",
    "input: - resolution: 1200x600\n- num_images: 2",
    "output: {        \"resolution\": \"1200x600\",        \"num_images\": 2,        \"objects\": [            {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":36,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Monotype Corsiva\"},            {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},            {\"type\":\"image\",\"left\":\"60.42%\",\"bottom\":\"15.57%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"},            {\"type\":\"image\",\"left\":\"68.42%\",\"bottom\":\"15.46%\",\"width\":\"40%\",\"height\":\"40%\",\"src\":\"\"}        ]    }",
    f"input: - resolution: {resolution}\n- num_images: {num_images}",
    "output: ",
    ])
    print("generated Template:", parse_gemini_response(response.text))
    return parse_gemini_response(response.text);

def select_template(resolution, num_images):
    """
    Selects the appropriate template based on resolution and number of images.
    Falls back to a default template if no exact match is found.
    """
    filtered_templates = []
    for template in TEMPLATES:
        if template['resolution'] == resolution and template['num_images'] == num_images:
            # add to filtered templates
            filtered_templates.append(template)
    # if filtered templates are not empty, return a random template from filtered templates
    if filtered_templates:
        return random.choice(filtered_templates)
    else:
        return generate_template_with_gemini(resolution, num_images)
    

def generate_banner(promotion, theme, resolution, color_palette, image_data_list):
    try:
        num_images = len(image_data_list)
        # print("Number of images: ", num_images)

        has_atleast_one_potrait_image = False

        uploaded_files = []
        for image_data in image_data_list:
            # Convert base64 to bytes and upload each image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_file.write(base64.b64decode(image_data.split(",")[1]))
                temp_file_path = temp_file.name  
            with Image.open(temp_file_path) as temp_image:
                img_width, img_height = temp_image.size
                if img_height >img_width:
                    has_atleast_one_potrait_image = True
            uploaded_file = genai.upload_file(temp_file_path) 
            uploaded_files.append(uploaded_file)
            os.remove(temp_file_path)
        
        
        selected_template = select_template(resolution, num_images)
        template = round_percentages(copy.deepcopy(selected_template))
        
        # modifying the current template position of images if all images are of landscape resolution
        if not has_atleast_one_potrait_image:
            for obj in template['objects']:
                if obj['type'] == 'image':
                    if 'bottom' in obj and 'left' in obj:
                        bottom = int(obj['bottom'].rstrip('%'))
                        left = int(obj['left'].rstrip('%'))
                        obj['bottom'] = str(min(100, bottom + 15)) + "%" #inc by 15%
                        obj['left'] = str(max(0, left - 5)) + "%" #dec by 5%

        width, height = map(int, resolution.split('x'))

        # Generate background image
        background_image_path = generate_background(theme, color_palette, width, height)[0]
        background_image_base64 = image_to_base64(background_image_path)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(base64.b64decode(background_image_base64))
            temp_file_path = temp_file.name  
            background_image_file = genai.upload_file(temp_file_path)  # Upload background image
        os.remove(temp_file_path)

        
        prompt = f"""
        Create a banner design based on the following:
        Template: {template['objects']}
        Promotion: {promotion}
        Theme: {theme}
        Resolution: {width}x{height}
        Background image: <the first image is background image of banner design>
        Product images: <the images except the first one are product images of banner design>
        Color Palette: {color_palette} (background image may consist of combination of these colors)

        Return JSON only:
        {{
        "backgroundImage": <concise and brief description of background image>,
        "backgroundColors": [hex values of colors present in the first image as list],
        "products": <write name of each product seperated by ",">,
        "mainText": "<promotion text, keep it short>",
        "secondaryText": "<if applicable, max 7 words, be creative based on products>",
        "textColors": {{
            "mainText": "<hex color value for primary text based on backgroundColors>",
            "secondaryText": "< different hex color value for secondary text based on backgroundColors>"
        }}

        }}
        Apply design principles for readability and prominence. Return JSON only.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt, background_image_file] + uploaded_files ) #uploaded_files has input images
        

        logging.debug(f"Gemini API response: {response.text}")

        design_choices = parse_gemini_response(response.text)

        # Apply design choices 
        modified_template = apply_design_choices(template, design_choices, width, height, image_data_list)

        modified_template['objects'].insert(0, {
            "type": "image",
            "left": "0%",
            "top": "0%",
            "width": "100%",
            "height": "100%",
            "src": f"data:image/png;base64,{background_image_base64}"
        })

        background_image_base64 = None

        return modified_template
        # return responsive_template
    except Exception as e:
        logging.error(f"Error in generate_banner: {str(e)}")
        raise

def parse_gemini_response(response_text):
    try:
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {str(e)}")
        logging.error(f"Raw response: {response_text}")
        raise ValueError("Invalid JSON response from Gemini API")
    
def get_smallest_font_size(template):
    smallest_font_size = float('inf')
    for obj in template['objects']:
        if obj['type'] == 'text':
            if obj['fontSize'] < smallest_font_size:
                smallest_font_size = obj['fontSize']
    return smallest_font_size

def apply_design_choices(template, choices, width, height, image_data_list):
    # Reset image_index for each function call
    image_index = 0
    # compare font size of text objects and store the smallest one
    smallest_font_size = get_smallest_font_size(template)

    for obj in template['objects']:
        if obj['type'] == 'text':
            if 'mainText' in choices and obj['fontSize'] > smallest_font_size:
                obj['text'] = choices['mainText'] or ""
                obj['fill'] = choices['textColors'].get('mainText', '#000000')
            elif 'secondaryText' in choices and obj['fontSize'] <= smallest_font_size:
                obj['text'] = choices['secondaryText'] or ""
                obj['fill'] = choices['textColors'].get('secondaryText', '#000000')

            obj['fontFamily'] = obj.get('fontFamily', 'Arial')
            obj['fontSize'] = obj.get('fontSize', 20)
            obj['fontWeight'] = obj.get('fontWeight', 'normal')
            obj['fontStyle'] = obj.get('fontStyle', 'normal')
            obj['textAlign'] = obj.get('textAlign', 'left')

        elif obj['type'] == 'image':
            if image_index < len(image_data_list) and image_data_list[image_index]:
                obj['src'] = f"data:image/jpeg;base64,{image_data_list[image_index]}"
                image_index += 1
            else:
                # Remove the image object if no data is available
                obj['src'] = ''

    # Remove any image objects with empty src
    template['objects'] = [obj for obj in template['objects'] if obj['type'] != 'image' or obj['src']]

    template['width'] = width
    template['height'] = height

    return template

@app.route('/generate_banner', methods=['POST'])
def create_banner():
    try:
        data = request.json
        promotion = data['promotion']
        theme = data['theme']
        resolution = data['resolution']
        color_palette = data['color_palette']
        image_data_list = data['images']

        banner_data = generate_banner(promotion, theme, resolution, color_palette, image_data_list)
        return jsonify(banner_data)
    except Exception as e:
        logging.error(f"Error in create_banner: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)