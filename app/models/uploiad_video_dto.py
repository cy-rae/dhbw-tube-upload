from werkzeug.datastructures.file_storage import FileStorage


class UploadVideoDTO:
    def __init__(self, title: str, creator: str, description: str, cover: FileStorage, video: FileStorage):
        self.title = title
        self.creator = creator
        self.description = description
        self.cover = cover
        self.video = video
