import os
import httpx

BASE_URL = os.environ.get('ASSISTANT_API_URL', 'http://127.0.0.1:8000').rstrip('/')

def request(method: str, path: str, data=None, params=None):
    try:
        endpoint = BASE_URL + '/api' + path
        response = httpx.request(method, endpoint, json=data, params=params, timeout=5)
    except httpx.RequestError:
        raise ValueError('Cannot connect to the backend. Check that it is running.') from None

    if not response.is_success:
        try:
            detail = response.json().get('detail', 'Request failed.')
        except ValueError:
            detail = 'The backend returned an error.'

        if isinstance(detail, list):
            detail = 'Invalid request data.'

        raise ValueError(detail)

    return response.json()
