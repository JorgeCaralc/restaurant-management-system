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

    print("All tests passed")


if __name__ == "__main__":
    _run_tests()