from fastapi import FastAPI

from .routers import films, actors

app = FastAPI()


app.include_router(films.router)
app.include_router(actors.router)


@app.get("/")
async def root():
    return {"message": ""}
