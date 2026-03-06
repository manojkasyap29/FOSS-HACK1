from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NutriScan API", description="Backend for the NutriScan App")


class ScanRequest(BaseModel):
    image_url: str
    user_id: int


@app.get("/")
def read_root():
    return {"status": "NutriScan API is running"}


@app.post("/api/scan")
def scan_product(request: ScanRequest):
    # Dummy response for MVP
    return {
        "ingredients_detected": ["Sugar", "Palm Oil", "Maltodextrin"],
        "allergy_alerts": ["Contains artificial additives"],
        "health_score": -0.42,
        "verdict": "Unhealthy"
    }