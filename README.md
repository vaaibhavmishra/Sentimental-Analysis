# Sentivista — AI Sentiment Analysis

A web application that leverages **BERT (Bidirectional Encoder Representations from Transformers)** for multilingual sentiment analysis. Analyze individual text or bulk CSV files and get results with confidence scores, interactive charts, and exportable data.

## Features

- **Single Text Analysis** — Enter text and get instant sentiment detection with confidence scores
- **Real-time Detection** — See sentiment change as you type (debounced)
- **CSV Bulk Analysis** — Upload a CSV file with a `Review` column for batch processing
- **Interactive Charts** — Donut chart visualization powered by Chart.js
- **Per-Row Results** — See sentiment for each review in a sortable table
- **CSV Export** — Download analysis results as a new CSV
- **Emoji & Color Coding** — Visual sentiment indicators (😊 😟 😡 etc.)
- **Confidence Scores** — See how confident the model is in each prediction

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.1 (App Factory Pattern) |
| ML Model | `nlptown/bert-base-multilingual-uncased-sentiment` via HuggingFace Transformers |
| Frontend | Vanilla HTML/CSS/JS + Chart.js |
| Inference | PyTorch with `torch.no_grad()` optimized batching |

## Project Structure

```
sentivista/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/
│   │   ├── main.py          # Home, analyzer, health check
│   │   └── analysis.py      # /predict, /upload_csv endpoints
│   ├── services/
│   │   └── sentiment.py     # BERT model service (lazy-loading singleton)
│   ├── templates/
│   │   ├── home.html        # Landing page
│   │   └── analyzer.html    # Sentiment analyzer page
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── config.py                # Dev/prod configuration
├── run.py                   # Entry point
├── requirements.txt
├── run_project.sh
├── .env.example
└── sample.csv
```

## How to Run

1. **Prerequisites**: Python 3.9+

2. **Quick Start**:
   ```bash
   chmod +x run_project.sh
   ./run_project.sh
   ```

   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python run.py
   ```

3. **Access**: Open `http://127.0.0.1:8000`

4. **Environment** (optional): Copy `.env.example` to `.env` and customize:
   ```bash
   cp .env.example .env
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Landing page |
| `GET` | `/analyze` | Sentiment analyzer page |
| `GET` | `/health` | Health check |
| `POST` | `/predict` | Analyze single text (JSON body: `{"text": "..."}`) |
| `POST` | `/upload_csv` | Analyze CSV file (multipart form with `file` field) |

### Example: `/predict`

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'
```

Response:
```json
{
  "label": "Very Positive",
  "confidence": 0.9234,
  "emoji": "😊"
}
```

## Team

- Avni Sharma, Vidhika Rastogi, Vaibhav Mishra, Shreeram Susekhar Pani, Rajhav Bhadwal
- **Supervisor**: Dr. Garima Jain

> **Note**: On first run, the application downloads a ~700MB model file. Please be patient.