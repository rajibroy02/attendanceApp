from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

# Serve static files (CSS/JS) if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load Jinja2 templates (points to your "templates" folder)
templates = Jinja2Templates(directory="templates")

# Import your FastAPI app (from app.py)
from ..app import app as fastapi_app

# Mount APIs under "/api" (optional but organized)
app.mount("/api", fastapi_app)  # APIs: https://your-app.vercel.app/api/...

# Serve index.html at root ("/")
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)