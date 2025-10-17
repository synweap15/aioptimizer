import uvicorn
from server import create_server
from routers import api

app = create_server()

# Include API routers
app.include_router(api.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
