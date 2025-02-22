from flask import request


def get_request_file(field_name: str = None) -> dict:
    field_name = 'document' if field_name is None else field_name
    file = {}
    request_file = request.files.to_dict().get(field_name)

    if request_file:
        file = {
            'mime_type': request_file.mimetype,
            'filename': request_file.filename,
            'file_data': request_file.read(),
        }
    return file
