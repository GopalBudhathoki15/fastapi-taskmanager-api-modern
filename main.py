from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.task import router as task_router
from fastapi.middleware.cors import CORSMiddleware
from config import settings


app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev
    "http://localhost:5173",  # Vite dev
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])


# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to Task Manager API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
