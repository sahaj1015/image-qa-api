# Image QA API

## Local test (optional)
```
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
uvicorn main:app --reload
```
Then visit http://127.0.0.1:8000 in a browser — you should see {"status": "ok", ...}

## Deploy on Render
1. Push this folder to a new GitHub repo.
2. Go to render.com -> New -> Web Service -> connect your repo.
3. Environment: Python 3
4. Build Command: pip install -r requirements.txt
5. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
6. Add Environment Variable: GEMINI_API_KEY = your_actual_key
7. Click Create Web Service and wait for deploy to finish.
8. Your public URL will look like: https://your-app-name.onrender.com
