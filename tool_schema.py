my_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city"]
            }
        }
    },
    { 
        "type": "function",
        "function": {
            "name": "get_news",
            "description": """
            Retrieve news articles for any user news request.

            Understand the user's intent and extract:
            - query: Boolean news search terms, such as
            'AI OR artificial intelligence'.
            - location: City, region, or country if the user
            requests location-specific news.
            - country: Two-letter country code if known.
            - mode: local for location news, search for
            topic searches, headlines for general headlines,
            auto otherwise.
            - published_after: Date filter such as NOW-1DAY
            or NOW-7DAYS.

            Do not invent search results or locations.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": ["string", "null"],
                        "description": "News search terms in APITube Boolean query syntax."
                    },
                    "location": {
                        "type": ["string", "null"],
                        "description": "Location for local news."
                    },
                    "country": {
                        "type": ["string", "null"],
                        "description": "Two-letter country code, such as us, tr, gb."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "local", "search", "headlines"]
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of articles to retrieve. Maximum 10 on the Free plan."
                    },
                    "published_after": {
                        "type": ["string", "null"],
                        "description": "APITube date filter, such as NOW-1DAY or NOW-7DAYS."
                    }
                },
                "required": ["query", "location", "country", "mode"]
            }
        }
    }

]