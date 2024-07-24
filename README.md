# Nikles-ML-service

Clone repository

Create a folder in the root path named 'logs'

Create a virtual environment:
`py -3.11 -m venv env`
`env\Scripts\activate`

Run these commands:
`pip install -r requirements.txt`
`uvicorn app.main:app --host 0.0.0.0 --port [port number] --reload`

Go to swagger, create a post request with the address: `http://localhost:8000/api/chatfromlocalpdf`
request body:  
{
  "question": "what colors are in nikles luxury finish?",
  "session_id": "1234"
}
