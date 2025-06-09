from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
from google.genai import errors
from PIL import Image
import io
import base64
import os
import random
import json
import logging
import math
import copy
import tempfile
from functools import wraps
import asyncio # For asyncio.sleep

from flask_cors import CORS


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Enable CORS for all routes and origins
CORS(app)

# Configure Gemini API
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not found or is empty.")
gemini_client = genai.Client(api_key=gemini_api_key)

# Retry Decorator
def retry_on_transient_error(max_retries=3, delay_seconds=1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except errors.APIError as e:
                    is_transient = False
                    # Prioritize specific transient error types from the SDK
                    if isinstance(e, (errors.DeadlineExceededError,
                                      errors.InternalServerError,
                                      errors.ServiceUnavailableError,
                                      errors.ResourceExhaustedError)):
                        is_transient = True

                    if not is_transient and hasattr(e, 'code') and isinstance(e.code, int):
                         if e.code == 429 or e.code >= 500:
                            is_transient = True

                    if is_transient and attempt < max_retries - 1:
                        actual_delay = delay_seconds * (2**attempt)
                        logging.warning(f"Gemini API transient error in '{func.__name__}' (Attempt {attempt + 1}/{max_retries}, Type: {type(e).__name__}, Code: {getattr(e, 'code', 'N/A')}): {e}. Retrying in {actual_delay:.2f}s...")
                        await asyncio.sleep(actual_delay)
                    else:
                        logging.error(f"Gemini API Error in '{func.__name__}' (Attempt {attempt + 1}/{max_retries}, Type: {type(e).__name__}, Code: {getattr(e, 'code', 'N/A')}): {e}")
                        raise
            return None
        return wrapper
    return decorator


# flux_client = Client("black-forest-labs/FLUX.1-schnell", hf_token=os.environ.get("HF_TOKEN"))



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


@retry_on_transient_error()
async def _generate_background_api_call(prompt_str):
    response = await gemini_client.generate_content_async(
        model="models/gemini-2.0-flash-preview-image-generation",
        contents=prompt_str
    )
    if response.candidates and response.candidates[0].content.parts:
        image_part = response.candidates[0].content.parts[0]
        if image_part.inline_data and image_part.inline_data.data:
            image_data = image_part.inline_data.data
            return Image.open(io.BytesIO(image_data))
        else:
            raise ValueError("No image data (inline_data) found in the Gemini API response part.")
    else:
        raise ValueError("No candidates or parts found in the Gemini API response for image generation.")

async def generate_background(theme, color_palette, canvasWidth, canvasHeight):
    colors = ", ".join(color_palette)
    prompt = f"Create an abstract background banner with the theme '{theme}' and color palette: {colors}. The banner should be {canvasWidth}x{canvasHeight} pixels."
    logging.info(f"Initiating background generation for theme: {theme}, Resolution: {canvasWidth}x{canvasHeight}")
    try:
        generated_image = await _generate_background_api_call(prompt)
        logging.info(f"Successfully generated background for theme: {theme}")
        return generated_image
    except errors.APIError as e:
        logging.error(f"Gemini API Error in generate_background (Code: {getattr(e, 'code', 'N/A')}, Type: {type(e).__name__}): {e}")
        raise
    except ValueError as e:
        logging.error(f"ValueError in generate_background (likely response parsing): {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in generate_background: {e}")
        raise

def image_to_base64(pil_image, image_format="PNG"):
    buffered = io.BytesIO()
    pil_image.save(buffered, format=image_format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def round_percentages(template):
    for obj in template['objects']:
        for key in ['left', 'bottom', 'width', 'height']:
            if key in obj:
                value = obj[key]
                if isinstance(value, str) and value.endswith('%'):
                    numeric_value = float(value.strip('%'))
                    rounded_value = math.ceil(numeric_value)
                    obj[key] = f"{rounded_value}%"
                elif isinstance(value, (int, float)):
                    rounded_value = math.ceil(value)
                    obj[key] = f"{rounded_value}%"
    return template

@retry_on_transient_error()
async def _generate_template_api_call(prompt_parts, generation_config_dict):
    response = await gemini_client.generate_content_async(
        model="models/gemini-1.5-flash",
        contents=prompt_parts,
        generation_config=types.GenerationConfig(**generation_config_dict)
    )
    return parse_gemini_response(response.text)

async def generate_template_with_gemini(resolution, num_images):
    generation_config_dict = {
        "temperature": 1, "top_p": 0.95, "top_k": 64,
        "max_output_tokens": 8192, "response_mime_type": "text/plain",
    }
    prompt_parts = [
        "For given resolution and number of images, generate fabricjs object template that positions the image and text objects as per resolution in JSON fomat: (Return JSON only)",
        "input: - resolution: 1360x800\n- num_images: 1",
        "output: {        \"resolution\": \"1360x800\",        \"num_images\": 1,            \"objects\": [        {\"type\":\"text\",\"left\":\"7.86%\",\"bottom\":\"49.62%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":48,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Gill Sans MT\"},        {\"type\":\"text\",\"left\":\"7.44%\",\"bottom\":\"36.78%\",\"width\":\"48%\",\"height\":\"100%\",\"fontSize\":64,\"fill\":\"\",\"fontWeight\":\"bold\",\"fontStyle\":\"normal\",\"textAlign\":\"left\",\"text\":\"\",\"fontFamily\":\"Arial Black\"},        {\"type\":\"image\",\"left\":\"62%\",\"bottom\":\"7%\",\"width\":\"70%\",\"height\":\"70%\",\"src\":\"\"},        ]    }",
        f"input: - resolution: {resolution}\n- num_images: {num_images}",
        "output: ",
    ]
    logging.info(f"Initiating template generation for R:{resolution}, N:{num_images}")
    try:
        parsed_response = await _generate_template_api_call(prompt_parts, generation_config_dict)
        logging.debug(f"Successfully generated template for R:{resolution}, N:{num_images}. Response: {str(parsed_response)[:200]}")
        return parsed_response
    except errors.APIError as e:
        logging.error(f"Gemini API Error in generate_template_with_gemini (Code: {getattr(e, 'code', 'N/A')}, Type: {type(e).__name__}): {e}")
        raise
    except ValueError as e:
        logging.error(f"ValueError in generate_template_with_gemini (likely JSON parsing): {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in generate_template_with_gemini: {e}")
        raise

async def select_template(resolution, num_images):
    filtered_templates = []
    for template_item in TEMPLATES:
        if template_item['resolution'] == resolution and template_item['num_images'] == num_images:
            filtered_templates.append(template_item)
    if filtered_templates:
        return random.choice(filtered_templates)
    else:
        return await generate_template_with_gemini(resolution, num_images)

@retry_on_transient_error()
async def _generate_design_choices_api_call(api_contents, model_name="models/gemini-1.5-flash"):
    response = await gemini_client.generate_content_async(
        model=model_name,
        contents=api_contents
    )
    return response.text

async def generate_banner(promotion, theme, resolution, color_palette, pil_product_images):
    try:
        num_images = len(pil_product_images)
        has_atleast_one_potrait_image = False
        
        uploaded_product_files_for_api = []
        for pil_image in pil_product_images:
            img_width, img_height = pil_image.size
            if img_height > img_width:
                has_atleast_one_potrait_image = True

            buffered_product = io.BytesIO()
            image_format = pil_image.format if pil_image.format else "PNG"
            pil_image.save(buffered_product, format=image_format)
            mime_type = f"image/{image_format.lower()}"
            if mime_type == "image/jpg": mime_type = "image/jpeg"
            uploaded_product_files_for_api.append(types.Part(inline_data=types.Blob(mime_type=mime_type, data=buffered_product.getvalue())))

        selected_template_data = await select_template(resolution, num_images)
        template = round_percentages(copy.deepcopy(selected_template_data))
        
        if not has_atleast_one_potrait_image:
            for obj_item in template['objects']:
                if obj_item['type'] == 'image':
                    if 'bottom' in obj_item and 'left' in obj_item:
                        bottom = int(obj_item['bottom'].rstrip('%'))
                        left = int(obj_item['left'].rstrip('%'))
                        obj_item['bottom'] = str(min(100, bottom + 15)) + "%"
                        obj_item['left'] = str(max(0, left - 5)) + "%"

        width, height = map(int, resolution.split('x'))
        pil_background_image = await generate_background(theme, color_palette, width, height)
        background_image_base64 = image_to_base64(pil_background_image)

        buffered_bg = io.BytesIO()
        pil_background_image.save(buffered_bg, format="PNG")
        background_image_part = types.Part(inline_data=types.Blob(mime_type="image/png", data=buffered_bg.getvalue()))
        
        prompt_text = f"""
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
        api_contents = [prompt_text, background_image_part] + uploaded_product_files_for_api
        response_text = await _generate_design_choices_api_call(api_contents=api_contents) # Explicitly name arg
        
        logging.debug(f"Gemini API response for design choices: {response_text[:200]}")
        design_choices = parse_gemini_response(response_text)
        modified_template = apply_design_choices(template, design_choices, width, height, pil_product_images)

        modified_template['objects'].insert(0, {
            "type": "image", "left": "0%", "top": "0%",
            "width": "100%", "height": "100%",
            "src": f"data:image/png;base64,{background_image_base64}"
        })

        return modified_template
    except errors.APIError as e:
        logging.error(f"Gemini API Error in generate_banner (Code: {getattr(e, 'code', 'N/A')}, Type: {type(e).__name__}): {e}")
        raise
    except ValueError as e:
        logging.error(f"ValueError in generate_banner (e.g., image processing, response parsing): {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in generate_banner: {type(e).__name__} - {e}")
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

def apply_design_choices(template, choices, width, height, pil_product_images):
    image_index = 0
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
            if image_index < len(pil_product_images):
                pil_image = pil_product_images[image_index]
                image_format = pil_image.format if pil_image.format else "PNG"
                base64_image_data = image_to_base64(pil_image, image_format=image_format)

                mime_type = f"image/{image_format.lower()}"
                if mime_type == "image/jpg": mime_type = "image/jpeg"

                obj['src'] = f"data:{mime_type};base64,{base64_image_data}"
                image_index += 1
            else:
                obj['src'] = ''

    template['objects'] = [obj for obj in template['objects'] if obj['type'] != 'image' or obj['src']]
    template['width'] = width
    template['height'] = height
    return template

@app.route('/generate_banner', methods=['POST'])
async def create_banner():
    try:
        data = await request.get_json()
        promotion = data['promotion']
        theme = data['theme']
        resolution = data['resolution']
        color_palette = data['color_palette']
        image_data_list = data['images']

        pil_images_from_client = []
        for image_data_base64 in image_data_list:
            try:
                header, encoded = image_data_base64.split(",", 1)
            except ValueError:
                logging.warning(f"Malformed image_data_base64, attempting to decode directly: {image_data_base64[:30]}...")
                encoded = image_data_base64

            image_bytes = base64.b64decode(encoded)
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_images_from_client.append(pil_image)

        banner_data = await generate_banner(promotion, theme, resolution, color_palette, pil_images_from_client)
        return jsonify(banner_data)
    except errors.APIError as e:
        logging.error(f"Gemini API Error encountered in create_banner (Code: {getattr(e, 'code', 'N/A')}, Type: {type(e).__name__}): {e}")
        http_status = 500
        error_message = "An error occurred while communicating with the generative AI service."
        if isinstance(e, errors.ResourceExhaustedError):
            http_status = 429
            error_message = "The service is experiencing high demand or rate limits were exceeded. Please try again later."
        elif isinstance(e, (errors.InternalServerError, errors.ServiceUnavailableError, errors.DeadlineExceededError)):
            http_status = 503
            error_message = "The generative AI service is temporarily unavailable or a timeout occurred. Please try again later."
        elif isinstance(e, (errors.InvalidArgumentError, errors.PermissionDeniedError, errors.UnauthenticatedError, errors.NotFoundError)):
             http_status = 400
             error_message = f"A client-side or authentication error occurred: {type(e).__name__}. Please check your request and credentials."
        elif hasattr(e, 'code') and isinstance(e.code, int): # Fallback for other codes if present
            if e.code == 429:
                http_status = 429
                error_message = "Rate limit exceeded. Please try again later."
            elif e.code >= 500:
                http_status = 503
                error_message = "The generative AI service reported a server error. Please try again later."
        return jsonify({"error": error_message, "details": str(e)}), http_status
    except ValueError as e:
        logging.error(f"ValueError in create_banner (e.g., image decoding, response parsing): {str(e)}")
        return jsonify({"error": f"Invalid request or data: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Unexpected error in create_banner: {type(e).__name__} - {str(e)}")
        return jsonify({"error": "An unexpected internal error occurred.", "details": str(e)}), 500

@app.route('/')
async def index():
    return await render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)