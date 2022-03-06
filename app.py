from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


base_dir = os.getcwd()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{base_dir}/dev.db"


db = SQLAlchemy(app)
ma = Marshmallow(app)
#models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50),nullable=False)
    product_sku = db.Column(db.String(50),nullable=True)
    price = db.Column(db.Float,nullable=False)


#serializer
class Product_Schema(ma.Schema):
    class Meta:
        fields = ("id","product_name",'product_sku',"price")



product_schema = Product_Schema()
products_schema = Product_Schema(many=True)

@app.route("/")
def index():
    return "Hello world"


@app.route("/get_product")
def get_products():
    products = Product.query.all()
    return jsonify(products_schema.dump(products))


if __name__ == "__main__":
    db.create_all()
    product1 = Product(
        product_name="Test_product",product_sku="123456",
        price=25.5
    )
    db.session.add_all([product1])
    db.session.commit()
    app.run(debug=True)