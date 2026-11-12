# Simple LLM App

Pass a user message to Grok and display the reply.

## Setup

1. I have given cursor the prompt which generates the boiler template code based on the requirement.
2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Visit https://console.groq.com/keys to generate GROQ API key and copy that key.

3. Copy `.env.example` to `.env` and put your GROQ API key in it:

```
GROQ_API_KEY==your-groq-api-key-here
```

4. Run the app:

```bash
streamlit run app.py
(or)
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The app opens in your browser. Type a message, click **Send**, and the model response appears below.
