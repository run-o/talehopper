import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock
from app.main import app
from fastapi import Request



@pytest.fixture
def mock_story_generator():
    with patch('app.api.routes.story.llm_generate_story',
               return_value=("Test paragraph", ["Choice 1", "Choice 2", "Choice 3"])):
        yield

@pytest.fixture
def story_request_payload():
    return {
        "prompt": {
            "age": 8,
            "language": "english",
            "length": 5
        },
        "history": [],
        "choice": None
    }

def test_rate_limit_enforcement(client: TestClient, mock_story_generator, story_request_payload):
    """
    Test that the rate limit of 10 requests per minute is enforced on the generate_story endpoint.
    """ 
    # Patch both get_remote_address and Request.client.host
    with patch('slowapi.util.get_remote_address', return_value='127.0.0.1'), \
         patch.object(Request, 'client') as mock_client:
        # Set up the mock client.host property
        type(mock_client).host = PropertyMock(return_value='127.0.0.1')
        
        # Simulate 10 successful requests
        for _ in range(10):
            response = client.post('/story/generate', json=story_request_payload)
            assert response.status_code == 200
            assert 'history' in response.json()
            assert 'choices' in response.json()

        # 11th request should be rate limited
        response = client.post('/story/generate', json=story_request_payload)
        assert response.status_code == 429
        assert response.json()['detail'] == 'Rate limit exceeded. Please slow down.'


def test_rate_limit_different_ip(client: TestClient, mock_story_generator, story_request_payload):
    """
    Test that rate limiting is applied per IP address.
    """    
    # First IP address (but different from other test):
    # patch both get_remote_address and Request.client.host
    with patch('slowapi.util.get_remote_address', return_value='127.0.0.2'), \
         patch.object(Request, 'client') as mock_client:
        # Set up the mock client.host property
        type(mock_client).host = PropertyMock(return_value='127.0.0.2')
        
        # Make 10 successful requests
        for _ in range(10):
            response = client.post('/story/generate', json=story_request_payload)
            assert response.status_code == 200

        # 11th request from first IP should be rate limited
        response = client.post('/story/generate', json=story_request_payload)
        assert response.status_code == 429

    # Different IP address:
    with patch('slowapi.util.get_remote_address', return_value='127.0.0.3'), \
         patch.object(Request, 'client') as mock_client:
        # Set up the mock client.host property
        type(mock_client).host = PropertyMock(return_value='127.0.0.3')
        
        response = client.post('/story/generate', json=story_request_payload)
        assert response.status_code == 200  # This request should succeed as it's from a different IP
