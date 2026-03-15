"""Shared HTTP request logic for subgraph API calls.

Provides exponential-backoff retry so every fetcher benefits without
duplicating error-handling code.
"""

import time
import requests


def subgraph_post(url: str, query: str, max_retries: int = 5) -> dict:
    """POST a GraphQL query with exponential backoff retry.

    Returns the parsed JSON response dict, or None if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json={"query": query}, timeout=30)
            if response.status_code == 200:
                return response.json()
            print(f"HTTP {response.status_code} on attempt {attempt + 1}/{max_retries}")
        except requests.RequestException as exc:
            print(f"Request error on attempt {attempt + 1}/{max_retries}: {exc}")
        time.sleep(2 ** attempt)
    return None
