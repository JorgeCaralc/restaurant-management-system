"""
Command-line interface (CLI) of the Restaurant Management System.

Entry point of the program: run it with `python main.py`.
This is the ONLY module that talks to the user (print / input): it shows
the menu, reads and validates what the user types, and calls the functions
in restaurant_logic.py and storage.py.
"""

def show_menu():
    """Print the main menu options."""
    print("===== Restaurant Management System =====")
    print("1. Load restaurant")
    print("2. Load new group requests")
    print("3. Take an order")
    print("4. Charge and release a table")
    print("5. Grow the menu")
    print("6. Check status")
    print("7. Exit")


def main():
    """Run the main menu loop until the user chooses to exit."""
    while True:
        show_menu()
        option = input("Choose an option (1-7): ").strip()
        if option == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()