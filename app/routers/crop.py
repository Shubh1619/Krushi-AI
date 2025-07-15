from fastapi import APIRouter, File, UploadFile, Form
from app.utils.image_encoder import encode_image_to_base64
from app.services.groq_ai import diagnose_crop_from_image


router = APIRouter()


@router.post("/diagnose")
async def diagnose_crop(
    image: UploadFile = File(...),
    crop: str = Form(...),
    lang: str = Form('mr')
):
    if not image.content_type.startswith("image/"):
        return {"error": "❌ कृपया वैध छायाचित्र अपलोड करा (jpg/png/jpeg)"}
    
    file_bytes = await image.read()
    result = diagnose_crop_from_image(file_bytes, crop)
    return {
        "crop": crop,
        "lang": lang,
        "result": result
    }
