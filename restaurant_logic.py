"""
Core logic of the restaurant: seating groups, orders, bills and the menu.

These functions never use print() or input(): they receive everything
they need as arguments and return results, so the CLI decides what to show.
"""


def create_restaurant(data):
    """
    Create the restaurant for a new evening from the data loaded from the JSON file.
    Copies name, capacity, max_tables and menu from data, and adds the
    evening's values, all empty: no tables, no people, no earnings and
    nobody waiting.
    """
    restaurant = {
        "name": data["name"],
        "capacity": data["capacity"],
        "max_tables": data["max_tables"],
        "menu": data["menu"],
        "tables": [],
        "occupancy": 0,
        "earnings": 0,
        "waiting_list": [],
    }
    return restaurant
def seat_group(restaurant, customers):
    """Seat a group of customers at a free table, if they fit.

    A group fits if there are enough free seats (capacity) and a free table
    (max_tables). The table gets the lowest number between 1 and max_tables
    that no active table is using, like a real dining room.

    Returns the table number, or None if the group does not fit.
    """
    if restaurant["occupancy"] + customers > restaurant["capacity"]:
        return None
    if len(restaurant["tables"]) >= restaurant["max_tables"]:
        return None

    used_numbers = []
    for table in restaurant["tables"]:
        used_numbers.append(table["table_num"])

    table_num = 1
    while table_num in used_numbers:
        table_num += 1

    restaurant["tables"].append({
        "table_num": table_num,
        "customers": customers,
        "status": "seated",
        "orders": [],
    })
    restaurant["occupancy"] += customers
    return table_num


def add_to_waiting_list(restaurant, groups):
    """Add the new groups to the end of the waiting list, in arrival order.

    A group bigger than the capacity would never fit, so it is not added.
    Returns the list of rejected groups (it may be empty).
    """
    rejected = []
    for customers in groups:
        if customers > restaurant["capacity"]:
            rejected.append(customers)
        else:
            restaurant["waiting_list"].append(customers)
    return rejected


def seat_waiting_groups(restaurant):
    """Seat every waiting group that fits, in arrival order, using seat_group.

    The groups that still do not fit stay in the waiting list, in the same order.
    Returns a list of (customers, table_num) for the groups seated now.
    """
    seated = []
    still_waiting = []
    for customers in restaurant["waiting_list"]:
        table_num = seat_group(restaurant, customers)
        if table_num is None:
            still_waiting.append(customers)
        else:
            seated.append((customers, table_num))
    restaurant["waiting_list"] = still_waiting
    return seated


def get_tables(restaurant, status):
    """Return the active tables with the given status ("seated" or "ordered").

    The list holds the same table dicts that are in the restaurant, not
    copies, so a change made to one of them is also seen in the restaurant.
    """
    tables = []
    for table in restaurant["tables"]:
        if table["status"] == status:
            tables.append(table)
    return tables

def _clean_name(name):
    """Return the name without extra spaces: none at the start or the end,
    and only one between words ("  Cocido   madrileño " -> "Cocido madrileño")."""
    return " ".join(name.split())


def find_dish(menu, name):
    """Find a dish in the menu without caring about capitals or extra spaces.

    Returns the dish name exactly as it is written in the menu
    ("cocido madrileño" -> "Cocido madrileño"), or None if it is not on
    the menu. An empty name is never found.
    """
    wanted = _clean_name(name).lower()
    if wanted == "":
        return None
    for dish in menu:
        if _clean_name(dish).lower() == wanted:
            return dish
    return None

def register_order(table, dishes, menu):
    """Save the dishes ordered by a table and mark it as "ordered".

    dishes holds exact menu names (main.py checks each one with find_dish).
    Each dish is saved with its price at this moment, so if the price changes
    later in the menu, the table still pays what the dish cost when ordered.
    """
    orders = []
    for dish in dishes:
        orders.append({"dish": dish, "price": menu[dish]})
    table["orders"] = orders
    table["status"] = "ordered"

def calculate_bill(table):
    """Return the total to pay for a table, rounded to 2 decimals.

    Adds up the prices saved in its orders (the prices when ordered,
    not the current menu prices). It does not change the table.
    """
    total = 0
    for order in table["orders"]:
        total += order["price"]
    return round(total, 2)


def charge_and_release(restaurant, table_num):
    """Charge a table and free it, so another group can use it.

    Adds the bill to the evening's earnings, takes its customers out of
    the occupancy and removes the table from the restaurant.

    Returns the bill, or None if there is no active table with that number
    or it has not ordered yet (in that case nothing changes).
    """
    table = None
    for active_table in restaurant["tables"]:
        if active_table["table_num"] == table_num:
            table = active_table
    if table is None:
        return None
    if table["status"] != "ordered":
        return None

    bill = calculate_bill(table)
    restaurant["earnings"] = round(restaurant["earnings"] + bill, 2)
    restaurant["occupancy"] -= table["customers"]
    restaurant["tables"].remove(table)
    return bill


def add_or_update_dish(menu, name, price):
    """Add a new dish to the menu, or change the price of a dish it already has.

    If the dish is already on the menu, even written with other capitals or
    extra spaces, its price is updated and its name stays as in the menu.
    If it is new, it is added without extra spaces.
    The name must not be empty and the price must be > 0 (main.py checks both).

    Returns True if the dish already existed (updated), False if it is new.
    """
    existing = find_dish(menu, name)
    if existing is not None:
        menu[existing] = price
        return True
    menu[_clean_name(name)] = price
    return False


def _run_tests():
    """Check the functions of this module. Only runs with: python restaurant_logic.py"""
    data = {
        "name": "Casa Pepe",
        "capacity": 50,
        "max_tables": 5,
        "menu": {"Callos a la madrileña": 12, "Bocata de calamares": 5, "Cocido madrileño": 20},
    }

    # create_restaurant
    restaurant = create_restaurant(data)
    assert restaurant["name"] == "Casa Pepe"
    assert restaurant["capacity"] == 50
    assert restaurant["max_tables"] == 5
    assert restaurant["menu"] == data["menu"]
    assert restaurant["tables"] == []
    assert restaurant["occupancy"] == 0
    assert restaurant["earnings"] == 0
    assert restaurant["waiting_list"] == []
    other = create_restaurant(data)
    assert other["tables"] is not restaurant["tables"]
    # seat_group: tables get numbers 1, 2, 3...
    restaurant = create_restaurant(data)
    assert seat_group(restaurant, 4) == 1
    assert seat_group(restaurant, 2) == 2
    assert restaurant["occupancy"] == 6
    assert restaurant["tables"][0] == {"table_num": 1, "customers": 4, "status": "seated", "orders": []}

    # seat_group: a group bigger than the free seats does not fit (6 + 45 > 50)
    assert seat_group(restaurant, 45) is None
    assert restaurant["occupancy"] == 6
    assert len(restaurant["tables"]) == 2

    # seat_group: fill the 5 tables; a 6th group does not fit even with free seats
    assert seat_group(restaurant, 1) == 3
    assert seat_group(restaurant, 1) == 4
    assert seat_group(restaurant, 1) == 5
    assert seat_group(restaurant, 1) is None

    # seat_group: when table 2 is freed, the next group gets table 2, not 6
    restaurant["tables"].pop(1)
    restaurant["occupancy"] -= 2
    assert seat_group(restaurant, 3) == 2

    # seat_group: a group of exactly the capacity fits (<=, not <)
    restaurant = create_restaurant(data)
    assert seat_group(restaurant, 50) == 1

    # get_tables: filters by status and keeps the restaurant's order
    restaurant = create_restaurant(data)
    seat_group(restaurant, 2)
    seat_group(restaurant, 3)
    seat_group(restaurant, 4)
    restaurant["tables"][1]["status"] = "ordered"
    seated = get_tables(restaurant, "seated")
    ordered = get_tables(restaurant, "ordered")
    assert len(seated) == 2
    assert seated[0]["table_num"] == 1
    assert seated[1]["table_num"] == 3
    assert len(ordered) == 1
    assert ordered[0]["table_num"] == 2

    # get_tables: returns the same table dicts, not copies
    assert ordered[0] is restaurant["tables"][1]

    # get_tables: an empty restaurant has no tables in any state
    assert get_tables(create_restaurant(data), "seated") == []

    # find_dish: ignores capitals and extra spaces, returns the exact menu name
    menu = data["menu"]
    assert find_dish(menu, "Cocido madrileño") == "Cocido madrileño"
    assert find_dish(menu, "COCIDO madrileño") == "Cocido madrileño"
    assert find_dish(menu, "  cocido   MADRILEÑO  ") == "Cocido madrileño"

    # find_dish: a dish that is not on the menu, or an empty name, gives None
    assert find_dish(menu, "Paella") is None
    assert find_dish(menu, "Cocido") is None
    assert find_dish(menu, "") is None
    assert find_dish(menu, "   ") is None
    assert find_dish({}, "Cocido madrileño") is None

    # register_order: saves each dish with its current price and marks the table as ordered
    restaurant = create_restaurant(data)
    seat_group(restaurant, 2)
    table = restaurant["tables"][0]
    register_order(table, ["Cocido madrileño", "Bocata de calamares", "Cocido madrileño"], restaurant["menu"])
    assert table["status"] == "ordered"
    assert table["orders"] == [
        {"dish": "Cocido madrileño", "price": 20},
        {"dish": "Bocata de calamares", "price": 5},
        {"dish": "Cocido madrileño", "price": 20},
    ]

    # register_order: the restaurant sees the change (same table dict, not a copy)
    assert get_tables(restaurant, "ordered") == [table]
    assert get_tables(restaurant, "seated") == []

    # register_order: if the price changes later in the menu, the saved price stays the same
    menu = dict(data["menu"])
    table = {"table_num": 1, "customers": 1, "status": "seated", "orders": []}
    register_order(table, ["Cocido madrileño"], menu)
    menu["Cocido madrileño"] = 25
    assert table["orders"][0]["price"] == 20

     # calculate_bill: adds the saved prices (20 + 5 + 20 = 45) and does not change the table
    restaurant = create_restaurant(data)
    seat_group(restaurant, 2)
    table = restaurant["tables"][0]
    register_order(table, ["Cocido madrileño", "Bocata de calamares", "Cocido madrileño"], restaurant["menu"])
    assert calculate_bill(table) == 45
    assert "bill" not in table
    assert table["status"] == "ordered"

    # calculate_bill: rounds to 2 decimals (in Python, 0.1 + 0.2 gives 0.30000000000000004)
    table = {"table_num": 1, "customers": 2, "status": "ordered",
             "orders": [{"dish": "Caña", "price": 0.1}, {"dish": "Agua", "price": 0.2}]}
    assert calculate_bill(table) == 0.3

    # calculate_bill: a table with no orders costs 0
    table = {"table_num": 1, "customers": 1, "status": "seated", "orders": []}
    assert calculate_bill(table) == 0

    # charge_and_release: charges an ordered table, frees it and updates the evening's numbers
    restaurant = create_restaurant(data)
    seat_group(restaurant, 4)
    seat_group(restaurant, 2)
    register_order(restaurant["tables"][1], ["Cocido madrileño", "Bocata de calamares"], restaurant["menu"])
    assert charge_and_release(restaurant, 2) == 25
    assert restaurant["earnings"] == 25
    assert restaurant["occupancy"] == 4
    assert len(restaurant["tables"]) == 1
    assert restaurant["tables"][0]["table_num"] == 1

    # charge_and_release: a table that has not ordered, or does not exist, gives None and nothing changes
    assert charge_and_release(restaurant, 1) is None
    assert charge_and_release(restaurant, 2) is None
    assert charge_and_release(restaurant, 9) is None
    assert restaurant["earnings"] == 25
    assert restaurant["occupancy"] == 4
    assert len(restaurant["tables"]) == 1

    # charge_and_release: earnings add up during the evening and the freed table number is used again
    assert seat_group(restaurant, 3) == 2
    register_order(restaurant["tables"][1], ["Callos a la madrileña"], restaurant["menu"])
    assert charge_and_release(restaurant, 2) == 12
    assert restaurant["earnings"] == 37

    # add_or_update_dish: a new dish is added without extra spaces and gives False
    menu = dict(data["menu"])
    assert add_or_update_dish(menu, "  Tortilla   de patatas ", 8) is False
    assert menu["Tortilla de patatas"] == 8
    assert len(menu) == 4

    # add_or_update_dish: an existing dish (other capitals) keeps its menu name, gets the new price, gives True
    assert add_or_update_dish(menu, "COCIDO madrileño", 25) is True
    assert menu["Cocido madrileño"] == 25
    assert "COCIDO madrileño" not in menu
    assert len(menu) == 4

    # add_to_waiting_list: groups join the end of the queue; a group bigger than the capacity is rejected
    restaurant = create_restaurant(data)
    assert add_to_waiting_list(restaurant, [4, 60, 2]) == [60]
    assert restaurant["waiting_list"] == [4, 2]
    assert add_to_waiting_list(restaurant, [3]) == []
    assert restaurant["waiting_list"] == [4, 2, 3]

    # seat_waiting_groups: seats every group that fits, in arrival order
    assert seat_waiting_groups(restaurant) == [(4, 1), (2, 2), (3, 3)]
    assert restaurant["waiting_list"] == []
    assert restaurant["occupancy"] == 9

    # seat_waiting_groups: only 5 tables, so the last 2 groups keep waiting in the same order
    restaurant = create_restaurant(data)
    add_to_waiting_list(restaurant, [4, 2, 6, 3, 5, 2, 8])
    assert len(seat_waiting_groups(restaurant)) == 5
    assert restaurant["waiting_list"] == [2, 8]

    # seat_waiting_groups: a group that does not fit does not block the ones behind it
    restaurant = create_restaurant(data)
    seat_group(restaurant, 45)
    add_to_waiting_list(restaurant, [10, 3])
    assert seat_waiting_groups(restaurant) == [(3, 2)]
    assert restaurant["waiting_list"] == [10]

    # seat_waiting_groups: when a table is charged and freed, the waiting group gets it
    register_order(restaurant["tables"][0], ["Cocido madrileño"], restaurant["menu"])
    charge_and_release(restaurant, 1)
    assert seat_waiting_groups(restaurant) == [(10, 1)]
    assert restaurant["waiting_list"] == []

    print("All tests passed")

if __name__ == "__main__":
    _run_tests()