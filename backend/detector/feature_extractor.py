import re
import pandas as pd
import numpy as np
from urllib.parse import urlparse

def extract_url_features(url, FEATURES):
    X = pd.DataFrame(np.zeros((1, len(FEATURES))), columns=FEATURES)

    parsed = urlparse(url)
    hostname = parsed.netloc

    X["length_url"] = len(url)
    X["length_hostname"] = len(hostname)
    X["nb_dots"] = url.count(".")
    X["nb_hyphens"] = url.count("-")
    X["nb_at"] = url.count("@")
    X["nb_slash"] = url.count("/")
    X["nb_www"] = 1 if "www" in url else 0
    X["https_token"] = 1 if url.startswith("https") else 0

    ip_pattern = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    X["ip"] = 1 if ip_pattern.search(url) else 0

    digits = sum(c.isdigit() for c in url)
    X["ratio_digits_url"] = digits / len(url) if len(url) else 0

    return X
