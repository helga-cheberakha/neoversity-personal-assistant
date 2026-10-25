import pytest
from fastapi.testclient import TestClient
from personal_assistant.api import storage_base
from personal_assistant.api.app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Define test data directory.
    monkeypatch.setattr(storage_base, 'DATA_DIR', tmp_path)
    return TestClient(app)

# The launcher uses this endpoint to detect a running backend.
def test_health(client):
    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

def test_contact_create_update_delete(client):
    created = client.post('/api/contacts', json={
        'name': 'Clara Obrien',
        'phone': '0671234567',
    })
    assert created.status_code == 201
    assert created.json()['phones'] == ['0671234567']

    updated = client.put('/api/contacts/item', params={'name': 'Clara Obrien'}, json={
        'email': 'clara.obrien@example.com',
        'birthday': '25.10.1990',
    })
    assert updated.status_code == 200
    assert updated.json()['email'] == 'clara.obrien@example.com'
    assert updated.json()['birthday'] == '25.10.1990'

    deleted = client.delete('/api/contacts/item', params={'name': 'Clara Obrien'})
    assert deleted.status_code == 200
    assert client.get('/api/contacts').json() == []

def test_duplicate_contact_name_phone(client):
    client.post('/api/contacts', json={'name': 'Clara Obrien', 'phone': '0671234567'})
    response = client.post('/api/contacts', json={'name': 'clara obrien', 'phone': '0501234567'})
    repeated_phone = client.post('/api/contacts', json={'name': 'Clara Obrien', 'phone': '0501234567'})

    assert response.status_code == 201
    assert repeated_phone.status_code == 422
    assert repeated_phone.json()['detail'] == 'This phone number already exists for this contact.'
    
    contacts = client.get('/api/contacts').json()
    assert len(contacts) == 1
    assert contacts[0]['phones'] == ['0671234567', '0501234567']

@pytest.mark.parametrize('payload', [
    {'name': '   ', 'phone': '0671234567'},
    {'name': 'Clara', 'phone': '067-123-4567'},
    {'name': 'Clara', 'phone': '0671234567', 'email': 'clara@example'},
    {'name': 'Clara', 'phone': '0671234567', 'address': '   '},
    {'name': 'Clara', 'phone': '0671234567', 'birthday': '31.02.1990'},
])
def test_contact_invalid_values(client, payload):
    response = client.post('/api/contacts', json=payload)

    assert response.status_code == 422
    assert client.get('/api/contacts').json() == []

@pytest.mark.parametrize('method, url, kwargs', [
    ('get', '/api/contacts/item', {'params': {'name': 'Missing'}}),
    ('put', '/api/contacts/item', {'params': {'name': 'Missing'}, 'json': {'email': 'a@example.com'}}),
    ('delete', '/api/contacts/item', {'params': {'name': 'Missing'}}),
])
def test_missing_contact(client, method, url, kwargs):
    response = getattr(client, method)(url, **kwargs)

    assert response.status_code == 404

def test_note_create_update_delete(client):
    created = client.post('/api/notes', json={'text': 'Buy a birthday gift'})
    assert created.status_code == 201
    note_id = created.json()['id']

    updated = client.put('/api/notes/item', params={'id': note_id}, json={'text': 'Buy a book'})
    assert updated.status_code == 200
    assert updated.json()['text'] == 'Buy a book'

    deleted = client.delete('/api/notes/item', params={'id': note_id})
    assert deleted.status_code == 200
    assert client.get('/api/notes').json() == []

def test_duplicate_note_text(client):
    first = client.post('/api/notes', json={'text': 'Same note'})
    second = client.post('/api/notes', json={'text': 'Same note'})

    assert first.status_code == 201
    assert second.status_code == 201
    
    assert first.json()['id'] != second.json()['id']
    assert len(client.get('/api/notes').json()) == 2

def test_note_empty_text(client):
    response = client.post('/api/notes', json={'text': '   '})

    assert response.status_code == 422
    assert client.get('/api/notes').json() == []

@pytest.mark.parametrize('method', ['put', 'delete'])
def test_missing_note(client, method):
    kwargs = {'json': {'text': 'Updated text'}} if method == 'put' else {}
    response = getattr(client, method)('/api/notes/item', params={'id': 999}, **kwargs)

    assert response.status_code == 404

@pytest.mark.parametrize('method', ['put', 'delete'])
def test_note_id_value(client, method):
    kwargs = {'json': {'text': 'Updated text'}} if method == 'put' else {}
    response = getattr(client, method)('/api/notes/item', params={'id': 0}, **kwargs)

    assert response.status_code == 422
