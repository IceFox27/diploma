import secrets
import os.path
from PIL import Image
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime

from flask import current_app

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['SERVER_PATH'], picture_fn)
    output_size = (64, 64)
    i = Image.open(picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def save_task_files(files, task_id):
    saved_files = []
    
    if not files:
        return None
    
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'task_reports', str(task_id))
    os.makedirs(upload_folder, exist_ok=True)
    
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{name}_{timestamp}{ext}"

            file_path = os.path.join(upload_folder, new_filename)
            file.save(file_path)
            
            saved_files.append(f'/static/uploads/task_reports/{task_id}/{new_filename}')
    
    return json.dumps(saved_files) if saved_files else None