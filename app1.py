from flask import Flask, request, jsonify, render_template
import pandas as pd
from model import classify_text  # Import the model logic

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Home.html')  # Render your HTML page
    
@app.route('/predict', methods=['POST'])
def predict():
    # Get the input text from the request
    data = request.json
    text = data.get("text", "")

    # Use the ML model to classify the text
    sentiment = classify_text(text)

    # Return the result as a JSON response
    return jsonify({"sentiment": sentiment})

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    try:
        # Read the uploaded CSV file into a DataFrame
        df = pd.read_csv(file)

        # Check if the necessary column exists
        if 'Review' not in df.columns:
            return jsonify({"error": "CSV must contain a 'text' column"}), 400

        # Classify each text entry in the CSV
        sentiment_counts = {'Very Positive': 0, 'Positive': 0, 'Neutral': 0, 'Negative': 0, 'Very Negative': 0}
        for text in df['Review']:
            sentiment = classify_text(text)
            if sentiment == 'Very Positive':
                sentiment_counts['Very Positive'] += 1
            elif sentiment == 'Positive':
                sentiment_counts['Positive'] += 1
            elif sentiment == 'Neutral':
                sentiment_counts['Neutral'] += 1
            elif sentiment == 'Negative':
                sentiment_counts['Negative'] += 1
            elif sentiment == 'Very Negative':
                sentiment_counts['Very Negative'] += 1

        # Return the sentiment counts as a JSON response
        return jsonify({"sentiment_counts": sentiment_counts})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
