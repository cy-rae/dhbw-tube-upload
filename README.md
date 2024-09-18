# dhbw-tube-upload Microservice

## Overview
The **DHBW Upload Microservice** is a Flask-based application designed to handle video uploads. It provides an endpoint for uploading videos to a MinIO object storage and saving the associated metadata to a PostgreSQL database. This microservice ensures that video files and their corresponding thumbnails are securely stored and that all relevant metadata is properly recorded for future retrieval and management.

## Features
- **Video Upload**: Allows users to upload video files along with cover images.
- **MinIO Integration**: Stores video files and cover images in MinIO object storage.
- **PostgreSQL Integration**: Saves video metadata in a PostgreSQL database.
- **Payload Validation**: Validates the incoming request payload to ensure all required fields are present and correct.
- **Error Handling**: Provides detailed error messages and logging for troubleshooting.

## Endpoints
`/upload`
- Method: POST
- Description: Validates the payload, uploads the video and cover to MinIO, and stores the metadata in the PostgreSQL database.
- Request Payload:
    - `title` (string): The title of the video.
    - `creator` (string): The creator of the video.
    - `description` (string, optional): A description of the video.
    - `cover` (file): The cover image file for the video.
    - `video` (file): The video file.
- Response:
    - *201 Created*: If the upload is successful.
    - *400 Bad Request*: If the payload is invalid.
    - *500 Internal Server Error*: If there is an error during file upload or metadata storage.

## Configuration
The microservice can be configured using environment variables. The following variables are available:

- `FLASK_APP`: The Flask application entry point.
- `FLASK_ENV`: The environment in which the Flask app is running (e.g., production).
- `MINIO_ENDPOINT`: The endpoint for the MinIO server.
- `MINIO_ACCESS_KEY`: The access key for MinIO.
- `MINIO_SECRET_KEY`: The secret key for MinIO.
- `POSTGRES_URI`: The URI for the PostgreSQL database.

## Logging
The microservice uses Python's built-in logging module to log important events and errors. Logs are printed to the console and can be viewed in the Docker container logs.
