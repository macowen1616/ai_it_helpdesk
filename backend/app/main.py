from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "IT Help Desk Assistant API"}