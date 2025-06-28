from fastapi import FastAPI
from routes import router
#this launches the application like main() in java / springboot
app = FastAPI(title="Bhagavad Gita Chat API")
app.include_router(router, prefix="/api")