from .models_note import NoteRecord, NoteBook
from .storage_base import read_json, write_json

# Prepare the note record for storage in a json file.
def note_to_dict(note: NoteRecord) -> dict:
    return {
        'id': note.id, 
        'text': note.text,
    }

# Load note records from json.
def load_notes() -> NoteBook:
    data = read_json('notes.json', {'next_id': 1, 'notes': []})
    
    if not isinstance(data, dict) or not isinstance(data.get('notes'), list):
        raise ValueError('Invalid notes file: expected an object with a "notes" list.')
    
    next_id = data.get('next_id')
    
    if type(next_id) is not int or next_id < 1:
        raise ValueError('Invalid notes file: "next_id" must be a positive integer.')
    
    notebook = NoteBook()
    for item in data['notes']:
        if not isinstance(item, dict):
            raise ValueError('Invalid note record: each note must be an object.')
        
        id = item.get('id')
        text = item.get('text')
        
        if type(id) is not int or id < 1:
            raise ValueError('Invalid note record: "id" must be a positive integer.')

        if id in notebook.data:
            raise ValueError(f"Invalid note record {id}: duplicate ID.")
        
        if not isinstance(text, str):
            raise ValueError(f"Invalid note record {id}: 'text' must be a string.")
        
        notebook.data[id] = NoteRecord(id, text)
    
    if notebook.data and next_id <= max(notebook.data):
        raise ValueError('Invalid notes file: "next_id" must be greater than all saved note IDs.')

    notebook.next_id = next_id

    return notebook

# Save note records to json.
def save_notes(notebook):
    items = [note_to_dict(note) for note in notebook.data.values()]
    write_json('notes.json', {
        'next_id': notebook.next_id, 
        'notes': items,
    })
