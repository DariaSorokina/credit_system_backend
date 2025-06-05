from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .endpoints import applications, deals, documents,offers, user
from .config import settings
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)
app.include_router(deals.router)
app.include_router(documents.router)
app.include_router(user.router)
app.include_router(offers.router)

@app.get("/")
def read_root():
    return {"message": "Credit System API"}

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)