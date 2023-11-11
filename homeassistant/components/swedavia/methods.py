
import aiohttp
import asyncio
from flight_data import FlightInfo


async def fetch_flight_info(airport, scheduled, flight_type, flight_id):
    base_url = "https://api.swedavia.se/flightinfo/v2/query"
    
    filter_params = f"airport eq '{airport}' and scheduled eq '{scheduled}' and flightType eq '{flight_type}' and flightId eq '{flight_id}'"
    url = f"{base_url}?filter={filter_params}"

    headers = {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': 'f6483fdb85134f6e91deade69410175b',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
              
                module_instance = FlightInfo.from_dict(data)
             

                return module_instance
               
            else:
                raise Exception(f"Failed to fetch flight info. Status code: {response.status}")

async def main():
    airport = "ARN"
    scheduled = "240101"
    flight_type = "A"
    flight_id = "ET714"

    try:
        flight_info = await fetch_flight_info(airport, scheduled, flight_type, flight_id)
        # Access information using the Module instance
        for flight in flight_info.flights:
            if flight_type=="D":
                departure = flight.departure
                print(f"Flight ID: {departure.flight_id}")
                print(f"Departure Airport (Swedish): {departure.arrival_airport_swedish}")
                print(f"Departure Airport (English): {departure.arrival_airport_english}")
                print(f"Airline Operator: {departure.airline_operator.name}")
                print(f"Departure Time (UTC): {departure.departure_time.scheduled_utc}")
                print(f"Terminal: {departure.location_and_status.terminal}")
                print(f"Flight Leg Status: {departure.location_and_status.flight_leg_status}")
            else:
                arrival = flight.arrival
                print(f"Flight ID: {arrival.flight_id}")
                print(f"Arrival Airport (Swedish): {arrival.departure_airport_swedish}")
                print(f"Arrival Airport (English): {arrival.departure_airport_english}")
                print(f"Airline Operator: {arrival.airline_operator.name}")
                print(f"Arrival Time (UTC): {arrival.arrival_time.scheduled_utc}")
                print(f"Terminal: {arrival.location_and_status.terminal}")
                print(f"Flight Leg Status: {arrival.location_and_status.flight_leg_status}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise 

if __name__ == "__main__":
    asyncio.run(main())
