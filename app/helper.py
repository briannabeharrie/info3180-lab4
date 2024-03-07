import os

def get_uploaded_images(app):
    uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    image_files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
    return image_files