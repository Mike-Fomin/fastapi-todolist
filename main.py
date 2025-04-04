from fastapi import FastAPI

from app.api.authentication import auth_router
from app.api.endpoints import router


app = FastAPI()

app.include_router(auth_router)
app.include_router(router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app='main:app',
        host='127.0.0.1',
        port=8000,
        reload=True
    )