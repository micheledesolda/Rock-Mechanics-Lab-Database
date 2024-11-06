Rock Mechanics Lab Database
Project Overview

The Rock Mechanics Lab Database provides a structured platform to manage and retrieve experimental data for rock mechanics laboratories. Built with FastAPI and MongoDB, this database API supports efficient access to various experimental data, including core samples, block characteristics, experiments, sensors, and machines.
Features

    FastAPI-based RESTful API for efficient data retrieval and management.
    MongoDB database integration for scalable storage of experiment data.
    Modular API endpoints for managing different laboratory data (e.g., samples, sensors, experiments).
    CORS-enabled for cross-origin access, allowing integration with other applications or analysis tools.

Installation

    Clone the Repository git clone <repository-url> cd Rock_Mechanics_Lab_Database_GPT

    Install Dependencies The project uses Poetry for dependency management. If Poetry is not installed: pip install poetry

    Then install dependencies: poetry install

    Configure MongoDB Ensure MongoDB is installed and running. Default settings assume MongoDB is available locally. Adjust connection settings in .env if needed.

    Run the Server Start the FastAPI server: poetry run python main.py

    The API will be accessible at http://localhost:8000.

Usage

    Access API Documentation After starting the server, open http://localhost:8000/docs in your browser to access the automatically generated API documentation (Swagger UI).

    API Endpoints Key endpoints:
        /blocks: Manage block data.
        /core_samples: Access core sample information.
        /experiments: Retrieve experiment details.
        /sensors: Retrieve and manage sensor data.
        /machines: Manage laboratory machine information.

    Use a tool like curl, Postman, or any HTTP client to interact with the API.

File Structure

    main.py: Main entry point for the FastAPI server.
    rock_mechanics_lab_database: Contains core API modules and router definitions.
    notebooks: Jupyter notebooks for exploratory analysis (not part of the core server).
    scripts: Contains auxiliary scripts for data management or setup.
    tests: Unit and integration tests to verify the functionality of the API.

Configuration

    Environment Variables: Environment settings are managed in a .env file. Key variables include:
        MONGO_URI: URI for connecting to the MongoDB database.
        CORS_ORIGINS: Comma-separated list of allowed origins for CORS.

Testing

To run tests: poetry run pytest tests/
Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

