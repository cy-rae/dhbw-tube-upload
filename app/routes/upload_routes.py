"""Endpoint for uploading videos to MinIO and saving metadata to PostgreSQL"""
import io
import logging
import uuid
from typing import Optional, BinaryIO

from flask import Blueprint, request, jsonify
from minio.error import S3Error
from werkzeug.datastructures.file_storage import FileStorage

from app.models.minio_client import minio_client
from app.models.uploiad_video_dto import UploadVideoDTO
from app.models.video_metadata import db, VideoMetadata

upload_api = Blueprint(name='api', import_name=__name__)

video_bucket_name = "video-files"
cover_bucket_name = "video-covers"

# Ensure the buckets exists
for bucket in [video_bucket_name, cover_bucket_name]:
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)


@upload_api.route(rule='/upload', methods=['POST'])
def upload_video():
    """
    Validate the passed payload, upload the video and cover to MinIO and store the metadata to db.
    """
    (dto, err) = __validate_payload()
    if err is not None:
        logging.error(f"Invalid payload: {err}")
        return jsonify({"error": err}), 400

    video_metadata = get_video_metadata(dto)

    try:
        # Store cover and video in MinIO
        store_file(file=dto.cover, filename=video_metadata.cover_filename, bucket_name=cover_bucket_name)
        store_file(file=dto.video, filename=video_metadata.video_filename, bucket_name=video_bucket_name)

        # Store metadata in Postgres
        store_metadata(video_metadata)
    except S3Error as err:
        logging.error(f"S3Error error: {err}")
        return jsonify({"error": str(err)}), 500

    return jsonify({"message": "File uploaded successfully", "file_id": video_metadata.id}), 201


def __validate_payload() -> tuple[Optional[UploadVideoDTO], Optional[str]]:
    """
    Validate the request payload for the upload endpoint.
    returns: Returns None if the payload is valid, otherwise an error message.
    """
    # Check if metadata is valid
    title: Optional[str] = request.form.get('title')
    creator: Optional[str] = request.form.get('creator')
    if not title or not creator:
        return None, "Title and creator are required"

    # Check if cover is valid
    if 'cover' not in request.files:
        return None, "No cover part in the request"
    cover: Optional[FileStorage] = request.files['cover']
    if cover.filename == '':
        return None, "No cover selected"

    # Check if file is valid
    if 'video' not in request.files:
        return None, "No video part in the request"
    video: Optional[FileStorage] = request.files['video']
    if video.filename == '':
        return None, "No video selected"

    description: Optional[str] = request.form.get('description')
    return UploadVideoDTO(title, creator, description, cover, video), None


def get_video_metadata(dto: UploadVideoDTO) -> VideoMetadata:
    """
    Create an identifiable VideoMetadata object from the passed payload.
    """
    video_id = str(uuid.uuid4())

    cover_extension: str = dto.cover.filename.rsplit(sep='.', maxsplit=1)[1].lower()
    cover_filename = f"{video_id}.{cover_extension}"
    cover_mime_type = dto.cover.mimetype

    video_extension: str = dto.video.filename.rsplit(sep='.', maxsplit=1)[1].lower()
    video_filename = f"{video_id}.{video_extension}"
    video_mime_type = dto.video.mimetype

    return VideoMetadata(
        id=video_id,
        title=dto.title,
        creator=dto.creator,
        description=dto.description,
        cover_filename=cover_filename,
        cover_mime_type=cover_mime_type,
        video_filename=video_filename,
        video_mime_type=video_mime_type
    )


def store_file(file: FileStorage, filename: str, bucket_name: str):
    """
    Store the passed file in MinIO.
    @param file: The file to store.
    @param filename: The name of the file.
    @param bucket_name: The name of the bucket to store the file in.
    """

    # Parse the file stream to a binary stream
    binary_data: BinaryIO = io.BytesIO(file.stream.read())

    # Get the length of the binary data
    binary_data.seek(0, io.SEEK_END)
    length = binary_data.tell()
    binary_data.seek(0)  # Reset the stream position to the beginning

    # Determine part size based on the length of the binary data. The part size determines the size of the parts the
    # file is split into when uploading to MinIO.
    if length >= 1 * 1024 * 1024 * 1024:  # 1 GB or more
        part_size = 25 * 1024 * 1024  # 25 MB
    elif length >= 100 * 1024 * 1024:  # Less than 1 GB
        part_size = 10 * 1024 * 1024  # 10 MB
    else:  # Less than 100 MB
        part_size = 5 * 1024 * 1024  # 5 MB

    # Upload the file to MinIO
    minio_client.put_object(
        bucket_name,
        filename,
        binary_data,
        length=length,
        part_size=part_size,
        content_type=file.content_type
    )

    logging.info(f"Stored file with name '{filename}' into the MinIO database.")


def store_metadata(video_metadata: VideoMetadata):
    db.session.add(video_metadata)
    db.session.commit()
    logging.info(f"Stored metadata for video with ID '{video_metadata.id}' in the database.")
