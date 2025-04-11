from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import os
import numpy as np
import joblib
from insightface.app import FaceAnalysis
from sklearn.neighbors import KNeighborsClassifier
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models - using relative path
embeddings_path = os.path.join(os.path.dirname(__file__), "face_embeddings.pkl")
X_train, y_train = joblib.load(embeddings_path)
X_train = np.array(X_train, dtype=np.float32)
y_train = np.array(y_train, dtype=str)

knn = KNeighborsClassifier(n_neighbors=3, metric="cosine")
knn.fit(X_train, y_train)
face_app = FaceAnalysis(name="buffalo_s", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes
@app.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    image = read_image(file.file)
    recognized_faces = recognize_faces(image)[0]
    return JSONResponse(content={
        "recognized_faces": recognized_faces['name'],
        "timestamp": str(datetime.now())
    })

@app.get("/")
async def home():
    return FileResponse("templates/index.html")  # Updated path

# Helper functions
def read_image(file):
    image_bytes = file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(image_np, cv2.IMREAD_COLOR)

def recognize_faces(image):
    faces = face_app.get(image)
    return [{
        "name": str(knn.predict([face.normed_embedding])[0]),
        "bbox": face.bbox.astype(int).tolist()
    } for face in faces]

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=True)