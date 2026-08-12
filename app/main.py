from fastapi import FastAPI, status

from app.routers.auth_router import auth_router
from app.routers.desk_router import desk_router
from app.routers.room_router import room_router

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(desk_router)
app.include_router(room_router)
