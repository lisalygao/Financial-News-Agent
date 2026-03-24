import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    # This is the "Vibe Check" to see if the app is alive
    return "Market News Aggregator is LIVE on Google Cloud!"

if __name__ == "__main__":
    # This line solves your "Port" error. 
    # It looks for the $PORT variable Google provides, or defaults to 8080.
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host='0.0.0.0', port=port)