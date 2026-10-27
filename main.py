"""
Command-line interface (CLI) of the Restaurant Management System.

Entry point of the program: run it with `python main.py`.
This is the ONLY module that talks to the user (print / input): it shows
the menu, reads and validates what the user types, and calls the functions
in restaurant_logic.py and storage.py.
"""
import math
import restaurant_logic
import storage


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
    seated = restaurant_logic.get_tables(restaurant, "seated")
    if not seated:
        print("There are no seated tables waiting to order.")
        return
    if not restaurant["menu"]:
        print("The menu is empty. Add dishes first (option 5).")
        return
    table = choose_table(seated)
    if table is None:
        return
    dishes = []
    for customer in range(1, table["customers"] + 1):
        print(f"Customer {customer} (press Enter when finished):")
        customer_dishes = 0
        while True:
            name = input("  Dish: ").strip()
            if name == "":
                if customer_dishes > 0:
                    break
                print("  Each customer must order at least one dish.")
            else:
                dish = restaurant_logic.find_dish(restaurant["menu"], name)
                if dish is None:
                    print(f'  "{name}" is not on the menu.')
                else:
                    dishes.append(dish)
                    customer_dishes += 1
    restaurant_logic.register_order(table, dishes, restaurant["menu"])
    print(f"Order saved for table {table['table_num']}: {len(dishes)} dishes.")


def charge_table_option(restaurant):
    """Charge an ordered table and release it (option 4)."""
    ordered = restaurant_logic.get_tables(restaurant, "ordered")
    if not ordered:
        print("There are no tables waiting to pay.")
        return
    table = choose_table(ordered)
    if table is None:
        return
    for order in table["orders"]:
        print(f"  - {order['dish']}: {order['price']:.2f}")
    bill = restaurant_logic.charge_and_release(restaurant, table["table_num"])
    print(f"Table {table['table_num']} paid {bill:.2f}. The table is free now.")


def grow_menu_option(restaurant, restaurant_path):
    """Add a dish or update its price, and save the menu (option 5)."""
    name = input("Dish name: ").strip()
    if name == "":
        print("The dish name cannot be empty.")
        return
    existing = restaurant_logic.find_dish(restaurant["menu"], name)
    if existing is not None:
        print(f"{existing} is already on the menu. Its price will be updated.")
    price = ask_number("Price: ")
    restaurant_logic.add_or_update_dish(restaurant["menu"], name, price)
    try:
        storage.save_restaurant_data(restaurant_path, restaurant)
        print("Menu saved.")
    except (OSError, ValueError) as error:
        print(f"The menu could not be saved: {error}")
        print("The change is kept for tonight and will be saved again on exit.")


def show_status(restaurant):
    """Show all the data the program holds (option 6)."""
    print(f"===== {restaurant['name']} =====")
    print(f"Capacity: {restaurant['capacity']} people | Max tables: {restaurant['max_tables']}")
    print(f"Occupancy: {restaurant['occupancy']} people ({restaurant['capacity'] - restaurant['occupancy']} free seats)")
    print(f"Tables in use: {len(restaurant['tables'])} of {restaurant['max_tables']}")
    if not restaurant["tables"]:
        print("  No active tables.")
    else:
        for table in restaurant["tables"]:
            print(f"  Table {table['table_num']}: {table['customers']} customers, {table['status']}")
            for order in table["orders"]:
                print(f"      - {order['dish']}: {order['price']:.2f}")
    print(f"Waiting list: {restaurant['waiting_list']}")
    print("Menu:")
    for dish, price in restaurant["menu"].items():
        print(f"  - {dish}: {price:.2f}")
    print(f"Earnings tonight: {restaurant['earnings']:.2f}")


def exit_option(restaurant, restaurant_path):
    """Save the menu before closing (option 7). Return True to close, False to stay."""
    if restaurant is None:
        return True
    if restaurant["tables"] or restaurant["waiting_list"]:
        if not ask_yes_no("There are tables or groups still in the restaurant. Exit anyway?"):
            return False
    try:
        storage.save_restaurant_data(restaurant_path, restaurant)
        print("Menu saved.")
    except (OSError, ValueError) as error:
        print(f"The menu could not be saved: {error}")
    return True


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
            if exit_option(restaurant, restaurant_path):
                print("Goodbye!")
                break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()