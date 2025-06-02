from flask import Flask, request, jsonify
from flask_cors import CORS
import http.client
import json

app = Flask(__name__)
CORS(app)

API_KEY = "6e34518ed9msh5837db118f9169cp1caad1jsna30cf9d75d37"
API_HOST = "deepseek-all-in-one.p.rapidapi.com"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Prepare the payload for DeepSeek API
        payload = json.dumps({
            "messages": [{
                "role": "user",
                "content": user_message
            }]
        })

        # Set up the connection
        conn = http.client.HTTPSConnection(API_HOST)
        
        # Set up headers
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': API_HOST,
            'Content-Type': "application/json"
        }

        # Make the request
        conn.request("POST", "/reasoner", payload, headers)
        
        # Get the response
        response = conn.getresponse()
        response_data = json.loads(response.read().decode("utf-8"))
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001) 