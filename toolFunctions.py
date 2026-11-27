from urllib import response
from dotenv import load_dotenv
import requests
import os
from gmail_toolService import (
    get_gmail_service, read_email, send_email, search_emails)

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_weather(city: str):
    # Get city coordinates
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_response = requests.get(
        geo_url,
        params={"name": city, "count": 1},
        timeout=10
    )
    geo_response.raise_for_status()

    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return {"error": f"City '{city}' not found"}

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    # Get current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_response = requests.get(
        weather_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m"
            ]
        },
        timeout=10
    )
    weather_response.raise_for_status()

    weather_data = weather_response.json()

    return {
        "city": city,
        "temperature": weather_data["current"]["temperature_2m"],
        "humidity": weather_data["current"]["relative_humidity_2m"],
        "wind_speed": weather_data["current"]["wind_speed_10m"]
    }
    
def call_apitube(endpoint, params):
    BASE_URL = "https://api.apitube.io/v1/news"

    if not NEWS_API_KEY:
        raise RuntimeError("NEWS_API_KEY is missing")

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"X-API-Key": NEWS_API_KEY},
        params=params,
        timeout=20
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"APITube error {response.status_code}: {response.text}"
        )

    return response.json()

def format_articles(data):

    articles = []

    for article in data.get("results", []):

        source = article.get("source") or {}

        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "source": source.get("domain"),
            "url": article.get("href"),
            "published_at": article.get("published_at"),
            "language": article.get("language"),
            "distance_km": article.get("distance_km")
        })

    return articles

def get_news(
    query=None,
    location=None,
    country=None,
    mode="auto",
    page_size=10,
    published_after="NOW"
):
    page_size = min(max(page_size, 1), 10)

    try:
        # Local news
        if mode == "local" or (mode == "auto" and location):

            radii = [50, 200, 500]

            for radius in radii:
                params = {
                    "place": location,
                    "radius": radius,
                    "sort": "relevance",
                    "ranking": "fresh",
                    "per_page": page_size,
                    "published_at.start": published_after
                }

                if country:
                    params["country"] = country

                if query:
                    params["query"] = query

                data = call_apitube("local", params)
                articles = format_articles(data)

                if articles:
                    return {
                        "status": "success",
                        "search_type": "local",
                        "location": location,
                        "articles": articles
                    }

            # Broaden to general location-based search
            params = {
                "location.name": location,
                "per_page": page_size,
                "sort.by": "published_at"
            }

            if query:
                params["query"] = query

            data = call_apitube("everything", params)
            articles = format_articles(data)

        # Top headlines
        elif mode == "headlines" or (mode == "auto" and not query):
            data = call_apitube(
                "top-headlines",
                {
                    "per_page": page_size,
                    "language.code": "en"
                }
            )

            articles = format_articles(data)

        # General topic or keyword search
        else:
            params = {
                "query": query,
                "per_page": page_size,
                "sort.by": "published_at"
            }

            if published_after:
                params["published_at.start"] = published_after

            data = call_apitube("everything", params)
            articles = format_articles(data)

        if articles:
            return {
                "status": "success",
                "search_type": "general",
                "articles": articles
            }

        return {
            "status": "no_results",
            "message": "No matching articles found. Try broader search terms or another date range.",
            "articles": []
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"News API request failed: {str(e)}",
            "articles": []
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "articles": []
        }
        

# def execute_tool(tool_name, arguments, gmail_service):

#     if tool_name == "search_emails":

#         return search_emails(
#             gmail_service,
#             arguments["query"],
#             arguments["max_results"]
#         )

#     elif tool_name == "read_email":

#         return read_email(
#             gmail_service,
#             arguments["message_id"]
#         )

#     elif tool_name == "send_email":

#         # Show the email before sending
#         print("\n----- EMAIL PREVIEW -----")
#         print("To:", arguments["to"])
#         print("Subject:", arguments["subject"])
#         print("Body:", arguments["body"])
#         print("-------------------------")

#         confirmation = input(
#             "Do you want to send this email? (yes/no): "
#         ).strip().lower()

#         if confirmation not in ["yes", "y"]:
#             return {
#                 "status": "cancelled",
#                 "message": "User declined sending the email."
#             }

#         return send_email(
#             gmail_service,
#             arguments["to"],
#             arguments["subject"],
#             arguments["body"]
#         )

#     else:
#         raise ValueError(f"Unknown tool: {tool_name}")
