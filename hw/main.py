from collections import UserDict
import datetime
import pickle


class BirthdayValueError(ValueError):
    pass

class PhoneValueError(ValueError):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
            return
        raise PhoneValueError("The phone number must contain 10 digits.")

class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise BirthdayValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if not phone_obj:
            raise ValueError("This phone number does not exist")
        self.phones.remove(phone_obj)
    
    def edit_phone(self, old_phone, new_phone):
        Phone(new_phone)
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        Phone(phone)
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, obj):
        self.data[obj.name.value] = obj
    
    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name)

    def string_to_date(self, date_string):
        return datetime.datetime.strptime(date_string, "%d.%m.%Y").date()

    def date_to_string(self, date):
        return date.strftime("%d.%m.%Y")

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + datetime.timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday
    
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.date.today()

        for name, obj in self.data.items():
            if obj.birthday is None:
                continue
            birthday_this_year = self.string_to_date(obj.birthday.value).replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year+1)

            if 0 <= (birthday_this_year - today).days <= 7:
                birthday_this_year = self.adjust_for_weekend(birthday_this_year)

                congratulation_date_str = self.date_to_string(birthday_this_year)
                upcoming_birthdays.append({"name": name, "congratulation_date": congratulation_date_str})
        return upcoming_birthdays

    def __str__(self):
        text = "AddressBook:\n"
        for obj in self.data:
            dr = self.find(obj).birthday 
            birthday = dr if dr is not None else "No information"

            string = f"Contact name: {obj}, \
phones: {'; '.join(phone.value for phone in self.find(obj).phones)}, \
birthday: {birthday}\n"
            text += string
        return text

#**********************************************************Func
def input_error(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (PhoneValueError, BirthdayValueError) as ex:
                return ex
            except ValueError:
                return "Please specify the required number of arguments."
            except AttributeError:
                return "Contact not found."
        return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact changed."

@input_error
def print_phone(args, book):
    name, *_ = args
    record = book.find(name)
    return record

@input_error
def all_contact(book):
    return book

@input_error
def add_birthday(args, book):
    name, date, *_ = args
    record = book.find(name)
    if date:
        record.add_birthday(date)
    return "Birthday added"

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record.birthday is None:
        return "No information"
    return record.birthday

@input_error
def birthdays(book):
    birthdays = "Birthdays in the next 7 days:\n"
    for item in book.get_upcoming_birthdays():
        birthdays += f"{item["name"]}, Birthday: {item["congratulation_date"]}\n"
    return birthdays

def save_book(book, FILENAME):
    with open(FILENAME, "wb") as file:
        pickle.dump(book, file)

def load_book(FILENAME):
    try:
        with open(FILENAME, "rb") as file:
            data = pickle.load(file)
        return data 
    except FileNotFoundError:
        return AddressBook()

#*******************************************************Main
def main():
    FILENAME = "addressbook.pkl"
    book = load_book(FILENAME)
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_book(book, FILENAME)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_phone(args, book))
        elif command == "phone":
            print(print_phone(args, book))
        elif command == "all":
            print(all_contact(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
