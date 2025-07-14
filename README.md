# Pearl Tours Web Application

Pearl Tours is a web application designed to showcase and manage tour packages for exploring Uganda, the Pearl of Africa. It allows users to browse tours, view details, and administrators to manage tour listings.

## Technologies Used

- **Backend:** Python, FastApi
- **Frontend:** HTML, CSS, JavaScript, Bootstrap, TailWard
- **Database:** mySQL(with SQLite for development/testing)
- **Containerization:** Docker, Docker Compose

## Project Structure

```
├── app/                    # Main application folder
│   ├── templates/          # HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   ├── main.py             # Flask application entry point
│   ├── models.py           # Database models
│   ├── routes.py           # Application routes
│   └── ...                 # Other Python modules
├── static/                 # Public static assets
├── test.db                 # SQLite database file
├── .gitignore
├── Dockerfile              # Docker configuration for the application
├── docker-compose.yaml     # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
|__ Tests                   # pytest code testing
|__ .github\workflows       # Github actions workflows
```

## Setup and Running the Project

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Docker (optional, for containerized setup)
- Docker Compose (optional, for containerized setup)

### Local Development (Without Docker)

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/Scripts/activate  # On Windows: venv\Scripts\activate
    source venv/bin/activate  # On MacOS
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database (if applicable):**
    The application uses Flask-Migrate or similar, or database tables are created on first run. (Details might need to be added here based on `database.py` or `models.py` specifics).
    For instance, if there is an admin creation script:

    ```bash
    python -m app.create_admin
    ```

    (Verify if `test.db` is automatically created or needs a command)

5.  **Run the application:**
    ```bash
    python -m uvicorn app.main:app --reload --host localhost
    ```
    The application should typically be accessible at `http://localhost:8000`.

### Using Docker Compose (Recommended for ease of use)

1.  **Ensure Docker and Docker Compose are installed.**

2.  **Navigate to the project root directory.**

3.  **Build and run the services:**

    ```bash
    chmod +x start.sh && ./start.sh
    ```

4.  Creating an Admin in docker

    ```bash
     docker exec -it first-prototype-app-1 python -m app.create_admin
    ```

5.  The application will be accessible, usually at `http://localhost:8000` (or as configured in `docker-compose.yaml`).

6.  **To stop the services:**
    ```bash
    Press Ctrl C
    or docker ps get the conatiner id then docker stop <container_id>
    ```

## Contributing

Details on how to contribute to the project will be added here.

## License

Specify the project license here (e.g., MIT, Apache 2.0).
