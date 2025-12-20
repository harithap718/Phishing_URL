import os
import joblib
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import URLSerializer
from .feature_extractor import extract_url_features

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "phishing_rf_model.pkl")

data = joblib.load(MODEL_PATH)
model = data["model"]
FEATURES = data["features"]
TRUSTED_DOMAINS = [
    "google.com",
    "www.google.com",
    "paypal.com",
    "www.paypal.com",
    "amazon.com",
    "www.amazon.com",
    "facebook.com",
    "www.facebook.com"
]


# ---------------- RULE-BASED SECURITY ----------------
SUSPICIOUS_KEYWORDS = [
    "google", "paypal", "facebook", "amazon",
    "apple", "microsoft", "bank", "login", "secure"
]

def is_suspicious_url(url):
    url_lower = url.lower()

    if len(url) > 75:
        return True, "Very long URL"

    for c in set(url_lower):
        if url_lower.count(c) > 6:
            return True, "Repeated characters detected"

    digits = sum(c.isdigit() for c in url)
    if digits > 5:
        return True, "Excessive digits in URL"

    for brand in SUSPICIOUS_KEYWORDS:
        if brand in url_lower and not url_lower.startswith(f"https://www.{brand}."):
            return True, f"Brand misuse: {brand}"

    return False, None

# ---------------- API VIEW ----------------
@api_view(["POST"])
def predict_phishing(request):
    serializer = URLSerializer(data=request.data)

    if serializer.is_valid():
        url = serializer.validated_data["url"]
        url_lower = url.lower()

        # ---------- 1. TRUSTED DOMAIN CHECK ----------
        for domain in TRUSTED_DOMAINS:
            if domain in url_lower:
                return Response({
                    "prediction": "legitimate (trusted domain)",
                    "confidence": 0.99,
                    "reason": "Trusted domain whitelist"
                })

        # ---------- 2. RULE-BASED CHECK ----------
        rule_flag, reason = is_suspicious_url(url)

        # ---------- 3. ML PREDICTION ----------
        X = extract_url_features(url, FEATURES)
        prob = model.predict_proba(X).max()
        pred = model.predict(X)[0]

        # ---------- 4. FINAL DECISION ----------
        if rule_flag:
            label = "phishing (rule-based)"
        elif pred == 1 and prob >= 0.6:
            label = "phishing"
        else:
            label = "legitimate"

        return Response({
            "prediction": label,
            "confidence": round(float(prob), 3),
            "reason": reason
        })

    return Response(serializer.errors, status=400)
