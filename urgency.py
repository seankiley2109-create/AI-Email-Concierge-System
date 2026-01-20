from google import genai
from langsmith import traceable

@traceable
def define_urgency(category: str, sentiment: str) -> str:
    """
    Calculates an urgency score based on the category of the customer interaction
    and the sentiment expressed by the customer.

    The urgency score is determined by:
    1.  **Category:** Different categories are assigned varying urgency points.
        -   Aftersales categories (Shipping, Returns, Claims, Payment) add 3 points.
        -   Presales/Aftersales categories (Product Consultation, Order Support,
            Technical Assistance, Customer Account) add 2 points.
        -   Less urgent categories (Loyalty Programs, Customer Feedback) add 1 point.
    2.  **Sentiment:** Customer sentiment further modifies the urgency.
        -   "Very unhappy" sentiment adds 2 points.
        -   "Unhappy" sentiment adds 1 point.

    The final urgency score is the sum of points from both category and sentiment.

    Args:
        category (str): The classification of the customer interaction (e.g.,
                        "Shipping and Delivery Updates (Aftersales)",
                        "Product Consultation (Presales)").
        sentiment (str): The sentiment expressed by the customer (e.g.,
                         "Very unhappy", "Unhappy", "Neutral", "Happy").

    Returns:
        int: An integer representing the calculated urgency score.
             A higher score indicates greater urgency.
    """

    urgency_score = 0

    if category in ["Shipping and Delivery Updates", 
                    "Returns and Exchanges Management",
                    "Claims and Product Defects",
                   "Payment and Billing Support"]:
        urgency_score += 3
    elif category in ["Product Consultation", 
                      "Order Support",
                     "Technical Assistance",
                      "Customer Account Support"]:
        urgency_score += 2
    elif category in ["Loyalty Programs and Discounts", 
                      "Customer Feedback and Complaints"]:
        urgency_score += 1

    if sentiment == "Very unhappy":
        urgency_score += 2
    elif sentiment == "Unhappy":
        urgency_score += 1

    return urgency_score

