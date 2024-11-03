import cloudinary
import cloudinary.uploader
import os
from flask import url_for, current_app
import uuid


"""Handles file uploads. If cloudinary set uploads to cloudinary and returns url. if not uploads to upload directory and returns the path"""


class FileUploadFailed(Exception):
    pass
class NoFileError(Exception):
    pass

def upload_file(file, filename=None, overwrite=True, path="profile_pictures"):
    if file is not None:
        if not filename:
            filename = str(uuid.uuid4())
        if current_app.config["UPLOAD_LOCATION"] == 'cloudinary':
            try:
                upload_result = cloudinary.uploader.upload(file, 
                                                    public_id=f"{path}/{filename}",
                                                    overwrite=overwrite)
                    
                    # Get the secure URL of the uploaded image
                return upload_result['secure_url']
            except Exception as e:
                raise FileUploadFailed(f'Upload failed error:{e}')
        else:            
            file.save(os.path.join(current_app.config["UPLOAD_LOCATION"], f"{filename}.{file.filename.rsplit('.', 1)[1]}"))
            return url_for('send_file',filename=f"{filename}.{file.filename.rsplit('.', 1)[1]}")
    raise NoFileError()