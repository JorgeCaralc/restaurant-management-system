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

    print("All tests passed")

if __name__ == "__main__":
    _run_tests()