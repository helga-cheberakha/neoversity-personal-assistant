from threading import Lock
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Literal
from pydantic import BaseModel, EmailStr
from .models_contact import Address, Birthday, ContactRecord, Email, Name
from .storage_contact import contact_to_dict, load_contacts, save_contacts
from .storage_note import load_notes, note_to_dict, save_notes


app = FastAPI(title='Personal Assistant')
# Run one backend process. Serialize changes to the json files.
lock = Lock()

# Define the request data for adding a contact record.
class NewContactRecord(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None
    address: str | None = None
    birthday: str | None = None

# Define the request data for updating a contact record.
class ContactRecordChange(BaseModel):
    # A new contact name. None leaves the name unchanged.
    name: str | None = None
    # A phone number to add or use as a replacement.
    new_phone: str | None = None
    # The existing phone number to replace.
    # None means the new phone number should be added instead.
    old_phone: str | None = None
    # None leaves the field unchanged.
    # Empty string clears the field value.
    email: EmailStr | Literal[''] | None = None
    address: str | None = None
    birthday: str | None = None

# Define the request data for adding or updating a note.
class NoteData(BaseModel):
    text: str

@app.exception_handler(OSError)
async def file_error(request: Request, error: OSError):
    return JSONResponse(
        status_code=500,
        content={'detail': 'Cannot read or save data files.'},
    )

@app.exception_handler(ValueError)
async def data_error(request: Request, error: ValueError):
    return JSONResponse(
        status_code=500,
        content={'detail': 'Invalid saved data. Check your json files.'},
    )

# Endpoint to check that the API is ready.
@app.get('/api/health')
def health_check():
    return {'status': 'ok'}

# Endpoint to get contact records.
@app.get('/api/contacts')
def list_contacts(keywords: str = ''):
    book = load_contacts()

    return [contact_to_dict(record) for record in book.search(keywords)]

# Endpoint to get birthdays.
@app.get('/api/contacts/birthdays')
def birthdays(days: int = Query(default=7, ge=0, le=366)):
    book = load_contacts()

    return book.get_upcoming_birthdays(days)

# Endpoint to get contact record by its name.
@app.get('/api/contacts/item')
def get_contact(name: str):
    book = load_contacts()
    record = book.find_record(name)

    if record is None:
        raise HTTPException(status_code=404, detail='Contact not found.')

    return contact_to_dict(record)

# Endpoint to create a contact record or add a phone to an existing contact record.
@app.post('/api/contacts', status_code=201)
def add_contact(body: NewContactRecord):
    # Prevent simultaneous changes to the data file.
    with lock:
        book = load_contacts()
        record = book.find_record(body.name)
        
        try:
            if record is None:
                record = ContactRecord(body.name)
            
            record.add_phone(body.phone)
            
            if body.email is not None:
                record.set_email(body.email)
            
            if body.address is not None:
                record.set_address(body.address)
            
            if body.birthday is not None:
                record.set_birthday(body.birthday)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        book.add_record(record)
        save_contacts(book)
        return contact_to_dict(record)

# Endpoint to update a contact record.
@app.put('/api/contacts/item')
def update_contact(name: str, body: ContactRecordChange):
    # Prevent simultaneous changes to the data file.
    with lock:
        book = load_contacts()
        record = book.find_record(name)

        if record is None:
            raise HTTPException(status_code=404, detail='Contact not found.')

        try:
            new_name = None

            if body.name is not None:
                new_name = Name(body.name)
                existing_record = book.find_record(new_name.value)

                if existing_record is not None and existing_record is not record:
                    raise ValueError('This contact name already exists.')
            
            # We need both the old and new numbers to replace a phone.
            if body.old_phone is not None and body.new_phone is None:
                raise ValueError('A new phone is required.')

            # Add a new phone or replace the existing phone.
            if body.new_phone is not None:
                if body.old_phone is None:
                    record.add_phone(body.new_phone)
                else:
                    record.edit_phone(body.old_phone, body.new_phone)

            # Update optional fields.
            if body.email is not None:
                record.email = Email(body.email) if body.email else None

            if body.address is not None:
                record.address = Address(body.address) if body.address else None

            if body.birthday is not None:
                record.birthday = Birthday(body.birthday) if body.birthday else None

            # We use the contact name as its key and to update the contact name
            # remove the old entry and add a new one under the new name.
            if new_name is not None:
                book.delete_record(record.name.value)
                record.name = new_name
                book.add_record(record)

        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        save_contacts(book)

        return contact_to_dict(record)

# Endpoint to delete a contact record.
@app.delete('/api/contacts/item')
def delete_contact(name: str):
    # Prevent simultaneous changes to the data file.
    with lock:
        book = load_contacts()
        record = book.find_record(name)

        if record is None:
            raise HTTPException(status_code=404, detail='Contact not found.')

        book.delete_record(record.name.value)
        save_contacts(book)
    
    return {'message': 'Contact deleted.'}

# Endpoint to get note records.
@app.get('/api/notes')
def list_notes(keywords: str = ''):
    notes = load_notes()

    return [note_to_dict(note) for note in notes.search(keywords)]

# Endpoint to create a note record.
@app.post('/api/notes', status_code=201)
def add_note(body: NoteData):
    # Prevent simultaneous changes to the data file.
    with lock:
        notebook = load_notes()
        
        try:
            note = notebook.add_record(body.text)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        
        save_notes(notebook)
        return note_to_dict(note)

# Endpoint to update a note record.
@app.put('/api/notes/item')
def edit_note(body: NoteData, id: int = Query(ge=1)):
    # Prevent simultaneous changes to the data file.
    with lock:
        notebook = load_notes()
        
        try:
            note = notebook.find_record(id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        
        try:
            note.set_text(body.text)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        
        save_notes(notebook)
        return note_to_dict(note)

# Endpoint to delete a contact record.
@app.delete('/api/notes/item')
def delete_note(id: int = Query(ge=1)):
    # Prevent simultaneous changes to the data file.
    with lock:
        notebook = load_notes()
        
        try:
            notebook.delete_record(id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        
        save_notes(notebook)
    
    return {'message': 'Note deleted.'}
