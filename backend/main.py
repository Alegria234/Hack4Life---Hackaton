from fastapi import FastAPI

app = FastAPI(title="API Hospital Susana López - Hackathon FUP")

@app.get("/")
def read_root():
    return {"mensaje": "Backend de FastAPI funcionando correctamente. ¡Listos para la IA!"}