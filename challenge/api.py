import sys
from typing import List

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

from challenge.model import DelayModel

app = FastAPI(debug=True)
model = DelayModel()


all_airlines = [
    "American Airlines",
    "Air Canada",
    "Air France",
    "Aeromexico",
    "Aerolineas Argentinas",
    "Austral",
    "Avianca",
    "Alitalia",
    "British Airways",
    "Copa Air",
    "Delta Air",
    "Gol Trans",
    "Iberia",
    "K.L.M.",
    "Qantas Airways",
    "United Airlines",
    "Grupo LATAM",
    "Sky Airline",
    "Latin American Wings",
    "Plus Ultra Lineas Aereas",
    "JetSmart SPA",
    "Oceanair Linhas Aereas",
    "Lacsa",
]


class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

    @validator("MES")
    def check_mes_range(cls, value):
        if (value < 1) or (value > 12):
            raise HTTPException(status_code=400, detail="MES must be between 1 and 12")
        return value

    @validator("TIPOVUELO")
    def check_tipovuelo(cls, value):
        if value not in ["I", "N"]:
            raise HTTPException(
                status_code=400, detail="TIPOVUELO must be either 'I' or 'N'"
            )
        return value

    @validator("OPERA")
    def check_opera(cls, value):
        if value not in all_airlines:
            raise HTTPException(status_code=400, detail="OPERA must be a valid airline")
        return value


class PredictionInput(BaseModel):
    flights: List[Flight]


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {"status": "OK"}


@app.post("/predict", response_model=dict)
async def post_predict(input: PredictionInput) -> dict:
    try:
        all_entries = []
        for flights in input:
            for flights_info in flights[1]:
                all_entries.append(flights_info.__dict__)

        df = pd.DataFrame(all_entries)

        preprocessed_data = model.preprocess(df)
        predictions = model.predict(preprocessed_data)

        return {"predict": predictions}
    except Exception as e:
        # Log the error details
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8012)
