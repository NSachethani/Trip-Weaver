import json
import os
from urllib.request import Request, urlopen
import urllib.error
import gradio as gr

# Ensure proper URL formatting regardless of trailing slashes or whether /chat is already included
BASE_URL = os.environ.get("TRAVEL_PLANNER_API_URL", "http://127.0.0.1:8000").rstrip("/")
API_URL = BASE_URL if BASE_URL.endswith("/chat") else f"{BASE_URL}/chat"


def format_flights(flights):
    lines = ["**✈️ Flights:**"]
    for flight in flights:
        f_id = flight.get("_id", "Unknown ID")
        airline = flight.get("airline", "Unknown Airline")
        flight_number = flight.get("flightNumber", "Unknown Flight Number")
        
        origin = flight.get("origin")
        origin_str = origin.get("airport", "Unknown Origin") if isinstance(origin, dict) else (origin or "Unknown Origin")
        
        destination = flight.get("destination")
        dest_str = destination.get("airport", "Unknown Destination") if isinstance(destination, dict) else (destination or "Unknown Destination")
        
        flight_date = flight.get("flightDate", "Unknown Date")
        departure_time = flight.get("departureTime", "")
        arrival_time = flight.get("arrivalTime", "")
        price = flight.get("price", "N/A")
        currency = flight.get("currency", "")
        available_seats = flight.get("availableSeats", "N/A")
        
        lines.append(
            f"- **{airline} {flight_number}** (ID: `{f_id}`)\n"
            f"  • {origin_str} ➔ {dest_str}\n"
            f"  • Date: {flight_date} ({departure_time} - {arrival_time})\n"
            f"  • Price: {currency} {price} | Seats Left: {available_seats}"
        )
    return "\n".join(lines)


def format_hotels(hotels):
    lines = ["**🏨 Hotels:**"]
    for hotel in hotels:
        h_id = hotel.get("_id", "Unknown ID")
        name = hotel.get("name") or "Unknown Hotel"
        
        location = hotel.get("location")
        city = hotel.get("city") or (location.get("city") if isinstance(location, dict) else "Unknown City")
        
        price_per_night = hotel.get("pricePerNight") or "N/A"
        currency = hotel.get("currency") or hotel.get("price") or ""
        
        lines.append(f"- **{name}** (`{h_id}`) in {city} — {currency} {price_per_night} per night")
    return "\n".join(lines)


def call_chat_api(message):
    payload = json.dumps({"message": message}).encode("utf-8")
    request = Request(API_URL, data=payload, headers={"Content-Type": "application/json"})

    try:
        response = urlopen(request, timeout=15)
        data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return f"⚠️ **Connection Error:** Could not reach backend at `{API_URL}`. Is your FastAPI server running?\n\n*Details: {exc}*"
    except Exception as exc:
        return f"⚠️ **Unexpected Error:** {exc}"

    chat_text = data.get("response", "No response returned.")
    parts = [chat_text]

    if data.get("flights"):
        parts.append(format_flights(data["flights"]))
    if data.get("hotels"):
        parts.append(format_hotels(data["hotels"]))

    return "\n\n".join(parts)


def respond(user_message, history):
    if not user_message.strip():
        return "", history

    if history is None:
        history = []

    # Get answer from FastAPI backend
    bot_response = call_chat_api(user_message)
    
    # Append dictionary format required by Gradio 5
    new_history = list(history) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_response}
    ]
    
    return "", new_history


def main():
    with gr.Blocks(title="Trip Weaver") as demo:
        gr.Markdown(
            "# 🌍 Multi Agent Travel Planner Chat\n"
            "Ask the backend for flights, hotels, or travel plans. "
            f"Currently pointing to: `{API_URL}`"
        )
        
        chatbot = gr.Chatbot()
        message_input = gr.Textbox(
            label="Your message", 
            placeholder="Find me flights from CAN to HAN on 2025-11-15",
            lines=1
        )
        submit_btn = gr.Button("Send", variant="primary")

        submit_btn.click(
            respond, 
            inputs=[message_input, chatbot], 
            outputs=[message_input, chatbot]
        )
        message_input.submit(
            respond, 
            inputs=[message_input, chatbot], 
            outputs=[message_input, chatbot]
        )

    demo.launch()


if __name__ == "__main__":
    main()
    