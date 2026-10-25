from functools import wraps
from .api import request

CONTACT_SINGLE_FIELDS = ('name', 'email', 'address', 'birthday')

# Handle input errors raised by command handlers.
def input_error(func):
    @wraps(func)
    def inner(args):
        try:
            return func(args)
        except ValueError as error:
            return f"Error: {error} Type 'help' for examples."

    return inner

# Prepare contact records to display.
def format_contacts(contacts) -> str:
    if not contacts:
        return 'No contacts found.'

    lines = []
    for contact in contacts:
        # Get all phone numbers and display with name of the contact.
        phones = ', '.join(contact['phones']) or '-'
        line = f"{contact['name']} | Phones: {phones}"
        
        # Display another contact fields.
        for field in ('email', 'address', 'birthday'):
            line += f" | {field}: {contact[field] or '-'}"

        lines.append(line)

    return "\n".join(lines)

# Prepare birthdays to display.
def format_contact_birthdays(contacts) -> str:
    if not contacts:
        return 'No upcoming birthdays found.' 

    lines = []
    for contact in contacts:
        lines.append(f"{contact['name']} | Birthday: {contact['birthday']} | Congratulate on: {contact['congratulation_date']}")

    return "\n".join(lines)

# Prepare note records to display.
def format_notes(notes) -> str:
    if not notes:
        return 'No notes found.'

    lines = []
    for note in notes:
        lines.append(f"{note['id']}: {note['text']}")

    return "\n".join(lines)

# Validate a number.
def validate_number(number) -> bool:
    if number.isascii() and number.isdigit():
        return True

    return False

# Validate a note ID.
def validate_note_id(note_id) -> bool:
    if validate_number(note_id) and int(note_id) > 0:
        return True

    return False


# Add/edit/delete/display contact record(s).
@input_error
def add_contact(args: list) -> str:
    name, phone = args
    request('POST', '/contacts', data={'name': name, 'phone': phone})

    return 'Contact saved.'

@input_error
def edit_contact(args: list) -> str:
    name, field, value = args
    if field not in CONTACT_SINGLE_FIELDS:
        raise ValueError(f"Choose allowed contact fields: '{', '.join(CONTACT_SINGLE_FIELDS)}'.")

    request('PUT', '/contacts/item', params={'name': name}, data={field: value})

    return 'Contact updated.'

@input_error
def display_contact(args: list) -> str:
    name, = args
    contact = request('GET', '/contacts/item', params={'name': name})

    return format_contacts([contact])

@input_error
def delete_contact(args: list) -> str:
    name, = args
    responce = request('DELETE', '/contacts/item', params={'name': name})

    return responce['message']

@input_error
def display_all(args: list) -> str:
    if args:
        raise ValueError("Correct command format: 'all'.")
    
    contacts = request('GET', '/contacts')

    return format_contacts(contacts)

@input_error
def search_contacts(args: list) -> str:
    keyword, = args
    contacts = request('GET', '/contacts', params={'keywords': keyword})

    return format_contacts(contacts)

@input_error
def change_phone(args: list) -> str:
    name, old_phone, new_phone = args
    request('PUT', '/contacts/item', params={'name': name}, data={'old_phone': old_phone, 'new_phone': new_phone})        

    return 'Phone updated.'

@input_error
def display_phone(args: list) -> str:
    name, = args
    contact = request('GET', '/contacts/item', params={'name': name})        

    return ', '.join(contact['phones']) or 'No phone numbers.'

# Add/edit/display date of birth of the contact record.
@input_error
def add_birthday(args: list) -> str:
    name, birthday = args
    request('PUT', '/contacts/item', params={'name': name}, data={'birthday': birthday})        

    return 'Birthday saved.'

@input_error
def display_birthday(args: list) -> str:
    name, = args
    contact = request('GET', '/contacts/item', params={'name': name})        

    return contact['birthday'] or 'No birthday set.'

# Display upcoming birthdays.
@input_error
def birthdays(args: list) -> str:
    if len(args) > 1:
        raise ValueError("Correct command format: 'birthdays' or 'birthdays <days>', where <days> specifies how many days ahead to check for upcoming birthdays.")  

    # Validate days number before sending the request.
    if args and (not validate_number(args[0]) or not 0 <= int(args[0]) <= 366):
        raise ValueError('Days must be a number from 0 to 366.')

    days = int(args[0]) if args else 7
    contacts = request('GET', '/contacts/birthdays', params={'days': days})   

    return format_contact_birthdays(contacts)

# Add/edit/delete/display note records.
@input_error
def add_note(args: list) -> str:
    text, = args
    note = request('POST', '/notes', data={'text': text})

    return f"Note added. ID: {note['id']}"

@input_error
def edit_note(args: list) -> str:
    note_id, text = args
    # Validate note IDs, which should be a positive numbers.
    if not validate_note_id(note_id):
        raise ValueError('Note ID must be a positive number.')

    request('PUT', '/notes/item', params={'id': int(note_id)}, data={'text': text})

    return 'Note updated.'

@input_error
def delete_note(args: list) -> str:
    note_id, = args
    # Apply the same ID validation before deleting a note.
    if not validate_note_id(note_id):
        raise ValueError('Note ID must be a positive number.')

    responce = request('DELETE', '/notes/item', params={'id': int(note_id)})

    return responce['message']

@input_error
def display_notes(args: list) -> str:
    if args:
        raise ValueError("Correct command format: 'notes'.")

    notes = request('GET', '/notes')

    return format_notes(notes)

@input_error
def search_notes(args: list) -> str:
    keyword, = args
    notes = request('GET', '/notes', params={'keywords': keyword})

    return format_notes(notes)
