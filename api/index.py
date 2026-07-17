from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from entity import ChatRequest, ChatResponse
from agents.tools import get_hotels, get_flights, search_hotel, search_flights, book_hotel, book_flight
from agents.graph import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def hello():
    return {"message": "Hello, World!"}


@app.get("/api/hotels")
async def list_hotels():
    return get_hotels.invoke({})


@app.get("/api/flights")
async def list_flights():
    return get_flights.invoke({})


@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    initial_state = {
        "messages": request.history + [request.message] if request.history else [request.message],
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

    result = graph.invoke(initial_state)

    response_text = result.get("response_text", "Something went wrong. Please try again.")

    return ChatResponse(
        response=response_text,
        hotels=result.get("hotel_results", []) or None,
        flights=result.get("flight_results", []) or None,
    )



