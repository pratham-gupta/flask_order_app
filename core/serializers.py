from flask_marshmallow import Marshmallow
from core import app

ma = Marshmallow(app)


# serializers
class Product_Serializer(ma.Schema):
    """
    Serializers to serialize the given product object
    and deserializer product object from incoming request.
    """

    class Meta:
        # field names are sensitive to model definition
        fields = ("id", "product_name", "product_sku", "price")
