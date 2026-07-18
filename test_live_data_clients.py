import sys
from unittest.mock import MagicMock

# Proactively mock 'requests' module in sys.modules so that live_data_clients
# can import it and bind it, regardless of whether it is installed in the environment.
mock_requests_lib = MagicMock()
sys.modules['requests'] = mock_requests_lib

# Import and ensure requests attributes are bound
import src.live_data_clients
src.live_data_clients.HAS_REQUESTS = True
src.live_data_clients.requests = mock_requests_lib

import pytest
from unittest.mock import patch
import time
from src.live_data_clients import RateLimiter, LiveDataClient, ClinicalTrialsClient, FAERSLiveClient


def test_rate_limiter_basic():
    """Verify rate limiter logs acquisition and respects maximum calls limit."""
    limiter = RateLimiter(max_per_minute=2)
    start_time = time.time()
    
    # First two calls should be instant
    limiter.acquire()
    limiter.acquire()
    duration = time.time() - start_time
    assert duration < 0.5


@patch('src.live_data_clients.requests')
def test_client_get_success(mock_req_class):
    """Verify that a successful GET request caches the response."""
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"ETag": "W/123456"}
    mock_response.json.return_value = {"status": "ok", "trials": [1, 2]}
    mock_req_class.get.return_value = mock_response

    client = LiveDataClient("https://example.com/api", rate_limit_per_min=100)
    
    # 1. First call (should hit network mock)
    res1 = client.get("endpoint", {"q": "test"})
    assert res1["_cached"] is False
    assert res1["data"] == {"status": "ok", "trials": [1, 2]}
    assert mock_req_class.get.call_count == 1

    # 2. Second call (should hit cache)
    res2 = client.get("endpoint", {"q": "test"})
    assert res2["_cached"] is True
    assert res2["data"] == {"status": "ok", "trials": [1, 2]}
    # Network mock call count should still be 1
    assert mock_req_class.get.call_count == 1


@patch('src.live_data_clients.requests')
def test_client_get_304_etag(mock_req_class):
    """Verify that ETag 304 response returns cached data."""
    # First request: 200 OK
    response_ok = MagicMock()
    response_ok.status_code = 200
    response_ok.headers = {"ETag": "etag_val"}
    response_ok.json.return_value = {"data": "fresh"}
    
    # Second request: 304 Not Modified
    response_not_modified = MagicMock()
    response_not_modified.status_code = 304
    
    mock_req_class.get.side_effect = [response_ok, response_not_modified]

    client = LiveDataClient("https://example.com/api", rate_limit_per_min=100)
    
    # Run first request to populate cache and set etag
    client.get("endpoint", use_cache=False)
    
    # Run second request (without using cached result directly)
    res = client.get("endpoint", use_cache=False)
    assert res["_cached"] is True
    assert res.get("_not_modified") is True
    assert res["data"] == {"data": "fresh"}


@patch('src.live_data_clients.requests')
def test_client_retry_on_errors(mock_req_class):
    """Verify client retries when encountering 500 server error or 429 rate limit."""
    # First response: 500 error
    response_error = MagicMock()
    response_error.status_code = 500
    
    # Second response: 200 OK
    response_ok = MagicMock()
    response_ok.status_code = 200
    response_ok.headers = {}
    response_ok.json.return_value = {"status": "recovered"}
    
    mock_req_class.get.side_effect = [response_error, response_ok]

    client = LiveDataClient("https://example.com/api", rate_limit_per_min=100, max_retries=3)
    
    res = client.get("endpoint", use_cache=False)
    assert res["_cached"] is False
    assert res["data"] == {"status": "recovered"}
    assert mock_req_class.get.call_count == 2


def test_clinical_trials_client_instantiation():
    """Verify specialized ClinicalTrialsClient properties."""
    client = ClinicalTrialsClient()
    assert client.base_url == "https://clinicaltrials.gov/api/v2"
    assert client.rate_limiter.max_per_minute == 50


def test_faers_client_instantiation():
    """Verify specialized FAERSLiveClient properties."""
    client = FAERSLiveClient(api_key="secret_key")
    assert client.base_url == "https://api.fda.gov/drug/event.json"
    assert client.api_key == "secret_key"
