from fastapi import FastAPI

from .routers import films, actors, categories, languages

app = FastAPI(root_path="/api/v1")


app.include_router(films.router, tags=["films"])
app.include_router(languages.router, tags=["languages"])
app.include_router(actors.router, tags=["actors"])
app.include_router(categories.router, tags=["film_categories"])


@app.get("/")
async def root():
    return {"message": ""}
