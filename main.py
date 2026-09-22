from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
import threading

from entity import ChatRequest, ChatResponse
from agents.tools import get_hotels, get_flights
from agents.graph import graph

# Thread-safe per-session history
conversation_history = defaultdict(list)
_history_lock = threading.Lock()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def hello():
    return {"message": "Hello, World!"}


@app.get("/hotels")
async def list_hotels():
    return get_hotels.invoke({})


@app.get("/flights")
async def list_flights():
    return get_flights.invoke({})


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    session_id = http_request.headers.get("X-Session-ID", "default")
    
    with _history_lock:
        history = conversation_history[session_id]
        recent_pairs = history[-3:]
        flattened = []
        for u, a in recent_pairs:
            flattened.extend([u, a])
        flattened.append(request.message)

    initial_state = {
        "messages": flattened,
        "intent": "",
        "sub_action": "",
        "city": None,
        "check_in": None,
        "check_out": None,
        "origin": None,
        "destination": None,
        "flight_date": None,
        "hotel_id": None,
        "guest_name": None,
        "guest_email": None,
        "room_type": None,
        "flight_id": None,
        "passenger_name": None,
        "passenger_email": None,
        "hotel_results": [],
        "flight_results": [],
        "response_text": "",
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {e}")

    response_text = result.get("response_text", "Something went wrong. Please try again.")

    with _history_lock:
        conversation_history[session_id].append((request.message, response_text))
        # Cap history at 20 exchanges per session
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]

    return ChatResponse(
        response=response_text,
        hotels=result.get("hotel_results", []) or None,
        flights=result.get("flight_results", []) or None,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)