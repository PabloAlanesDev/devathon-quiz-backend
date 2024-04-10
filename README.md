# [Backend] Code Quiz Challenge: Test Your Programming Knowledge

Are you a coding enthusiast looking to put your skills to test? Don't look more! Our Code Quiz Challenge is designed to challenge your programming knowledge versus other players across various languages and concepts. Whether you,re a begginer or a seasoned developer looking for a fun way to brush up on your skills, this quiz is perfect for you.


# Getting Started

- Clone the repository

    ```
    git clone https://github.com/PabloAlanesDev/devathon-quiz-backend.git
    ```

- Create python virtualenv
    ```
    python -m virtualenv .venv
    ```

- Activate python virtualenv
    ```
    source .venv/bin/activate
    ```

- Install python dependencies
    ```
    pip install -r requirements-dev.txt
    pip install flask-pymongo python-dotenv
    ```

- Run server

    ```sh
    python server.py
    ```

# Run server with Docker

- Build docker image of the app

    ```sh
    docker compose build
    ```

- Run container of the app

    ```sh
    docker compose up app
    ```

# Built With
- Python
- flask-socketio
- MongoDB
