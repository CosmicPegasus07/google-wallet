import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv
from chat_component import root_agent

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
)
# Add custom endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
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
from contextlib import asynccontextmanager
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
        port=8000, 
        reload=False
    )