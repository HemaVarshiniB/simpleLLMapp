<video width="400" controls>
  <source src="./demo.mp4" type="video/mp4">
</video>


This project is the part of learning and practicing AI.

## Title
Build your first LLM application
Create a Python application that accepts user input and sends it to an OpenAI model.

## Requirements
- Accept input from the terminal.
- Send a request to the API.
- Display the model's response.
- Handle API errors.
- Track input and output token usage.

## Setup
1. 
```bash 
mkdir my_python_project
cd my_python_project 
```

2. Create a virtual environment, activate it and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Visit https://console.groq.com/keys to generate GROQ API key and copy that key.

3. Create `.env` and put your GROQ API key in it:

```
GROQ_API_KEY==your-groq-api-key-here
GROQ_URL=https://api.groq.com/openai/v1
```

4. Run the app:

```bash
python run app.py
```

The app opens in your terminal. 
