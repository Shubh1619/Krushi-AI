# 📄 app/utils/image_encoder.py

import base64
from io import BytesIO
from PIL import Image

def encode_image_to_base64(file) -> str:
    image = Image.open(file.file)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")