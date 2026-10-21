# restaurant-management-system
Capstone Python CUNEF – Restaurant Management System (CLI)

Command-line application that manages a full evening of service in a restaurant:
groups arrive, get seated, order, pay and leave, over and over during the night.
Built from the best parts of our Labs 02–04 (Python Programming, MSc in AI & Data Science).

> **This README is the team's contract.** Before coding a function, check here what it
> receives and what it returns. If something needs to change, change it here first
> (in a branch + Pull Request) so the three of us stay in sync.

---

## 1. How to run

```
python main.py
```

Run it from the project root folder (where `main.py` is), so the relative paths
`data/...` and `tables/...` work.

Group request files go inside `tables/`. That folder is **ignored by Git** (`tables*` in
`.gitignore`), so each member keeps their own test files. Format:

```json
[
    {"customers": 4},
    {"customers": 2},
    {"customers": 6}
]
```

---

## 2. Project structure

```
restaurant-management-system/
├── main.py                 # CLI: the only module that uses print() / input()
├── restaurant_logic.py     # Rules: seating, orders, bills, menu
├── storage.py              # Reading and writing JSON files
├── data/
│   └── restaurant.json     # Restaurant data (saved back when the menu grows)
└── tables/                 # Group requests (ignored by Git)
```

`main.py` imports `restaurant_logic` and `storage`. Those two never import `main`.

---

## 3. Team and responsibilities

| Module / task | Owner | Branch |
|---|---|---|
| `main.py` (CLI) | _to be decided_ | `feature/cli` |
| `restaurant_logic.py` (logic) | _to be decided_ | `feature/restaurant-logic` |
| `storage.py` (JSON) + novel feature lead | _to be decided_ | `feature/storage` |
| Novel feature | all (led by the `storage.py` owner) | `feature/<feature-name>` |

---

## 4. Workflow rules

1. **Never commit directly to `main`.** One branch per feature or per person.
2. **Before creating a branch:** switch to `main` → Source Control `···` → **Pull**.
   If your branch already exists and `main` has changed: Pull `main`, go back to your branch,
   then `···` → Branch → Merge Branch... → `main`.
3. **Small, frequent commits**, one per function that works. Message = verb + what + why
   (e.g. `Add seat_group with lowest free table number`), never "update" or "changes".
4. **Commit ≠ push.** A commit only lives on your computer until you Push / Publish Branch.
5. **Pull Requests are reviewed and merged by another member** (Review changes → Approve),
   using **"Create a merge commit"** (not Squash). Do not delete merged branches.
6. **Never use the same quotes inside and outside an f-string**
   (`f"{restaurant['name']}"`, not `f'{restaurant['name']}'`): it only works on Python 3.12+.

---

## 5. Data contracts

### 5.1 Restaurant dictionary

```python
restaurant = {
    # FIXED: comes from data/restaurant.json and is saved back to it
    "name": "Casa Pepe",
    "capacity": 50,
    "max_tables": 5,
    "menu": {"Callos a la madrileña": 12, "Bocata de calamares": 5, "Cocido madrileño": 20},
    # TONIGHT: created empty when the restaurant is loaded, never saved
    "tables": [],
    "occupancy": 0,
    "earnings": 0,
}
```

| Key | Type | Saved to JSON? | Meaning |
|---|---|---|---|
| `name` | str | yes | Restaurant name |
| `capacity` | int > 0 | yes | Maximum number of people at the same time |
| `max_tables` | int > 0 | yes | Maximum number of tables at the same time |
| `menu` | dict {dish name: price} | yes | Price is a number > 0 |
| `tables` | list of table dicts | no | Active tables (seated or ordered) |
| `occupancy` | int | no | People currently in the restaurant |
| `earnings` | number | no | Money charged tonight |

### 5.2 Table dictionary

```python
table = {
    "table_num": 2,        # physical table: lowest free number between 1 and max_tables
    "customers": 4,
    "status": "seated",    # "seated" -> "ordered"
    "orders": [],          # after ordering: [{"dish": "Cocido madrileño", "price": 20}, ...]
}
```

- `"dish"` always holds the name **exactly as written in the menu**, even if the waiter
  typed it with different capitals.
- `"price"` is the price **at the moment of ordering** (see decision 3).
- There is no `"bill"` key: the bill is calculated when charging, and the table is
  removed right after.

### 5.3 Table lifecycle

| Stage | What happens |
|---|---|
| **Seated** | New table with `status = "seated"` and empty `orders`; `occupancy += customers` |
| **Ordered** | `orders` filled dish by dish (validated against the menu); `status = "ordered"` |
| **Charged & released** | `bill = sum of prices`; `earnings += bill`; `occupancy -= customers`; table removed from `tables` |

---

## 6. Design decisions

| # | Topic | Decision | Why |
|---|---|---|---|
| 1 | Table numbers | Lowest free physical number between 1 and `max_tables` | `len(tables) + 1` (labs) repeats numbers after a table is released. This never repeats among active tables and never goes above `max_tables`, like a real dining room |
| 2 | Table state | Text field `"status"`: `"seated"` / `"ordered"` | Readable in *Check status* and easy to extend with new states |
| 3 | Price changes | Each ordered dish stores its price when ordered | If option 5 changes a price, the table pays what the dish cost when it was ordered |
| 4 | Loading | The program starts empty; option 1 loads the restaurant. Options 2–6 ask to load it first | Literal reading of the menu. Reloading with active tables asks for confirmation (it would erase tonight's tables) |
| 5 | Saving the menu | Saved immediately after option 5, and again on exit (option 7) | Nothing is lost if the program closes unexpectedly |
| 6 | Re-ordering | A table orders only once: option 3 only lists `"seated"` tables | Simple and faithful to the lifecycle in the statement |
| 7 | Dish names | Case-insensitive and ignoring extra spaces | "cocido madrileño" finds "Cocido madrileño" |
| 8 | Invalid group file | **The whole file is rejected** with a clear message (open for review, see section 10) | A corrupted file from the host system is not trusted at all |

---

## 7. Function contracts

### 7.1 `storage.py` — files

| Function | Receives | Returns | Errors (raised, not caught here) |
|---|---|---|---|
| `load_restaurant_data(path)` | path to the restaurant JSON | dict with `name`, `capacity`, `max_tables`, `menu` | `FileNotFoundError`, `json.JSONDecodeError`, `ValueError` (missing key or invalid value) |
| `load_groups(path)` | path to a group requests JSON | list of ints, e.g. `[4, 2, 6]` | `FileNotFoundError`, `json.JSONDecodeError`, `ValueError` (not a list, or a `"customers"` that is not an int > 0) |
| `save_restaurant_data(path, restaurant)` | path and restaurant dict | nothing | `OSError` if the file cannot be written |

`save_restaurant_data` writes **only** `name`, `capacity`, `max_tables` and `menu`, using
`encoding="utf-8"`, `ensure_ascii=False` and `indent=4`. Every `open()` uses `encoding="utf-8"`.

### 7.2 `restaurant_logic.py` — rules (no `print()`, no `input()`)

| Function | Receives | Returns | Side effects |
|---|---|---|---|
| `create_restaurant(data)` | dict from `load_restaurant_data` | full restaurant dict | — |
| `seat_group(restaurant, customers)` | restaurant, number of people | table number, or `None` if it does not fit | Adds the table and updates `occupancy` |
| `get_tables(restaurant, status)` | restaurant, `"seated"` or `"ordered"` | list of tables in that state | — |
| `find_dish(menu, name)` | menu, text typed by the user | exact menu name, or `None` | — |
| `register_order(table, dishes, menu)` | table, list of exact menu names, menu | nothing | Fills `orders` with name + current price; `status = "ordered"` |
| `calculate_bill(table)` | table | total (sum of `"price"`) | — |
| `charge_and_release(restaurant, table_num)` | restaurant, table number | the bill, or `None` if that table does not exist or has not ordered | Updates `earnings` and `occupancy`; removes the table |
| `add_or_update_dish(menu, name, price)` | menu, dish name, price | `True` if the dish already existed (updated), `False` if new | Modifies `menu` (if it existed with other capitals, updates that one) |

### 7.3 `main.py` — CLI (the only module that talks to the user)

| Function | What it does |
|---|---|
| `main()` | Menu loop. Holds `restaurant` (`None` until option 1) and the file paths. Called from `if __name__ == "__main__":` |
| `ask_number(prompt)` | Asks until the user types a valid positive number (`try/except ValueError`). Never crashes |
| `choose_table(tables)` | Shows the given tables and only accepts one of their numbers |
| One function per option | Load restaurant, load groups, take an order, charge a table, grow the menu, show status, exit |

**Take an order (option 3)**, as in Lab 04: dish by dish for each customer, at least one dish per
customer; each dish is checked with `find_dish` and rejected if it is not on the menu.

**Grow the menu (option 5)**: ask the name → if `find_dish` finds it, **warn** that it already
exists → ask the price anyway with `ask_number` → `add_or_update_dish` → `save_restaurant_data`.

**Check status (option 6)** must show **everything the program holds**: name, capacity,
`max_tables`, occupancy and free seats, tables in use, every active table (number, customers,
status, ordered dishes with their saved price), the full menu with prices, and earnings.

---

## 8. Design principles

1. **Only `main.py` talks to the user.** The other modules return values or raise exceptions,
   so the CLI decides what to show and the logic can be tested just by checking return values.
2. **`storage.py` raises file errors and `main.py` catches them** with `try/except`, so a bad
   file never closes the program.
3. **`storage.py` translates the file format into the program's format**
   (`[{"customers": 4}]` → `[4]`). If groups arrived through an API, only `storage.py` would change.
4. **No global variables.** Everything is created inside `main()` and passed as arguments.
   Code written directly under `if __name__ == "__main__":` is also global, so that block
   only calls `main()`.
5. **Lists and dictionaries are modified in place.** `seat_group` changes `restaurant`
   without returning it.

---

## 9. Error handling summary

| Situation | Raised by | Caught by | User sees |
|---|---|---|---|
| File does not exist | `open()` in `storage.py` | `main.py` | Message + menu again |
| File is not valid JSON | `json.load` in `storage.py` | `main.py` | Message + menu again |
| JSON has missing/invalid data | `storage.py` (`ValueError`) | `main.py` | Message + menu again |
| User types a non-number | `float()` / `int()` in `main.py` | `ask_number` | Asked again |
| Dish not on the menu | — (`find_dish` returns `None`) | `main.py` | Asked again |
| Group does not fit | — (`seat_group` returns `None`) | `main.py` | "No room for a group of N" |

---

## 10. Open points (to decide as a team)

- [ ] **Who owns each module** (section 3).
- [ ] **Novel feature.** It may change the data contracts, so we decide it before coding.
      Proposal: a **waiting list** — groups that do not fit wait in `restaurant["waiting_list"]`
      and are seated automatically when a table is released.
- [ ] **Invalid group in a file** (decision 8): reject the whole file, or seat the valid
      groups and skip the invalid ones?
- [ ] **Exit with tables not charged yet:** warn before closing?

---

## 11. Ambiguities found in the statement (for the report)

- "The program starts by loading the restaurant" vs. menu option 1 "Load restaurant" → decision 4.
- A price can change (option 5) between ordering and charging → decision 3.
- No limit of customers per table: a group of any size uses one table if capacity allows it.
- Whether a table can order more than once → decision 6.
