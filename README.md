# First Simple LLM App

Pass a user message to Grok and display the reply.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and put your xAI API key in it:

```
XAI_API_KEY=your-xai-api-key-here
```

3. Run the app:

```bash
streamlit run app.py
```

The app opens in your browser. Type a message, click **Send**, and the model response appears below.
