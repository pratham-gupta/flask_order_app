from core import app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from core.serializers import Product_Serializer
from sqlalchemy.orm import backref, relationship
import datetime


# db instance
db = SQLAlchemy(app)
ma = Marshmallow(app)

# models


# reference table to map different product to different orders: many to many relation
# )
class OrderProduct(db.Model):
    __tablename__ = "order_product_association"
    orderproductid = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id")
    )  # foreign key to join Order item to order
    quantity = db.Column(
        db.Integer, nullable=False
    )  # foreign key to join Order item to products


class Product(db.Model):
    """Product tabels stores the product informations,
    args:
        product_name: name of the product, max 50 characters
        price: price of product float value
    """

    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    # product_sku = db.Column(db.String(50),nullable=True)
    order = db.relationship(
        "OrderProduct", backref="product_mapper"
    )  # product mapper can be used to cross reference order relative to current procut object. eg. Product.product_mapper will give the order object it belongs to
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product: {self.product_name}>"


class Order(db.Model):
    """Order table stores manifested order information"""

    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    # product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    product = db.relationship(
        "OrderProduct", backref="order_mapper"
    )  # order mapper can be used to cross reference product relative to current order object.
    order_total = db.Column(db.Integer, nullable=True, default=0)

    def __repr__(self):
        return f"<Order: {self.id} >"


if __name__ == "__main__":

    # run the model script to add dummy data to db
    db.create_all()
    product1 = Product(product_name="Test_product", product_sku="123456", price=25.5)
    product2 = Product(product_name="Python Book", product_sku="abcabc", price=25)

    order1 = Order()
    order1.product.append(product1)
    order1.product.append(product2)

    db.session.add_all([product1, product2])
    db.session.add_all([order1])

    db.session.commit()
    # app.run(debug=True)
