## How this works:

![ArtVisionX Architecture](./static/ArtVisionX_Architecture.png)

This Flask app dynamically generates image banners based on user-provided themes, color palettes, and target resolutions. It leverages the **Gemini** large language model (LLM) for text-based tasks and utilizes the **Flux** model for image generation. Here's a detailed breakdown of its system design:

1. **Template Management:**
    - The app maintains a predefined set of `TEMPLATES` (stored as a list of dictionaries), where each dictionary represents a template layout for banners. These templates define object placements, including text and images, for a variety of target resolutions and image counts. Each template acts as a blueprint that ensures consistency in design while offering flexibility for different layout needs.
    - The `select_template` function is responsible for selecting the most appropriate template based on the user's requested resolution and the number of images to be displayed. It searches for an exact match but may fallback to a closest match or dynamically generate one if no perfect template is available, ensuring adaptability.
    - The `round_percentages` function is used to fine-tune the selected template by adjusting percentage-based dimensions (like width, height, or margins) to the nearest integer. This step ensures pixel-perfect alignment of elements, avoiding any rendering inaccuracies across different screen resolutions.

2. **LLM-powered Template Generation:**
    - If a suitable template isn't found, `generate_template_with_gemini` dynamically creates one using structured prompt to the Gemini API.
    - It uses few-shot prompting, providing examples of input (resolution, image count) and desired JSON output (template structure).
    - The LLM generates a JSON template, which is then parsed using `parse_gemini_response`. This function likely handles JSON formatting and error handling.

3. **Background Image Generation:**
    - The `generate_background` function handles background creation.
    - It takes the theme, color palette, canvas width, and height as input.
    - It constructs a prompt for the image generation model Flux-1-schnell.
    - The image generation model is called with the prompt and other parameters.
    - The generated background image is returned.

4. **Gemini API Integration:**
    - The `generate_banner` function utilizes the Gemini API to generate textual and color information for the banner design.
    - It constructs a prompt that includes the generated template from step 2, the promotion details, theme, resolution, the base64 encoded background image from step 3, and the base64 encoded product images from the input.
    - The Gemini API response, which is expected to be in JSON format, contains descriptions for the background image, a list of hex color values present in the background image, a comma-separated list of product names, the main promotional text, optional secondary text, and hex color values for both main and secondary text.
    - Robust error handling (e.g., `try-except` blocks) is implemented to manage potential issues with the API response or JSON parsing.  The function likely checks for valid JSON structure and handles cases where the API call fails or returns unexpected data.
    - The extracted textual and color information from the Gemini API response is then used to finalize the banner design, integrating it with the background and product images.  This likely involves using image manipulation libraries (like Pillow) to overlay text onto the image.


5. **Image Encoding:**
    - The `image_to_base64` function converts the generated background image into a base64 encoded string. This is a common practice for embedding images directly into HTML or JSON responses.



This design allows for flexible banner creation, adapting to various resolutions and image counts. The use Gemini API for template generation adds a layer of automation and adaptability, reducing the need for manually defined templates.  The image generation model provides the visual content based on user-provided themes and colors.
