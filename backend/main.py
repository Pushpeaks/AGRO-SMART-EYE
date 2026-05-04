import os
import io
import json
import torch
import torch.nn as nn
import random
from torchvision import models, transforms
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from groq import Groq

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load class names
CLASS_NAMES = []
try:
    with open('class_names.txt', 'r') as f:
        CLASS_NAMES = [line.strip() for line in f.readlines()]
except Exception as e:
    print("Warning: class_names.txt not found. Using defaults.")
    CLASS_NAMES = [
        "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
        "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
        "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
        "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy"
    ]

# Model initialization
device = torch.device("cpu")
model = None
try:
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(CLASS_NAMES))
    if os.path.exists('plant_disease_model.pth'):
        model.load_state_dict(torch.load('plant_disease_model.pth', map_location=device))
        model.eval()
        print("Model loaded successfully.")
    else:
        print("Warning: plant_disease_model.pth not found. Predictions will be random until trained.")
except Exception as e:
    print(f"Error loading model: {e}")

# Preprocessing transform
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Initialize Groq API
# Load from environment variables to prevent leaking keys in version control
# For multiple keys, provide them as a comma-separated string: GROQ_API_KEYS="key1,key2,key3"
raw_keys = os.environ.get("GROQ_API_KEYS", "gsk_placeholder_key_here")
GROQ_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# Provide a fallback if no keys were found
if not GROQ_API_KEYS:
    GROQ_API_KEYS = ["gsk_placeholder_key_here"]

@app.post("/predict")
async def predict(file: UploadFile = File(...), language: str = Form("en")):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        # Read and preprocess the image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        img_t = transform(image)
        batch_t = torch.unsqueeze(img_t, 0)

        # Run inference
        prediction = "Unknown"
        confidence = 0.0
        if model:
            with torch.no_grad():
                outputs = model(batch_t)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                conf, index = torch.max(probabilities, 0)
                prediction = CLASS_NAMES[index]
                confidence = conf.item()

        # Generate guidance using Gemini API
        guidance = {
            "causes": ["Could not fetch causes."],
            "effects": ["Could not fetch effects."],
            "suggestions": ["Could not fetch suggestions."]
        }

        if "healthy" not in prediction.lower():
            api_key = random.choice(GROQ_API_KEYS)
            groq_client = Groq(api_key=api_key)
            prompt = f"""
            You are an expert agronomist. A CNN model has just predicted that a plant has the following disease: {prediction}.
            Please provide the 'causes', 'effects', and actionable 'suggestions' for treating this disease.
            Respond strictly in valid JSON format with three keys: 'causes' (list of strings), 'effects' (list of strings), and 'suggestions' (list of strings).
            
            CRITICAL INSTRUCTION: You MUST write the actual content for 'causes', 'effects', and 'suggestions' entirely in {'Hindi' if language == 'hi' else 'English'}. 
            
            Do not include Markdown formatting blocks like ```json, just output the raw JSON object.
            """
            
            try:
                response = groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"},
                )
                
                response_text = response.choices[0].message.content.strip()
                guidance = json.loads(response_text)
            except Exception as e:
                print(f"Error fetching/parsing Groq response: {e}")
        elif "healthy" in prediction.lower():
             if language == "hi":
                 guidance = {
                     "causes": ["पौधा पूरी तरह से स्वस्थ है!"],
                     "effects": ["कोई हानिकारक प्रभाव नहीं।"],
                     "suggestions": ["नियमित रूप से पानी देना जारी रखें और अच्छी धूप सुनिश्चित करें।"]
                 }
             else:
                 guidance = {
                     "causes": ["The plant is perfectly healthy!"],
                     "effects": ["No harmful effects."],
                     "suggestions": ["Continue regular watering and ensure good sunlight."]
                 }

        return {
            "disease": prediction,
            "confidence": confidence,
            "guidance": guidance
        }

    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend static files if they exist (for unified Hugging Face deployment)
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        path_to_file = os.path.join(frontend_dist_path, full_path)
        # Exclude /predict from being intercepted just in case, though FastAPI order should handle it
        if full_path != "predict" and os.path.isfile(path_to_file):
            return FileResponse(path_to_file)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "AgroSmart CNN Backend is running. (Frontend dist not found)"}
