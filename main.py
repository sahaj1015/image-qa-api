import os
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# ---- Setup ----
app = FastAPI()

# Allow requests from anywhere (required so the grader's Cloudflare Worker can call this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read the Gemini API key from an environment variable (set this on Render, not in this file)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


# ---- Request format ----
class ImageQuestion(BaseModel):
    image_base64: str
    question: str


# ---- Health check (so you can confirm the server is alive) ----
@app.get("/")
def home():
    return {"status": "ok", "message": "Image QA API is running"}


# ---- Main endpoint ----
@app.post("/answer-image")
def answer_image(req: ImageQuestion):
    try:
        # Some clients include a data URL prefix like "data:image/png;base64,....."
        # Strip it if present, so we only decode the actual base64 data.
        image_data = req.image_base64
        if "," in image_data and "base64" in image_data.split(",")[0]:
            image_data = image_data.split(",")[1]

        img_bytes = base64.b64decode(image_data)

        prompt = (
            req.question
            + "\n\nLook carefully at the image and answer the question. "
            "Return ONLY the raw answer value (a number or short string). "
            "Do not include currency symbols, units, explanations, or extra words."
        )

        response = model.generate_content(
            [
                {"mime_type": "image/png", "data": img_bytes},
                prompt,
            ]
        )

        answer_text = response.text.strip()

        # Clean up common junk the model might add
        answer_text = answer_text.strip("`").strip()
        if answer_text.lower().startswith("answer:"):
            answer_text = answer_text[len("answer:"):].strip()

        # Strip common currency symbols, thousands separators, and stray quotes
        for junk in ["$", "€", "£", "₹", ",", '"', "'"]:
            answer_text = answer_text.replace(junk, "")
        answer_text = answer_text.strip()

        return {"answer": answer_text}

    except Exception as e:
        return {"answer": f"ERROR: {str(e)}"}
