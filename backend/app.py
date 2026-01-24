from fastapi import FastAPI
from flask import Flask

# FastAPI 应用
fastapi_app = FastAPI()

@fastapi_app.get("/")
def read_root():
    return {"message": "FastAPI is running"}

# Flask 应用
flask_app = Flask(__name__)

@flask_app.route("/")
def hello():
    return "Flask is running"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
