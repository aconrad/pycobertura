def qualifies_for_discount(quantity, price):
    if quantity >= 10 or price <= 100:
        print("You qualify for a discount!")
    else:
        print("No discount available.")
