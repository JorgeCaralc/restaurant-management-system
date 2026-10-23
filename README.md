# restaurant-management-system
Capstone Python CUNEF – Restaurant Management System (CLI)

Command-line application that manages a full evening of service in a restaurant:
groups arrive, get seated (or wait for a table), order, pay and leave, over and over during the night.
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
├── restaurant_logic.py     # Rules: seating, waiting list, orders, bills, menu
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
| `main.py` (CLI): menu loop and options 1, 2, 5, 6, 7 | _to be decided_ | `feature/cli` |
| `restaurant_logic.py` (logic) + options 3 and 4 in `main.py` | _to be decided_ | `feature/restaurant-logic`, `feature/cli-orders` |
| `storage.py` (JSON) + novel feature lead | _to be decided_ | `feature/storage` |
| Novel feature: **waiting list** | all (led by the `storage.py` owner) | `feature/waiting-list` |

`main.py` is the longest module, so the logic owner also writes options 3 and 4. To avoid
merge conflicts, that is done **after** the `main.py` skeleton (menu loop + one empty
function per option) has been merged, in a new branch created from the updated `main`.

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
7. **Do not commit test changes to `data/restaurant.json`.** Testing option 5 changes that
   file. Before committing, if it appears in Source Control and you did not mean to change
   it, click the curved arrow (**Discard Changes**).

---

## 5. Data contracts

### 5.1 Restaurant dictionary

```python
restaurant = {
    # FIXED: comes from the JSON file and is saved back to it
    "name": "Casa Pepe",
    "capacity": 50,
    "max_tables": 5,
    "menu": {"Callos a la madrileña": 12, "Bocata de calamares": 5, "Cocido madrileño": 20},
    # TONIGHT: created empty when the restaurant is loaded, never saved
    "tables": [],
    "occupancy": 0,
    "earnings": 0,
    "waiting_list": [],     # novel feature: sizes of the groups waiting, in arrival order
}
```

| Key | Type | Saved to JSON? | Meaning |
|---|---|---|---|
| `name` | str | yes | Restaurant name |
| `capacity` | int > 0 | yes | Maximum number of people at the same time |
| `max_tables` | int > 0 | yes | Maximum number of tables at the same time |
| `menu` | dict {dish name: price} | yes | Price is a number > 0. The menu may be empty |
| `tables` | list of table dicts | no | Active tables (seated or ordered) |
| `occupancy` | int | no | People currently in the restaurant |
| `earnings` | number | no | Money charged tonight (2 decimals) |
| `waiting_list` | list of ints | no | Groups waiting for a table, e.g. `[6, 3]` (first = arrived first) |

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

### 5.3 Group lifecycle

| Stage | What happens |
|---|---|
| **Arrives** | Comes in a file loaded with option 2. If it is bigger than `capacity` it is rejected straight away (it would never fit). Otherwise it joins the end of `waiting_list` |
| **Seated** | When it fits, it leaves `waiting_list` and gets a table with `status = "seated"` and empty `orders`; `occupancy += customers` |
| **Ordered** | `orders` filled dish by dish (validated against the menu); `status = "ordered"` |
| **Charged & released** | `bill = sum of prices` (rounded to 2 decimals); `earnings += bill`; `occupancy -= customers`; table removed from `tables`. Then the waiting groups are checked again |

**A group fits** when both conditions are true:
`occupancy + customers <= capacity` **and** `len(tables) < max_tables`.

---

## 6. Design decisions

| # | Topic | Decision | Why |
|---|---|---|---|
| 1 | Table numbers | Lowest free physical number between 1 and `max_tables` | `len(tables) + 1` (labs) repeats numbers after a table is released. This never repeats among active tables and never goes above `max_tables`, like a real dining room |
| 2 | Table state | Text field `"status"`: `"seated"` / `"ordered"` | Readable in *Check status* and easy to extend with new states |
| 3 | Price changes | Each ordered dish stores its price when ordered | If option 5 changes a price, the table pays what the dish cost when it was ordered |
| 4 | Loading | The program starts empty; option 1 asks for the file (Enter = `data/restaurant.json`). Options 2–6 ask to load it first | Literal reading of the menu. Reloading asks for confirmation if a restaurant is already loaded (tonight's data would be lost), and only replaces it if the new file loads correctly |
| 5 | Saving the menu | Saved immediately after option 5 to the same file it was loaded from, and again on exit (option 7) | Nothing is lost if the program closes unexpectedly |
| 6 | Re-ordering | A table orders only once: option 3 only lists `"seated"` tables | Simple and faithful to the lifecycle in the statement |
| 7 | Dish names | Case-insensitive and ignoring extra spaces; empty names are rejected | "cocido madrileño" finds "Cocido madrileño", and no empty dish is ever saved |
| 8 | Invalid group file | The whole file is rejected, with a message saying which group is wrong and why | If we seated the valid groups, fixing the file and loading it again would seat them twice |
| 9 | Waiting list order | Go through the queue in arrival order and seat **every** group that fits | Uses free tables as soon as possible. Groups that were already waiting go before the new ones |
| 10 | Money | Bills rounded to 2 decimals and shown as `12.50` | Avoids results like `0.30000000000000004` |

---

## 7. Function contracts

### 7.1 `storage.py` — files

| Function | Receives | Returns | Errors (raised, not caught here) |
|---|---|---|---|
| `load_restaurant_data(path)` | path to the restaurant JSON | dict with `name`, `capacity`, `max_tables`, `menu` | `FileNotFoundError`, `json.JSONDecodeError`, `ValueError` (missing key or invalid value) |
| `list_group_files(folder)` | folder name, e.g. `"tables"` | sorted list of the `.json` file names in it (may be empty) | `FileNotFoundError` if the folder does not exist |
| `load_groups(path)` | path to a group requests JSON | list of ints, e.g. `[4, 2, 6]` | `FileNotFoundError`, `json.JSONDecodeError`, `ValueError` (see below) |
| `save_restaurant_data(path, restaurant)` | path and restaurant dict | nothing | `OSError` if the file cannot be written |

**Validation inside `storage.py`.** Any content with the wrong shape becomes a `ValueError`
with a clear message, never a `KeyError` or `TypeError`:
- restaurant file: must be an object with `name` (text), `capacity` and `max_tables`
  (int > 0) and `menu` (object whose prices are numbers > 0; it may be empty);
- group file: must be a list, and every element must be an object with `"customers"`
  as an int > 0. The message says which group is wrong, e.g. `Group 2: "customers" must be a whole number greater than 0`.
- "int" means a real int, not `True`/`False` (in Python, `True` counts as an int).

`save_restaurant_data` writes **only** `name`, `capacity`, `max_tables` and `menu`, using
`encoding="utf-8"`, `ensure_ascii=False` and `indent=4`. Every `open()` uses `encoding="utf-8"`.

### 7.2 `restaurant_logic.py` — rules (no `print()`, no `input()`)

| Function | Receives | Returns | Side effects |
|---|---|---|---|
| `create_restaurant(data)` | dict from `load_restaurant_data` | full restaurant dict | — |
| `seat_group(restaurant, customers)` | restaurant, number of people | table number, or `None` if it does not fit | Adds the table and updates `occupancy` |
| `add_to_waiting_list(restaurant, groups)` | restaurant, list of group sizes | list of the groups rejected because they are bigger than `capacity` | Adds the other groups to the end of `waiting_list` |
| `seat_waiting_groups(restaurant)` | restaurant | list of `(customers, table_num)` for the groups seated now | Goes through `waiting_list` in order, seats every group that fits (with `seat_group`) and removes it from the list |
| `get_tables(restaurant, status)` | restaurant, `"seated"` or `"ordered"` | list of tables in that state | — |
| `find_dish(menu, name)` | menu, text typed by the user | exact menu name, or `None` | — |
| `register_order(table, dishes, menu)` | table, list of exact menu names, menu | nothing | Fills `orders` with name + current price; `status = "ordered"` |
| `calculate_bill(table)` | table | total (sum of `"price"`, rounded to 2 decimals) | — |
| `charge_and_release(restaurant, table_num)` | restaurant, table number | the bill, or `None` if that table does not exist or has not ordered | Updates `earnings` and `occupancy`; removes the table |
| `add_or_update_dish(menu, name, price)` | menu, dish name, price | `True` if the dish already existed (updated), `False` if new | Modifies `menu`; the name is stored without extra spaces (if it existed with other capitals, updates that one) |

### 7.3 `main.py` — CLI (the only module that talks to the user)

| Function | What it does |
|---|---|
| `main()` | Menu loop. Holds `restaurant` (`None` until option 1) and the restaurant file path. Called from `if __name__ == "__main__":` |
| `ask_number(prompt)` | Asks until the user types a valid number greater than 0 and returns it as a float. Never crashes |
| `choose_table(tables)` | Shows the given tables and asks for a table number. Returns **the chosen table dict**, or `None` if the user presses Enter without typing (cancel). Only accepts numbers from the list. `main` checks that the list is not empty before calling it |
| One function per option | Load restaurant, load groups, take an order, charge a table, grow the menu, show status, exit |

What each option does:

1. **Load restaurant:** asks for the file path (Enter = `data/restaurant.json`). If a
   restaurant is already loaded, asks for confirmation first. Only replaces it if the new
   file loads correctly. The function returns the restaurant (new or old).
2. **Load new group requests:** shows the `.json` files in `tables/` (`list_group_files`),
   the user picks one, `load_groups` → `add_to_waiting_list` → `seat_waiting_groups`.
   Shows which groups were seated (and where), which were rejected and which are waiting.
3. **Take an order:** if there are no seated tables, or the menu is empty, it says so and
   goes back. Otherwise `choose_table` with the seated tables, then for each customer asks
   dish by dish (checked with `find_dish`); a customer finishes with an empty line once they
   have at least one dish. Then `register_order`.
4. **Charge and release:** `choose_table` with the ordered tables → shows the bill →
   `charge_and_release(restaurant, table["table_num"])` → `seat_waiting_groups` and shows
   who got the free table.
5. **Grow the menu:** asks the name (empty names are rejected) → if `find_dish` finds it,
   **warns** that it already exists → asks the price anyway with `ask_number` →
   `add_or_update_dish` → `save_restaurant_data` to the same file.
6. **Check status:** shows **everything the program holds**: name, capacity, `max_tables`,
   occupancy and free seats, tables in use, every active table (number, customers, status,
   ordered dishes with their saved price), the waiting list, the full menu with prices,
   and earnings.
7. **Exit:** if there are tables or waiting groups left, asks for confirmation. Saves the
   menu and closes.

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

Every time `main.py` calls a function of `storage.py` (to load **or to save**), it uses
`try/except`, shows a clear message and goes back to the menu. The program never closes
because of a file.

| Situation | Raised by | Caught by | User sees |
|---|---|---|---|
| File or `tables/` folder does not exist | `open()` / folder listing in `storage.py` | `main.py` | Message + menu again |
| File is not valid JSON | `json.load` in `storage.py` | `main.py` | Message + menu again |
| JSON has the wrong shape or invalid data (e.g. `[4, 2]` or `[{"people": 4}]`) | `storage.py` (`ValueError`) | `main.py` | Message saying what is wrong + menu again |
| The menu cannot be saved (e.g. file locked) | `open()` in `save_restaurant_data` | `main.py` | Message + the program keeps running |
| User types a non-number as a price | `float()` in `main.py` | `ask_number` | Asked again |
| User types a table number that is not in the list | — | `choose_table` | Asked again |
| Dish not on the menu | — (`find_dish` returns `None`) | `main.py` | Asked again |
| Group does not fit right now | — (`seat_group` returns `None`) | — | It stays in the waiting list |
| Group bigger than the capacity | — (`add_to_waiting_list` returns it) | `main.py` | "Group of N rejected: bigger than the restaurant" |

---

## 10. Open points (to decide as a team)

- [ ] **Who owns each module** (section 3).
- [x] Novel feature → waiting list (sections 5, 6 and 7).
- [x] Invalid group in a file → the whole file is rejected (decision 8).
- [x] Exit with tables or waiting groups left → ask for confirmation (option 7).

---

## 11. Ambiguities found in the statement (for the report)

- "The program starts by loading the restaurant" vs. menu option 1 "Load restaurant" → decision 4.
- A price can change (option 5) between ordering and charging → decision 3.
- Whether a table can order more than once → decision 6.
- Option 4 says to show the tables that are "served"; we read it as tables that have **ordered**.
- Option 5 talks about "growing the dishes of the table"; we read it as the restaurant's **menu**.
- No limit of customers per table: a group of any size uses one table if capacity allows it.
- What to do with a group that does not fit → it waits (novel feature); if it is bigger than the capacity, it is rejected.
- Loading the same group file twice → treated as new groups arriving again.
- Tonight's data (tables, occupancy, earnings, waiting list) is never saved: every run starts a new evening.
