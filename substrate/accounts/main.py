from fastapi import FastAPI

from accounts.routes import accounts as accounts_routes
from accounts.routes import auth as auth_routes


app = FastAPI(title="accounts")
app.include_router(auth_routes.router)
app.include_router(accounts_routes.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
