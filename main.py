"""
Command-line interface (CLI) of the Restaurant Management System.

Entry point of the program: run it with `python main.py`.
This is the ONLY module that talks to the user (print / input): it shows
the menu, reads and validates what the user types, and calls the functions
in restaurant_logic.py and storage.py.
"""
import math


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


def ask_number(prompt):
    """Ask for a number greater than 0 until the user types a valid one."""
    while True:
        try:
            number = float(input(prompt))
            if number > 0 and math.isfinite(number):
                return number
            print("The number must be greater than 0.")
        except ValueError:
            print("That is not a number. Try again, e.g. 12.5")


def choose_table(tables):
    """Show the tables and return the one the user picks, or None to cancel."""
    for table in tables:
        print(f"Table {table['table_num']}: {table['customers']} customers ({table['status']})")
    while True:
        answer = input("Table number (Enter to cancel): ").strip()
        if answer == "":
            return None
        for table in tables:
            if str(table["table_num"]) == answer:
                return table
        print("That table is not in the list.")


def ask_yes_no(prompt):
    """Ask a yes/no question. Return True only if the user types y (Enter means no)."""
    answer = input(prompt + " (y/n): ").strip().lower()
    if answer == "y":
        return True
    else:
        return False


def load_restaurant_option(restaurant, restaurant_path):
    """Load the restaurant from a JSON file (option 1)."""
    print("This option is not implemented yet.")
    return restaurant, restaurant_path


def load_groups_option(restaurant):
    """Load group requests from a file in tables/ and seat them (option 2)."""
    print("This option is not implemented yet.")


def take_order_option(restaurant):
    """Take the order of a seated table (option 3)."""
    print("This option is not implemented yet.")


def charge_table_option(restaurant):
    """Charge an ordered table and release it (option 4)."""
    print("This option is not implemented yet.")


def grow_menu_option(restaurant, restaurant_path):
    """Add a dish or update its price, and save the menu (option 5)."""
    print("This option is not implemented yet.")


def show_status(restaurant):
    """Show all the data the program holds (option 6)."""
    print("This option is not implemented yet.")


def main():
    """Run the main menu loop until the user chooses to exit."""
    restaurant = None   # no restaurant loaded yet
    restaurant_path = "data/restaurant.json"
    while True:
        show_menu()
        option = input("Choose an option (1-7): ").strip()
        if option == "1":
            restaurant, restaurant_path = load_restaurant_option(restaurant, restaurant_path)
        elif option in ("2", "3", "4", "5", "6") and restaurant is None:
            print("Load the restaurant first (option 1).")
        elif option == "2":
            load_groups_option(restaurant)
        elif option == "3":
            take_order_option(restaurant)
        elif option == "4":
            charge_table_option(restaurant)
        elif option == "5":
            grow_menu_option(restaurant, restaurant_path)
        elif option == "6":
            show_status(restaurant)
        elif option == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()