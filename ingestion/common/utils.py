# ingestion/common/utils.py
import time
import requests
from typing import Any


def retry_request(url: str, retries: int = 3, delay: float = 2.0) -> requests.Response:
    """
    Simple retry logic for GET requests.
    """
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < retries:
                print(
                    f"Request failed (attempt {attempt}). Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"Request failed after {retries} attempts.")
                raise e
