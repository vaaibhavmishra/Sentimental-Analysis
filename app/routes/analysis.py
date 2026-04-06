import logging

import pandas as pd
from flask import Blueprint, request, jsonify, current_app

from app.services.sentiment import sentiment_service

logger = logging.getLogger(__name__)

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/predict", methods=["POST"])
def predict():
    """Classify a single text input."""
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Text cannot be empty"}), 400

    max_length = current_app.config.get("MAX_TEXT_LENGTH", 5000)
    if len(text) > max_length:
        return jsonify({"error": f"Text too long (max {max_length} characters)"}), 400

    model_name = current_app.config["MODEL_NAME"]
    result = sentiment_service.analyze_single(text, model_name)

    if result is None:
        return jsonify({"error": "Failed to analyze sentiment"}), 500

    return jsonify(result)


@analysis_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    """Analyze sentiments from an uploaded CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename or not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported"}), 400

    try:
        df = pd.read_csv(file)

        if "Review" not in df.columns:
            return jsonify({"error": "CSV must contain a 'Review' column"}), 400

        texts = df["Review"].tolist()
        model_name = current_app.config["MODEL_NAME"]

        # Batch inference
        results = sentiment_service.analyze_batch(texts, model_name)

        # Build per-row results and aggregate counts
        sentiment_counts = {
            "Very Positive": 0,
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0,
            "Very Negative": 0,
        }
        per_row = []
        error_count = 0

        for i, result in enumerate(results):
            review_text = str(texts[i])[:100]  # Truncate for response
            if result is None:
                error_count += 1
                per_row.append({
                    "row": i + 1,
                    "text": review_text,
                    "label": "Error",
                    "confidence": 0,
                    "emoji": "⚠️",
                })
            else:
                sentiment_counts[result["label"]] += 1
                per_row.append({
                    "row": i + 1,
                    "text": review_text,
                    "label": result["label"],
                    "confidence": result["confidence"],
                    "emoji": result["emoji"],
                })

        total = len(texts)
        return jsonify({
            "sentiment_counts": sentiment_counts,
            "per_row": per_row,
            "total": total,
            "errors": error_count,
        })

    except pd.errors.EmptyDataError:
        return jsonify({"error": "The CSV file is empty"}), 400
    except Exception as e:
        logger.error(f"CSV analysis failed: {e}")
        return jsonify({"error": f"Failed to process CSV: {str(e)}"}), 500
