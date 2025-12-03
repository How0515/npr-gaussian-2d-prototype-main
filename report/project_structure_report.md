# Project Structure Report

This project is organized into several key components, including a backend, a frontend, data management, and configuration files.

## Main Directory Structure

*   **`.claude/`**:
    *   `settings.local.json`: Contains local development environment settings.

*   **`backend/`**:
    *   Contains the Python-based backend service code.
    *   **`api/`**: Defines API endpoints (e.g., `upload.py`, `websocket.py`).
    *   **`config/`**: Contains backend-related configuration files (e.g., `brush_converter_config.yaml`).
    *   **`core/`**: Includes core logic and model implementations (e.g., `brush_converter.py`, `gaussian.py`, `renderer.py`, `deformation.py`).
    *   **`temp/uploads/`**: Directory for temporary file uploads.
    *   **`utils/`**: Contains utility functions (e.g., `helpers.py`).
    *   `main.py`: The entry point for the backend application.

*   **`data/`**:
    *   **`brushes/`**: Stores the brush library and individual brush definitions (`library.json`, `brushes/`, `thumbnails/`).

*   **`frontend/`**:
    *   Contains the web-based user interface (UI) files.
    *   **`css/`**: Includes stylesheets (`style.css`).
    *   **`js/`**: Contains client-side JavaScript logic (`brush_preview.js`, `canvas.js`, `ui.js`, `websocket_client.js`).
    *   `index.html`: The main HTML file for the frontend.

*   **Root Directory**:
    *   `deploy.sh`, `deploy_background.sh`: Deployment scripts.
    *   `environment.yml`, `requirements.txt`: Python environment and dependency management files.
    *   `setup.py`: Project installation script.
    *   `verify_setup.py`: Setup verification script.
    *   `input*.png`: Example input image files.
    *   `PROJECT_PLAN.md`, `README.md`: Project documentation files.

Overall, this project appears to be a web application for painting with 2D Gaussian splat brushes, consisting of a Python backend (likely using a framework like FastAPI) and an HTML/CSS/JavaScript frontend.
