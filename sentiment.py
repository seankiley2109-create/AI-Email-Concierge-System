from google import genai
from google.genai.types import HttpOptions
from google.genai import types
from google.cloud import language_v2
from langsmith import traceable

@traceable
def analyze_sentiment(email_text: str) -> dict:
    """
    Analyzes the sentiment of a given text using the Google Cloud Natural Language API
    and returns a detailed dictionary containing sentiment scores, magnitude,
    language, and sentiment breakdown by sentence.

    This function utilizes the `language_v2.LanguageServiceClient` to process the
    input text and determine its overall sentiment, as well as the sentiment of
    individual sentences within the text.

    The sentiment is categorized into "Very unhappy", "Unhappy", "Neutral",
    "Happy", and "Very Happy" based on predefined score ranges.

    Args:
        text (str): The input text (e.g., content of an email or message) to be
                    analyzed for sentiment.

    Returns:
        dict: A dictionary containing the sentiment analysis results.
              The structure of the dictionary is as follows:
              {
                  "sentiment_category": str,  # Overall sentiment ("Very unhappy", "Happy", etc.)
                  "score": float,             # Overall sentiment score (-1.0 to 1.0)
                  "magnitude": float,         # Overall sentiment magnitude (0.0 to +inf)
                  "language": str,            # Detected language of the text (e.g., "en")
                  "sentences": list           # List of dictionaries, each representing a sentence:
                      [
                          {
                              "text": str,          # The content of the sentence
                              "score": float,       # Sentiment score for the sentence
                              "magnitude": float,   # Sentiment magnitude for the sentence
                              "sentiment_label": str # Categorized sentiment for the sentence
                          },
                          ...
                      ]
              }
    """

    client = language_v2.LanguageServiceClient()

    document = {
        "content": email_text,
        "type_": language_v2.Document.Type.PLAIN_TEXT,
    }

    encoding_type = language_v2.EncodingType.UTF8

    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    score = response.document_sentiment.score
    magnitude = response.document_sentiment.magnitude

    def interpret_score(score: float) -> str:
        if score <= -0.35:
            return "Very unhappy"
        elif score <= -0.1:
            return "Unhappy"
        elif score < 0.25:
            return "Neutral"
        elif score < 0.75:
            return "Happy"
        else:
            return "Very Happy"

    result = {
        "sentiment_category": interpret_score(score),
        "score": score,
        "magnitude": magnitude,
        "language": response.language_code,
        "sentences": []
    }

    for sentence in response.sentences:
        sentence_score = sentence.sentiment.score
        result["sentences"].append({
            "text": sentence.text.content,
            "score": sentence_score,
            "magnitude": sentence.sentiment.magnitude,
            "sentiment_label": interpret_score(sentence_score)
        })

    return result
