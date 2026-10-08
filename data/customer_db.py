import json
import os

DB_FILE = "data/customers.json"


def load_customers():

    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_customer(customer):

    customers = load_customers()

    update = False

    for i, c in enumerate(customers):
        if (
            c.get("pon") == customer.get("pon")
            and
            str(c.get("onu_id")) == str(customer.get("onu_id"))
        ):

            customers[i] = customer
            update = True
            break

    if not update:
        customers.append(customer)

    with open(DB_FILE, "w") as f:
        json.dump(
            customers,
            f,
            indent=4
        )

def save_all_customers(customers):

    with open(DB_FILE, "w") as f:
        json.dump(
            customers,
            f,
            indent=4
        )
def delete_customer(pon, onu_id):

    customers = load_customers()

    customers = [
        c for c in customers
        if not (
            c.get("pon") == pon
            and
            str(c.get("onu_id")) == str(onu_id)
        )
    ]

    save_all_customers(customers)

def find_customers(keyword):

    customers = load_customers()

    keyword = str(keyword).lower()

    results = []

    for customer in customers:

        if (
            keyword in customer.get("name", "").lower()
            or keyword in customer.get("sn", "").lower()
            or keyword == str(customer.get("onu_id", ""))
            or keyword in customer.get("pppoe_user", "").lower()
        ):
            results.append(customer)

    return results

def get_customer(pon, onu_id):

    customers = load_customers()

    for c in customers:

        if (
            c.get("pon") == pon
            and
            str(c.get("onu_id")) == str(onu_id)
        ):
            return c

    return None

def update_customer(
    pon,
    onu_id,
    **kwargs
):

    cust = get_customer(
        pon,
        onu_id
    )

    if not cust:
        return False

    for k, v in kwargs.items():
        cust[k] = v

    save_customer(cust)

    return True
