from sys import path as sys_path
from os import getcwd as os_getcwd

from fastapi.middleware.cors import CORSMiddleware

# Adding ./src to python path for running from console purpose:
sys_path.append(os_getcwd())

from uvicorn import run as uvicorn_run
from fastapi import FastAPI

from src.lifespan import lifespan
from src.sso.versions.v1.routes import router as sso_router
from src.admins.versions.v1.routes import router as admins_router
from src.users.versions.v1.routes import router as users_router
from src.mock_transactions.routes import router as transaction_router

app: FastAPI = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=[  # Домены для тестов
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        # Либо добавьте свой тестовый домен
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(sso_router)
app.include_router(admins_router)
app.include_router(users_router)
app.include_router(transaction_router)

if __name__ == "__main__":
    uvicorn_run(app=app, host="0.0.0.0", port=8000)
