import logging
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

SENTIMENT_MAP = {
    0: "Very Negative",
    1: "Negative",
    2: "Neutral",
    3: "Positive",
    4: "Very Positive",
}

SENTIMENT_EMOJI = {
    "Very Negative": "😡",
    "Negative": "😟",
    "Neutral": "😐",
    "Positive": "🙂",
    "Very Positive": "😊",
}


class SentimentService:
    """Lazy-loading singleton for the BERT sentiment model."""

    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self, model_name: str) -> None:
        """Load model and tokenizer on first use."""
        if self._model is None:
            logger.info(f"Loading sentiment model: {model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                model_name
            )
            self._model.eval()
            logger.info("Model loaded successfully")

    def analyze_single(self, text: str, model_name: str, max_length: int = 512) -> Optional[dict]:
        """Classify a single text and return label + confidence."""
        self._load_model(model_name)

        try:
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Input text must be a non-empty string.")

            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=max_length,
            )

            with torch.no_grad():
                outputs = self._model(**inputs)

            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()

            label = SENTIMENT_MAP.get(predicted_class, "Unknown")
            return {
                "label": label,
                "confidence": round(confidence, 4),
                "emoji": SENTIMENT_EMOJI.get(label, ""),
            }

        except Exception as e:
            logger.error(f"Sentiment classification failed for text: {e}")
            return None

    def analyze_batch(
        self, texts: list[str], model_name: str, max_length: int = 512, batch_size: int = 16
    ) -> list[Optional[dict]]:
        """Classify a batch of texts efficiently."""
        self._load_model(model_name)
        results = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]

            # Filter valid strings
            valid_indices = []
            valid_texts = []
            for j, text in enumerate(batch_texts):
                if isinstance(text, str) and text.strip():
                    valid_indices.append(j)
                    valid_texts.append(text)

            # Initialize batch results with None
            batch_results = [None] * len(batch_texts)

            if not valid_texts:
                results.extend(batch_results)
                continue

            try:
                inputs = self._tokenizer(
                    valid_texts,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=max_length,
                )

                with torch.no_grad():
                    outputs = self._model(**inputs)

                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_classes = torch.argmax(probabilities, dim=-1)

                for k, idx in enumerate(valid_indices):
                    cls_id = predicted_classes[k].item()
                    conf = probabilities[k][cls_id].item()
                    label = SENTIMENT_MAP.get(cls_id, "Unknown")
                    batch_results[idx] = {
                        "label": label,
                        "confidence": round(conf, 4),
                        "emoji": SENTIMENT_EMOJI.get(label, ""),
                    }

            except Exception as e:
                logger.error(f"Batch classification failed: {e}")

            results.extend(batch_results)

        return results


# Module-level singleton
sentiment_service = SentimentService()
