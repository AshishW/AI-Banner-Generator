# ArtVisionX AI Backend

This Flask application is a backend server that dynamically generates image banner templates. It uses pre-defined templates or generates them on-the-fly using the Gemini LLM, depending on user-specified resolution and number of images.  Background images are created using an image generation model (potentially Flux), incorporating user-defined themes and color palettes. The resulting banner is then encoded in base64 for easy integration into web applications.  


## System Architecture

[System Architecture Design documentation](systemarchitecture.md)



## Directory structure

```
├── app.py
├── README.md
├── requirements.txt
├── .venv
├── static
└── templates
    └── index.html

```


## Setting up the Flask App Locally

These instructions guide you through setting up and running the Flask application locally.

### Prerequisites

*   **Python 3.7 or higher:** Ensure you have Python 3.7 or a later version installed on your system. You can check your Python version by running `python --version` or `python3 --version` in your terminal.  If you need to install Python, download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).


### Setup Steps

1.  **Clone the Repository:**  First, clone the application's repository from its location (replace `<repository_url>` with the actual URL):

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a Virtual Environment:** Creating a virtual environment is crucial to isolate the project's dependencies.  Use `venv` (recommended for Python 3.3+) or `virtualenv` (if you have it installed):

    ```bash
    python3 -m venv venv  # Using venv
    # or
    virtualenv venv       # Using virtualenv (requires installation: pip install virtualenv)
    ```

3.  **Activate the Virtual Environment:** Activate the virtual environment. The activation command depends on your operating system:

    *   **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```

    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```

4.  **Install Dependencies:** Install the required Python packages listed in the `requirements.txt` file (assuming your project has one):

    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Environment Variables:** Create a `.env` file in the root directory of your project. Add the following lines, replacing `<your_api_key>` and `<your_hf_token>` with your actual API keys:

    ```
    GEMINI_API_KEY=<your_api_key>
    HF_TOKEN=<your_hf_token>
    ```

    You may need to install the python-dotenv package to load these variables: `pip install python-dotenv`

6.  **Run the Application:** Navigate to the application's directory and start the Flask development server:

    ```bash
    python app.py
    ```

    This will typically start the server on `http://127.0.0.1:5000/` (or a similar address). Open your web browser and go to that address to see the application.

7.  **Deactivate the Virtual Environment:** When you're finished working on the application, deactivate the virtual environment:

    ```bash
    deactivate
    ```


### Troubleshooting

*   **Dependency Issues:** If you encounter issues installing dependencies, double-check your `requirements.txt` file and ensure all listed packages are compatible with your Python version.  You might need to resolve version conflicts manually.

*   **Server Errors:** If the server fails to start, check the terminal output for error messages. These messages often provide clues about the problem (e.g., missing modules, configuration errors).

*   **Port Conflicts:** If port 5000 is already in use, you can specify a different port when running the application:

    ```bash
    python app.py --port 5001  # Or any other available port
    ```

Remember to replace placeholders like `<repository_url>` and `<repository_name>` with your actual values.  If you have any other specific setup instructions or configuration details, please provide them, and I will update these instructions accordingly.
