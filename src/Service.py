from typing import List, Dict, Optional, Union
from Dao import ExperimentDao
from fastapi import FastAPI, HTTPException, Query

# the following code implement the exposed service 
experimentDao = ExperimentDao()
app = FastAPI()

@app.get("/experiments", response_model=Union[List[Dict], str])
async def get_experiments(offset: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    """
    Retrieve experiments with pagination.
    """
    result = experimentDao.read(offset, limit)
    if isinstance(result, str) and result.startswith("Error"):
        raise HTTPException(status_code=500, detail=result)
    elif result == "No experiments found":
        raise HTTPException(status_code=404, detail=result)
    return result