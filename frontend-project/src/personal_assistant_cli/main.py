import shlex
from . import commands

HELP = '''Commands:
  hello
  add "First Last" 0671234567
  edit "First Last" name "New Name"
  edit "First Last" email firstname.lastname@example.com
  edit "First Last" address "London, Main Street 10"
  edit "First Last" birthday 25.10.1990
  show "First Last"
  delete "First Last"
  all
  search "London"
  change-phone "First Last" 0671234567 0501234567
  phone "First Last"
  add-birthday "First Last" 25.10.1990
  show-birthday "First Last"
  birthdays [days]
  add-note "Buy a birthday gift"
  edit-note 1 "Buy a book"
  delete-note 1
  notes
  search-notes "gift"
  help
  exit (or close)
Use quotes for arguments containing spaces.
Use edit "First Last" email "" to clear an optional field.
'''

# Parse the user input and split it into command
# and arguments.
def parse_input(user_input: str) -> tuple:
    # Split user input into command and arguments.
    user_input_parts = shlex.split(user_input)

    if not user_input_parts:
        return '', []

    cmd, *args = user_input_parts
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    print("Welcome to the assistant bot! Type 'help' for commands.")

    while True:
        try:
            user_input = input('Enter a command: ')
            command, *args = parse_input(user_input)
        except ValueError:
            print('Check that all quotation marks are closed.')
            continue
        except (OSError, KeyboardInterrupt):
            print('\nGood bye!')
            break

        if not command:
            print('Please enter a command.')
            continue

        if command in ('exit', 'close', 'hello', 'help') and args:
            print('This command takes no arguments.')
        elif command in ('exit', 'close'):
            print('Good bye!')
            break
        elif command == 'hello':
            print('How can I help you?')
        elif command == 'help':
            print(HELP)
        elif command == 'add':
            print(commands.add_contact(args))
        elif command == 'edit':
            print(commands.edit_contact(args))
        elif command == 'show':
            print(commands.display_contact(args))
        elif command == 'delete':
            print(commands.delete_contact(args))
        elif command == 'all':
            print(commands.display_all(args))
        elif command == 'search':
            print(commands.search_contacts(args))
        elif command == 'change-phone':
            print(commands.change_phone(args))
        elif command == 'phone':
            print(commands.display_phone(args))
        elif command == 'add-birthday':
            print(commands.add_birthday(args))
        elif command == 'show-birthday':
            print(commands.display_birthday(args))
        elif command == 'birthdays':
            print(commands.birthdays(args))
        elif command == 'add-note':
            print(commands.add_note(args))
        elif command == 'edit-note':
            print(commands.edit_note(args))
        elif command == 'delete-note':
            print(commands.delete_note(args))
        elif command == 'notes':
            print(commands.display_notes(args))
        elif command == 'search-notes':
            print(commands.search_notes(args))
        else:
            print("Invalid command. Type 'help' for commands.")


if __name__ == '__main__':
    main()
