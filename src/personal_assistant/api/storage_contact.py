from .models_contact import ContactRecord, ContactBook
from .storage_base import read_json, write_json

# Prepare the contact record for storage in a json file.
def contact_to_dict(record: ContactRecord) -> dict:
    phones = []
    for phone in record.phones:
        phones.append(phone.value)
    
    birthday = None
    if record.birthday is not None:
        birthday = record.birthday.value.strftime('%d.%m.%Y')
    
    email = str(record.email) if record.email is not None else None
    address = str(record.address) if record.address is not None else None
    
    return {
        'name': record.name.value,
        'phones': phones,
        'email': email,
        'address': address,
        'birthday': birthday,
    }

# Load contact records from json.
def load_contacts() -> ContactBook:
    items = read_json('contacts.json', [])
    
    if not isinstance(items, list):
        raise ValueError('Invalid contacts file: expected a JSON array of contacts.')
    
    book = ContactBook()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str):
            raise ValueError('Invalid contact record: each contact must be an object with a non-empty "name" string field.')
        
        record = ContactRecord(item['name'])
        if book.find_record(record.name.value) is not None:
            raise ValueError(f"Invalid contact record: duplicate contact name {record.name.value}.")
        
        phones = item.get('phones', [])
        if not isinstance(phones, list):
            raise ValueError(f"Invalid contact record {record.name.value}: 'phones' must be a list of phone numbers.")
        
        for phone in phones:
            if not isinstance(phone, str):
                raise ValueError(f"Invalid contact record {record.name.value}: 'phone' must be a string.")
            
            record.add_phone(phone)
        
        for field in ('birthday', 'email', 'address'):
            value = item.get(field)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"Invalid contact record {record.name.value}: {field} must be a string.")
        
        if item.get('birthday') is not None:
            record.set_birthday(item['birthday'])
        
        if item.get('email') is not None:
            record.set_email(item['email'])
        
        if item.get('address') is not None:
            record.set_address(item['address'])
        
        book.add_record(record)
    
    return book

# Write contact records to json.
def save_contacts(book: ContactBook):
    items = []
    for record in book.values():
        items.append(contact_to_dict(record))
    
    write_json('contacts.json', items)
