import os
import httpx

BASE_URL = os.environ.get('ASSISTANT_API_URL', 'http://127.0.0.1:8000').rstrip('/')

# Define validation error messages for all fields.
FIELD_ERROR_MESSAGES = {
    'name': 'Enter a non-empty name. Names must be unique.',
    'email': 'Enter an email address in the form name@example.com, or use "" to clear it.',
    'phone': 'Enter a phone number containing exactly 10 digits.',
    'new_phone': 'Enter a new phone number containing exactly 10 digits.',
    'old_phone': 'Enter the existing phone number containing exactly 10 digits.',
    'address': 'Enter a non-empty address, or use "" to clear it.',
    'birthday': 'Enter a valid date in DD.MM.YYYY format, or use "" to clear it.',
    'text': 'Enter non-empty note text.',
    'days': 'Enter a number of days from 0 to 366.',
    'id': 'Enter a valid note ID.',
}

# Build validation error messages for all fields.
def format_validation_errors(errors):
    messages = []

    for error in errors:
        # FastAPI locations begin with the request part, such as "body" or "query".
        location = [str(part) for part in error.get('loc', ()) if part not in ('body', 'query', 'path')]
        # Find the field name.
        field_name = ''
        for part in location:
            part = part.lower()
            for name in FIELD_ERROR_MESSAGES:
                if part == name or part.startswith(f'{name}.') or part.startswith(f'{name}['):
                    field_name = name
                    break

            if field_name:
                break

        field = field_name or '.'.join(location)
        message = FIELD_ERROR_MESSAGES.get(field_name, error.get('msg', 'Invalid value.'))

        field_label = field.capitalize()
        messages.append(f'{field_label}: {message}' if field else message)

    return ' '.join(messages) or 'Invalid request data.'


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
            detail = format_validation_errors(detail)

        raise ValueError(detail)

    return response.json()
