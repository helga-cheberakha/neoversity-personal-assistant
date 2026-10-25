from collections import UserDict
from datetime import date, datetime, timedelta
from pydantic import EmailStr, TypeAdapter, ValidationError

# Create one validator to check email addresses with Pydantic.
email_adapter = TypeAdapter(EmailStr)

# Implements "Field" to store each field data.
class ContactField:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Validate and store a contact name.
class Name(ContactField):
    def __init__(self, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Contact name is required and cannot be empty.')
         
        super().__init__(value)

# Validate and store a contact phone number.
class Phone(ContactField):
    def __init__(self, value: str):
        value = value.strip()
        if not value.isdecimal() or len(value) != 10:
            raise ValueError('Invalid phone number format. It must contain 10 digits.')

        super().__init__(value)

# Validate and store a contact email address.
class Email(ContactField):
    def __init__(self, value: str):
        value = value.strip()
        try:
            # Check the address and use the normalized value.
            value = email_adapter.validate_python(value)
        except ValidationError as error:
            raise ValueError('Invalid email address.') from error

        super().__init__(value)

# Validate and store a contact postal address.
class Address(ContactField):
    def __init__(self, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Address cannot be empty.')
        
        super().__init__(value)

# Validate and store a contact birthday.
class Birthday(ContactField):
    def __init__(self, value: str):
        try:
            birthday = datetime.strptime(value, '%d.%m.%Y').date()
            super().__init__(birthday)
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY')

# Handle contact record.
class ContactRecord:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = None
        self.address = None
        self.birthday = None

    def __str__(self):
        contact_str = f"Name: {self.name.value} | Phones: {', '.join(p.value for p in self.phones)}"

        for field in ('email', 'address', 'birthday'):
            value = getattr(self, field, None)
            if value is not None:
                contact_str += f" | {field.capitalize()}: {value}"

        return contact_str

    def find_phone(self, phone: str) -> Phone | None:
        phone_obj = Phone(phone)

        for item in self.phones:
            if item.value == phone_obj.value:
                return item
    
        return None

    # Adds a new phone number to the record 
    # if it does not exist yet.
    def add_phone(self, phone: str) -> None:
        if not self.find_phone(phone):
            self.phones.append(Phone(phone))

    # Removes the existing phone number.
    def remove_phone(self, phone: str) -> None:
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove is not None:
            self.phones.remove(phone_to_remove)

    # Edits an existing phone number
    # if the new phone number does not already exist in the record.
    def edit_phone(self, original_phone: str, new_phone: str) -> None:
        phone_to_update = self.find_phone(original_phone)
        if phone_to_update is None:
            raise ValueError('The old phone number was not found.')

        if self.find_phone(new_phone):
            raise ValueError('This phone number already exists.')

        phone_to_update.value = Phone(new_phone).value

    # Set the email address.
    def set_email(self, email: str) -> None:
        self.email = Email(email)

    # Set the postal address.
    def set_address(self, address: str) -> None:
        self.address = Address(address)

    # Set the birthday.
    def set_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

# Handle contact book.
class ContactBook(UserDict):
    # Find a contact record using its name (case-insensitive) 
    # as identificator.
    def find_record(self, search_name: str) -> ContactRecord | None:
        search_name = search_name.strip()
        
        for name, record in self.items():
            if name.casefold() == search_name.casefold():
                return record
    
        return None

    # Adds a new contact record if the record 
    # with the same name (case-insensitive) does not exist yet.
    def add_record(self, record: ContactRecord) -> None:
        if not self.find_record(record.name.value):
            self.data[record.name.value] = record

    # Delete a contact record by its name (case-insensitive).
    def delete_record(self, removed_name: str) -> None:
        record = self.find_record(removed_name)
        if record is not None:
            del self.data[record.name.value]

    # Search notes by some keywords.
    def search(self, keywords: str) -> list[ContactRecord]:
        keywords = keywords.strip().casefold()
        found = []

        for record in self.data.values():
            values = [
                record.name.value,
                record.email.value if record.email else '',
                record.address.value if record.address else '',
            ]
            values.extend(phone.value for phone in record.phones)

            if any(keywords in value.casefold() for value in values):
                found.append(record)

        return found

    # Gets list of upcoming birthdays.
    def get_upcoming_birthdays(self, days=7, today=None) -> list:
        # Get the current date as a date without time.
        if today is None:
            today = date.today()
            
        # Build list of users upcoming birthdays.
        upcoming_birthdays = []

        for name, record in self.items():
            # Check whether the record has non-empty date of birthday.
            if record.birthday is None:
                continue

            # Get a date object without time.
            birthday = record.birthday.value

            # Get the user birthday to the current year.
            birthday_current_year = self.get_birthday_for_year(birthday, today.year)

            # Get the contact birthday to the next year if it has already passed
            # for the current year.
            if birthday_current_year < today:
                birthday_current_year = self.get_birthday_for_year(birthday, today.year + 1)

            # Get the difference in days.
            days_until_birthday = (birthday_current_year - today).days

            # Check whether the birthday is within the selected interval.
            if 0 <= days_until_birthday <= days:
                congratulation_date = birthday_current_year

                # Check whether the user birthday is on weekend
                # and move it to the Monday
                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                # Add the user birthday to the result list.
                upcoming_birthdays.append({
                    'name': name,
                    'birthday': birthday.strftime('%d.%m.%Y'),
                    'congratulation_date': congratulation_date.strftime('%d.%m.%Y')
                })

        return upcoming_birthdays

    @staticmethod
    def get_birthday_for_year(birthday: date, year: int) -> date:
        try:
            return birthday.replace(year=year)
        except ValueError:
            # Use March 1 for leap-day birthdays in non-leap years.
            return birthday.replace(year=year, month=3, day=1)
