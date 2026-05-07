def format_output(text):
    return text.strip()


def normalize_symbol(symbol):
    return (symbol or "").strip().upper()


def sentiment_for_text(text):
    positive = {"beat", "gain", "growth", "up", "surge", "bull", "profit", "strong"}
    negative = {"miss", "loss", "down", "fall", "bear", "weak", "lawsuit", "risk"}
    words = set((text or "").lower().replace("-", " ").split())
    score = len(words & positive) - len(words & negative)
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"
