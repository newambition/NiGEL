# Installation

This guide provides instructions on how to set up the NiGEL project on your local machine.

## Prerequisites

*   Python 3.9 or higher
*   Poetry for dependency management

## Installation Steps

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd NiGEL
    ```

2.  **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

3.  **Set up the Gemini API Key:**

    The application requires a Google Gemini API key to function. You need to set the API key in the `main.py` file.

    Open `main.py` and replace `"AIzaSyDWI4MZGoes22zdtD6JQcsU1Y8AOb5AoDY"` with your actual API key:

    ```python
    # Configure Gemini API
    MODEL_NAME = "gemini-2.0-flash"
    genai.configure(api_key="YOUR_GEMINI_API_KEY")
    ```

4.  **Run the application:**

    ```bash
    poetry run python main.py
    ```

## Building a Standalone Executable

The project is configured to be built into a standalone executable using PyInstaller and auto-py-to-exe.

To build the application, run the following command:

```bash
poetry run pyinstaller --onefile --noconsole --add-data "nigel.png:." main.py
```

This will create a single executable file in the `dist` directory.
