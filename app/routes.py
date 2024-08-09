"""Endpoint for uploading videos to MinIO and saving metadata to PostgreSQL"""

from flask import Blueprint, request, jsonify
from minio import Minio
from minio.error import S3Error
from .models import db, Video
import os
import uuid

api = Blueprint(name='api', import_name=__name__)

# MinIO Client Setup
minio_client = Minio(
    os.getenv('MINIO_ENDPOINT', 'minio:9000'),
    access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
    secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
    secure=False
)

bucket_name = "video-files"

# Ensure the bucket exists
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)


@api.route(rule='/upload', methods=['POST'])
def upload_video():
    title = request.form.get('title')
    creator = request.form.get('creator')
    description = request.form.get('description')

    if not title or not creator:
        return jsonify({"error": "Title and creator are required"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_id = str(uuid.uuid4())
    file_extension = file.filename.rsplit(sep='.', maxsplit=1)[1].lower()
    file_name = f"{file_id}.{file_extension}"

    try:
        # Upload file to MinIO
        minio_client.put_object(
            bucket_name,
            file_name,
            file.stream,
            length=-1,  # Length of the stream (unknown)
            part_size=10 * 1024 * 1024,  # 10 MB part size
            content_type=file.content_type
        )

        # Save metadata to the PostgreSQL database
        video = Video(
            id=file_id,
            title=title,
            creator=creator,
            description=description,
            filename=file_name
        )
        db.session.add(video)
        db.session.commit()

    except S3Error as err:
        return jsonify({"error": str(err)}), 500

    return jsonify({"message": "File uploaded successfully", "file_id": file_id}), 200
