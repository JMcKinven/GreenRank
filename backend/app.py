from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return jsonify({"message": "GreenRank API is running!"})

@app.route('/api/companies')
def get_companies():
    # Mock data for now
    companies = [
        {"id": 1, "name": "EcoTech Corp", "sustainability_score": 4.5, "sector": "Technology"},
        {"id": 2, "name": "Green Manufacturing", "sustainability_score": 3.8, "sector": "Manufacturing"},
        {"id": 3, "name": "Sustainable Foods", "sustainability_score": 4.2, "sector": "Food"}
    ]
    return jsonify(companies)

if __name__ == '__main__':
    app.run(debug=True)