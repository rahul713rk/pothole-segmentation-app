import os
import io
import base64
import logging
from typing import List, Optional
from urllib import request

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
import cv2

from model import load_model
from model import ModelConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pothole Detection API", version="1.0.0")

# Configuration
class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "../model/model.onnx")
    IMAGE_SIZE = (640, 640)
    ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/jpg"]
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pothole-segmentation-gaibscye9-rahul-kumars-projects-5f3adc4a.vercel.app/",  # Without trailing slash
        "http://localhost:3000",  # For local development
        "http://localhost:5000",  # For local backend testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Global model instance
model = None
input_name = output_name = None

@app.on_event("startup")
async def startup_event():
    """Load the ONNX model on startup"""
    global model,input_name , output_name
    try:
        model = load_model(Config.MODEL_PATH)

        input_name = model.get_inputs()[0].name

        logger.info(f"Model loaded successfully from {Config.MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise RuntimeError(f"Model loading failed: {str(e)}")

def preprocess_img(img):
    img = cv2.resize(img, (640, 640))
    if len(img.shape) == 2:  
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = img.transpose(2, 0, 1)  
    img = img[np.newaxis, ...]
    img = img.astype(np.float32) / 255.0
    return img



@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Process uploaded image and return segmentation prediction"""
    logger.info(f"Received prediction request from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    if model is None:
        logger.error("Prediction attempted with no model loaded")
        raise HTTPException(status_code=503, detail="Model not loaded")

    logger.info(f"Received file: {file.filename}, content-type: {file.content_type}")

    if file.content_type not in Config.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {Config.ALLOWED_CONTENT_TYPES}"
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > Config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {Config.MAX_FILE_SIZE} bytes"
        )

    try:
        contents = await file.read()
        image_bytes = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        original_image = cv2.resize(image, Config.IMAGE_SIZE)

        if original_image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        processed_image = preprocess_img(original_image)

        # Run model prediction
        prediction = model.run(None, {input_name: processed_image})
        det_output = prediction[0]  # (1, 37, 8400)
        mask_protos = prediction[1]  # (1, 32, 160, 160)

        # Process detections
        det_output = det_output.squeeze(0).transpose()  # (8400, 37)
        confs = det_output[:, 4]
        mask_coefs_all = det_output[:, 6:]  # (8400, 32)

        # Filter predictions
        conf_threshold = 0.5
        valid_idx = confs > conf_threshold

        if not np.any(valid_idx):
            raise HTTPException(status_code=200, detail="No potholes detected")

        # Use first valid detection
        mask_coefs = mask_coefs_all[valid_idx][0:1]  # shape: (1, 32)

        class_label = "Pothole"
        result_image  = segmentation_image(
            original_image, 
            mask_protos, 
            mask_coefs, 
            class_label,
            conf_score=confs[valid_idx][0]
        )

        original_base64 = image_to_base64(Image.fromarray(original_image))
        result_base64 = image_to_base64(Image.fromarray(result_image))

        return JSONResponse({
            "original_image": original_base64,
            "segmentation_image": result_base64,
            "predicted_labels": class_label
        })

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


def segmentation_image(original_image, mask_protos, mask_coefs, class_label, conf_score=0.7, threshold=0.5):
    """
    Enhanced visualization mimicking YOLOv8's plot() output.
    Adds:
    - Semantic mask (colored)
    - Bounding box from mask
    - Label with confidence score
    """
    try:
        mask_protos = mask_protos[0]       # Shape: (C, H, W)
        mask_coefs = mask_coefs[0]         # Shape: (C,)
        
        # Ensure dimensions match
        num_coefs = mask_coefs.shape[0]
        mask_protos = mask_protos[:num_coefs, :, :]

        # Compute mask: [C, H, W] × [C, 1, 1] → [H, W]
        mask = np.sum(mask_protos * mask_coefs[:, None, None], axis=0)
        mask = 1 / (1 + np.exp(-mask))  # Sigmoid

        binary_mask = (mask > threshold).astype(np.uint8)

        # Resize to original resolution
        binary_mask = cv2.resize(
            binary_mask,
            (original_image.shape[1], original_image.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

        # Convert to 3-channel for visualization
        vis_image = original_image.copy()
        if vis_image.dtype != np.uint8:
            vis_image = (vis_image * 255).astype(np.uint8)

        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            logger.warning("No contours found in mask.")
            return vis_image

        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Get class color
        color = ModelConfig.CLASS_COLORS[class_label]
        color = tuple(int(c) for c in color)  # Ensure OpenCV-compatible

        # Apply semi-transparent mask
        mask_color = np.zeros_like(vis_image, dtype=np.uint8)
        mask_color[binary_mask == 1] = color
        vis_image = cv2.addWeighted(vis_image, 0.7, mask_color, 0.3, 0)

        # Draw bounding box
        if conf_score >= threshold:
            cv2.rectangle(vis_image, (x, y), (x+w, y+h), color, 2)

            label = f"{class_label} {conf_score:.2f}"
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(vis_image,
                          (x, y - label_height - 10),
                          (x + label_width + 10, y),
                          color, -1)
            cv2.putText(vis_image, label,
                        (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 1, cv2.LINE_AA)

        # Optionally draw contour line
        cv2.drawContours(vis_image, [largest_contour], -1, color, 1)

        return vis_image

    except Exception as e:
        logger.error(f"Segmentation visualization failed: {str(e)}")
        return original_image


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)