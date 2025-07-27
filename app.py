import os
import sys
import time
import uvicorn
from fastapi import FastAPI, Request
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv
from datetime import datetime, timezone
from chat_component import root_agent
from contextlib import asynccontextmanager

def get_api_key_from_secret_manager():
    """Get Google API key from Secret Manager with fallback to .env"""
    # First try to load from .env file (for local development)
    load_dotenv(os.path.join(os.path.dirname(__file__), 'chat_component', '.env'))
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        print("Using Google API key from .env file")
        return api_key

    # If not in .env, try Secret Manager (for production)
    try:
        from google.cloud import secretmanager

        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0670800402")
        secret_name = "google-api-key"

        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

        response = client.access_secret_version(request={"name": name})
        api_key = response.payload.data.decode("UTF-8")

        # Set the environment variable for the ADK to use
        os.environ["GOOGLE_API_KEY"] = api_key
        print("Successfully loaded Google API key from Secret Manager")
        return api_key
    except Exception as e:
        print(f"Failed to get API key from Secret Manager: {e}")
        print("WARNING: No Google API key found. ADK agents may not work properly.")
        return None

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = BASE_DIR  # Parent directory containing multi_tool_agent
# Set up DB path for sessions
SESSION_DB_URL = f"sqlite:///{os.path.join(BASE_DIR,'chat_component', 'mock_finance.db')}"

# Create a lifespan event to initialize and clean up the session service
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Application starting up...")
    app.state.start_time = time.time()  # Track startup time for health checks

    # Initialize Google API key from Secret Manager
    get_api_key_from_secret_manager()

    # Initialize the DatabaseSessionService instance and store it in app.state
    try:
        app.state.session_service =DatabaseSessionService(db_url=SESSION_DB_URL)
        print("Database session service initialized successfully.")
    except Exception as e:
        print("Database session service initialized failed.")
        print(e)

    yield # This is where the application runs, handling requests
    # Shutdown code
    print("Application shutting down...")
# Create the FastAPI app using ADK's helper
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    # session_db_url=SESSION_DB_URL,
    allow_origins=["*"],  # In production, restrict this
    web=True,  # Enable the ADK Web UI
    lifespan=lifespan,  # Add the lifespan context manager
)
# Add custom endpoints
@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint that verifies system status
    """
    import time
    import psutil
    from datetime import datetime

    try:
        # Check database connectivity
        db_status = "healthy"
        try:
            if hasattr(app.state, 'session_service') and app.state.session_service:
                # Test database connection by attempting a simple operation
                db_status = "healthy"
            else:
                db_status = "not_initialized"
        except Exception as e:
            db_status = f"error: {str(e)}"

        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": time.time() - getattr(app.state, 'start_time', time.time()),
            "database": {
                "status": db_status
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            },
            "services": {
                "agent_service": "healthy" if 'root_agent' in globals() else "not_loaded"
            }
        }

        # Determine overall health status
        if db_status.startswith("error") or cpu_percent > 90 or memory.percent > 90:
            health_data["status"] = "degraded"

        return health_data

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@app.get("/health/simple")
async def simple_health_check():
    """
    Simple health check endpoint for basic monitoring
    """
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
@app.get("/agent-info")
async def agent_info():
    """Provide agent information"""
    
    return {
        "agent_name": root_agent.name,
        "description": root_agent.description,
        "model": root_agent.model,
        "tools": [t.name for t in root_agent.tools]
    }

DB_URL = "sqlite:///./multi_agent_data.db"
APP_NAME = "CustomerInquiryProcessor"



from fastapi import FastAPI, APIRouter, HTTPException
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
import json
import re
import uuid
from pydantic import BaseModel

class CustomerInquiryResponse(BaseModel):
    original_inquiry: str
    category: str
    suggested_response: str

class CustomerInquiryRequest(BaseModel):
    customer_inquiry: str

APP_NAME = "CustomerInquiryProcessor"

@app.post("/process-query")
async def process_customer_inquiry(
    request_body: CustomerInquiryRequest
):
    """
    Endpoint to interact with the multi-agent ADK system.
    request_body: {"customer_inquiry": "My internet is not working after the update, please help!"}
    """
    # Extract customer inquiry from request
    customer_inquiry = request_body.customer_inquiry
    unique_id = str(uuid.uuid4())
    session_id = unique_id
    user_id = unique_id

    try:
         # Get database session service from application state
        session_service: DatabaseSessionService = app.state.session_service
        
        # Try to get existing session or create new one
        current_session = None
        try:
            current_session = await session_service.get_session(
                app_name=APP_NAME,
                user_id = user_id,
                session_id=session_id,
            )
        except Exception as e:
            print(f"Existing Session retrieval failed for session_id='{session_id}' "
                    f"and user_uid='{user_id}': {e}")
        
        # If no session found, creating new session
        if current_session is None:
            current_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        else:
            print(f"Existing session '{session_id}'has been found. Resuming session.")

        # Initialize the ADK Runner with our multi-agent pipeline
        runner = Runner(
            app_name=APP_NAME,
            agent=root_agent,
            session_service = session_service,
        )


         # Format the user query as a structured message using the google genais content types
        user_message = types.Content(
            role="user", parts=[types.Part.from_text(text=customer_inquiry)]
        )
        
        # Run the agent asynchronously
        events = runner.run_async(
            user_id = user_id,
            session_id = session_id,
            new_message = user_message,
        )

        # Process events to find the final response 
        final_response = None
        last_event_content = None
        async for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    last_event_content = event.content.parts[0].text

        if last_event_content:
            final_response = last_event_content
        else:
            print("No final response event found from the Sequential Agent.")
    
        # Parse the JSON response from agents
        if final_response is None:
            raise HTTPException(status_code=500, detail="No response received from agent.")
        
        # Clean up Markdown code block if it exists
        # This handles responses like: ```json\n{ ... }\n```
        cleaned_response = re.sub(r"^```(?:json)?\n|```$", "", final_response.strip(), flags=re.IGNORECASE)
        
        # Loading the cleaned JSON
        try:
            response_data = json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Agent response is not valid JSON.")
        
        # Return the structured response using your Pydantic model
        return response_data
               
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process agent query: {e}")
    


if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080, 
        reload=False
    )