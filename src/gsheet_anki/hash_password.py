from gsheet_anki.auth import hash_password
import random


def generate_random_password(length=12):
    """
    Generates a random password of the specified length.
    :param length: Length of the password to generate.
    :return: Randomly generated password.
    """
    characters = (
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        '!@#$%^&*()-_=+[]{}|;:,.<>?'
    )
    return ''.join(random.choice(characters) for _ in range(length))


def main():
    """
    Main function to generate a random password and hash it.
    :return: None
    """
    user_input = input("Do you want to generate a random password? [Y/n]: ").strip().lower()
    if user_input == "n":
        password = input("Enter your password: ").strip()
    else:
        password = generate_random_password()
        print(f"Generated password: {password}")
    hashed_password = hash_password(password)
    print(f"Hashed password: {hashed_password}")


if __name__ == "__main__":
    main()
