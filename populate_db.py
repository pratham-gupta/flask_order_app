from flask import Flask
from core.models import db, Order, Product
from core.routes import addOrderProduct
import pandas as pd
import random


product_ids = [id[0] for id in db.session.query(Product.id).all()]
quantity = [10, 20, 30, 40, 50, 60]
dates = pd.date_range(start="2021/11/1", end="2022/3/6")
num_of_products = [1, 2, 3, 4]

print(len(product_ids))
for date in dates:

    date = date.to_pydatetime()
    n = random.choice(num_of_products)

    random_products = random.choices(product_ids, k=n)
    print(random_products)
    quantity = random.choices(quantity, k=n)
    # create order object

    order = Order(created_at=date)
    db.session.add(order)
    db.session.commit()
    product_quantity = [
        {"productid": random_products[i], "quantity": quantity[i]} for i in range(n)
    ]
    response = addOrderProduct(order, product_quantity)
    print(response)
