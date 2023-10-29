import pickle
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class PhoneValidationError(Exception):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise PhoneValidationError("Phone number must be a 10-digit number")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError(
                "Invalid date format for birthday. Birthday should be in the format DD.MM.YYYY"
            )
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        try:
            phone_obj = Phone(phone)
            self.phones.append(phone_obj)
        except ValueError as e:
            return str(e)

    def remove_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                self.phones.remove(phone_obj)
                return

    def edit_phone(self, old_phone, new_phone):
        for phone_obj in self.phones:
            if phone_obj.value == old_phone:
                phone_obj.value = new_phone
                return

    def add_birthday(self, birthday):
        try:
            birthday_obj = Birthday(birthday)
            self.birthday = birthday_obj
            return "Birthday added."
        except ValueError as e:
            return str(e)

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj

    def __str__(self):
        phone_str = "; ".join(str(phone) for phone in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phone_str}, birthday: {birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        if name.lower() in self.data:
            del self.data[name.lower()]

    def get_birthdays_per_week(self):
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                birthday_date = birthday_date.replace(year=today.year)
                if today < birthday_date <= next_week:
                    upcoming_birthdays.append(
                        (record.name.value, record.birthday.value)
                    )

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Enter user name."
        except IndexError:
            return "Give me name and phone please."
        except PhoneValidationError:
            return "Phone number must be a 10-digit number"
        except BirthdayError:
            return "Invalid date format for birthday"

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args, contacts):
    if len(args) < 2:
        return "Give me name and phone please."

    name, phone = args
    if name not in contacts:
        record = Record(name.lower())
        record.add_phone(phone)
        contacts.add_record(record)
        return "Contact added."
    else:
        return "Contact already exists. Use 'change' to update."


@input_error
def change_contact(args, contacts):
    if len(args) < 2:
        return "Give me name and phone please."

    name, phone = args
    name = args[0].lower()
    if name in contacts:
        record = contacts[name.lower()]
        if record.phones:
            record.remove_phone(record.phones[0].value)
        message = record.add_phone(phone)
        if message:
            return message
        else:
            return "Contact updated."
    else:
        return "Contact not found."


@input_error
def show_phone(args, contacts):
    if len(args) < 1:
        return "Give me name and phone please."

    name = args[0].lower()
    if name in contacts:
        record = contacts[name.lower()]
        return "; ".join(str(phone) for phone in record.phones)
    else:
        return "Contact not found."


@input_error
def show_all(args, contacts):
    if not contacts:
        return "No contacts found."
    result = "\n".join(
        [
            f"{name.capitalize()}: {'; '.join(str(phone) for phone in record.phones)}"
            for name, record in contacts.items()
        ]
    )
    return result


@input_error
def remove_phone(args, contacts):
    if len(args) < 1:
        return "Give me the name of the contact you want to remove."

    name = args[0].lower()
    if name in contacts:
        del contacts.data[name]
        return "Contact removed."
    else:
        return "Contact not found."


@input_error
def add_birthday(args, contacts):
    if len(args) < 2:
        return "Give me name and date of birth in the format DD.MM.YYYY."

    name, birthday = args
    name = args[0].lower()
    if name in contacts:
        record = contacts[name.lower()]
        result = record.add_birthday(birthday)
        return result
    else:
        return "Contact not found."


@input_error
def show_birthday(args, contacts):
    if len(args) < 1:
        return "Give me name and date of birth in the format DD.MM.YYYY."

    name = args[0].lower()
    if name in contacts:
        birthday = contacts[name.lower()].birthday
        if birthday:
            return birthday.value
        else:
            return "Birthday not set."
    else:
        return "Contact not found."


class BirthdayError(Exception):
    def __init__(self, message="Invalid date format for birthday"):
        self.message = message
        super().__init__(self.message)


def save_address_book(contacts, filename):
    with open(filename, "wb") as file:
        pickle.dump(contacts, file)


def load_address_book(filename):
    try:
        with open(filename, "rb") as file:
            contacts = pickle.load(file)
            return contacts
    except FileNotFoundError:
        return AddressBook()


def main():
    try:
        contacts = load_address_book("address_book.pickle")
    except:
        contacts = AddressBook()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_address_book(contacts, "address_book.pickle")
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            result = add_contact(args, contacts)
            print(result)
        elif command == "change":
            result = change_contact(args, contacts)
            print(result)
        elif command == "phone":
            result = show_phone(args, contacts)
            print(result)
        elif command == "all":
            result = show_all(args, contacts)
            print(result)
        elif command == "remove":
            result = remove_phone(args, contacts)
            print(result)
        elif command == "add-birthday":
            result = add_birthday(args, contacts)
            print(result)
        elif command == "show-birthday":
            result = show_birthday(args, contacts)
            print(result)
        elif command == "birthdays":
            upcoming_birthdays = contacts.get_birthdays_per_week()
            if upcoming_birthdays:
                print("Upcoming birthdays in the next week:")
                for name, birthday in upcoming_birthdays:
                    print(f"{name.capitalize()} - {birthday}")
            else:
                print("No upcoming birthdays in the next week.")
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
