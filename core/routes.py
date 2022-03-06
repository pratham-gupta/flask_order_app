from core import app
from core.models import db, Product, Order, OrderProduct
from core.serializers import Product_Serializer
from flask import jsonify, Flask, request, Response, send_file
import json
import pandas as pd
import datetime
from io import BytesIO


product_serializer = Product_Serializer(many=True)


def addOrderProduct(order, productids):
    """Function to add products corresponding to an order to OrderProduct table.
    Args:
        order: Order object corresponding to an order id
        productids: dict or list of dict containing productids and quantity
                    eg: [{'productid':1,'quantity':10},{'productid':2,'quantity':20}]
    Returns:
        flask.Response"""

    print("add order priduct called.")
    orderid = order.id
    if isinstance(productids, dict):
        productids = [productids]

    elif isinstance(productids, list):
        pass
    else:
        return Response(
            json.dumps(
                {
                    "Bad Requst": "Invaid productids Argument passed,takes list of dict or dict of the form [ {'productid':1,'quantity':1}}]"
                }
            ),
            status=403,
            mimetype="application/json",
        )

    # delete existing products for the given order from OrderProduct table before updating/adding new products
    # OrderProduct.query.filter_by(order_id=orderid).delete()
    db.session.commit()

    for prod in productids:
        product_id = prod["productid"]
        quantity = prod["quantity"]
        orderproduct = OrderProduct(
            order_id=orderid, product_id=product_id, quantity=quantity
        )

        db.session.merge(orderproduct)
        db.session.commit()

    order_products = OrderProduct.query.filter_by(order_id=orderid).all()
    order_total_price = 0
    for prod in order_products:
        order_total_price += int(prod.quantity) * float(prod.product_mapper.price)

    # update total order price for order object
    order.order_total = order_total_price

    db.session.commit()

    return Response(
        json.dumps({"Success": "Order has been accepted"}),
        status=200,
        mimetype="application/json",
    )


@app.route(
    "/getproducts",
)
def get_products():
    products = Product.query.all()
    return jsonify(product_serializer.dump(products))


@app.route("/add_products", methods=["POST"])
def add_products():
    """
    Add products to DB
    Takes csv file containing product information,
    add products to database, update if already exists.
    ---
    tags:
      - products
    parameters:
      - name: file
        in: formData
        description: csv file containing product info
        required: tr
        type: file
        default: None
    responses:
      200:
        description: Products added successfully
        schema:
            $ref: '#/definitions'
      400:
        description: Bad request, invalid file schema
        schema:
            $ref: '#/definitions'

    """
    if request.method == "POST":

        files = request.files["file"]
        df = pd.read_csv(files)
        # file schema validation
        if all([col in ["product_id", "price", "product_name"] for col in df.columns]):
            # if all columns are present, proceed with file
            for index, row in df.iterrows():
                product_id = row["product_id"]
                price = row["price"]
                product_name = row["product_name"]

                # check if product exists

                product = Product.query.get(product_id)
                if product == None:
                    # create new product
                    product = Product(
                        id=product_id, product_name=product_name, price=price
                    )
                    db.session.add(product)
                    db.session.commit()

                else:
                    # update existing product.
                    product.product_name = product_name
                    product.price = price
                    db.session.commit()

            return Response(
                json.dumps({"Success": "Product have been added successfully"}),
                status=200,
            )

        else:
            return Response(
                json.dumps(
                    {
                        "Bad Request": "Invalid File Passed, must contain following cols 'product_id','price','product_name'"
                    }
                ),
                status=400,
            )


@app.route("/add_order", methods=["POST"])
def add_order():
    """
    Post Endpoint to add order
    ---
    tags:
      - add order
    consumes:
      - "application/json"
    produces:
      - "application/json"

    parameters:
      - in: "body"
        name: "body"
        required: true
        schema:
          type: object
          properties:
            order:
              type: "object"
          example: {"orderid":1, "products":[{"productid":"1","quantity":10},{"productid":"2","quantity":"20"} ]}


    responses:
      200:
        description: The product inserted in the database

      404:
        description: Invalid Order Id

      403:
        description: Invalid request body.

    """

    if request.method == "POST":
        data = json.loads(request.data)
        print(data)
        orderid = data.get("orderid")
        products = data.get("products")

        if orderid == None:
            # if the orderid is None, create a new order
            order = Order()
            db.session.add(order)
            db.session.commit()

        else:
            order = Order.query.get(orderid)

            if order == None:
                return Response(
                    json.dumps(
                        {"Bad Request": "Invalid Order Id, order does not exist"}
                    ),
                    status=404,
                    mimetype="application/json",
                )

            # add products to orderproduct
        response = addOrderProduct(order, products)
        return response


@app.route("/product_report", methods=["POST"])
def product_report():
    """
    Post Endpoint to generate order report for given dates
    ---
    tags:
      - generate order report
    consumes:
      - "application/json"
    produces:
      - "text/csv"

    parameters:
      - in: "body"
        name: "body"
        required: true
        schema:
          type: object
          properties:
            dates:
              type: "object"

          example: {"start_date":"2022-03-06", "end_date":"2022-03-06"}


    responses:
      200:
        description: Report generated successfully

    """

    if request.method == "POST":
        data = json.loads(request.data)
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        start_date = datetime.datetime.fromisoformat(start_date).replace(
            hour=0, minute=0, second=0
        )
        end_date = datetime.datetime.fromisoformat(end_date).replace(
            hour=23, minute=59, second=59
        )

        query = (
            db.session.query(Order, Product, OrderProduct)
            .join(OrderProduct, OrderProduct.order_id == Order.id)
            .join(Product, Product.id == OrderProduct.product_id)
            .filter(Order.created_at >= start_date)
            .filter(Order.created_at <= end_date)
        )
        # print(order_data)
        report_data = pd.read_sql(query.statement, query.session.bind)
        print(report_data.head(5))
        report = (
            report_data.groupby(["product_name", "price"])
            .agg({"quantity": "sum"})
            .reset_index()
        )
        report["Total Amount"] = report["price"] * report["quantity"]

        response_stream = BytesIO(report.to_csv().encode())
        return send_file(
            response_stream, mimetype="text/csv", attachment_filename="report.csv"
        )
