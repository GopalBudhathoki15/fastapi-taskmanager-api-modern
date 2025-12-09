# TodoManager API

This is a FastAPI-based API for managing a simple todo list. It provides user authentication and CRUD operations for tasks.

## Features

* User registration and authentication using JWT
* Create, Read, Update, and Delete (CRUD) operations for tasks
* Each user has their own set of tasks
* Database migrations using Alembic

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.10+
* pip

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your_username/todomanager.git
    cd todomanager
    ```

2.  Create a virtual environment and activate it:
    ```bash
    python -m venv todovenv
    source todovenv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Create the database schema:
    ```bash
    alembic upgrade head
    ```

## Usage

To run the application, use the following command:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`. You can access the API documentation at `http://127.0.0.1:8000/docs`.

## Running the tests

To run the tests, use the following command:

```bash
pytest
```

## API Endpoints

### Authentication

*   `POST /auth/token`: Get an access token.
*   `POST /users/`: Create a new user.
*   `GET /users/me`: Get the current user's information.

### Tasks

*   `POST /tasks/`: Create a new task.
*   `GET /tasks/`: Get all tasks for the current user.
*   `GET /tasks/{task_id}`: Get a specific task.
*   `PUT /tasks/{task_id}`: Update a specific task.
*   `DELETE /tasks/{task_id}`: Delete a specific task.
