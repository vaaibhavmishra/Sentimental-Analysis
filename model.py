from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

def classify_text(text, max_length=512):
    try:
        # Ensure the input is a string
        if not isinstance(text, str):
            raise ValueError("Input text must be a string.")
        
        # Tokenize input text with a maximum length constraint
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=max_length)
        outputs = model(**inputs)

        # Get prediction probabilities and labels
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        sentiment = torch.argmax(predictions).item()

        # Map sentiment to human-readable labels
        sentiment_map = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
        return sentiment_map.get(sentiment, "Unknown")
    except Exception as e:
        # Log the error and skip the review
        return None
