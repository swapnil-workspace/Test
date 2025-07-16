# app.py
from fastapi import FastAPI, APIRouter, HTTPException
from .models import TextInput # Import your custom model

# Your main FastAPI application instance
app = FastAPI()

# Your router where the /initial_query endpoint is defined
router = APIRouter()

# Placeholder for your actual product fetching logic
async def fetch_product(query_text: str):
    # This is where your actual logic to interact with DB/other services would go
    # For example, querying Cosmos DB or a database
    if "error" in query_text.lower():
        raise ValueError("Simulated product fetch error")
    return {"product_info": f"Details for: {query_text}"}

@router.post("/initial_query")
async def handle_initial_query(input_data: TextInput):
    """
    This endpoint accepts a JSON request body conforming to the TextInput model.
    """
    try:
        # FastAPI automatically parses the JSON request body into a TextInput object
        # You can now access its fields directly: input_data.text
        
        logging.info(f"Received query text: {input_data.text}")
        
        result = await fetch_product(input_data.text)
        return {"result": result}
    except Exception as e:
        # FastAPI's HTTPException should be used here for proper HTTP error responses
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in your main app
app.include_router(router)

# Optional: Add other routes directly to 'app' or create more routers
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FastAPI app is running."}

# Important: You might have other imports and logic here like logging setup.
import logging
logging.basicConfig(level=logging.INFO) # Basic logging setup
