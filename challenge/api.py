import sys
from typing import List

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

from challenge.model import DelayModel

app = FastAPI(debug=True)
model = DelayModel()


class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

    @validator('MES')
    def check_mes_range(cls, value):
        if (value < 1) or (value > 12):
            raise HTTPException(status_code=400, detail='MES must be between 1 and 12')
        return value
    
    @validator('TIPOVUELO')
    def check_tipovuelo(cls, value):
        if value not in ['I', 'N']:
            raise HTTPException(status_code=400, detail="TIPOVUELO must be either 'I' or 'N'")
        return value

class PredictionInput(BaseModel):
    flights: List[Flight]

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

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