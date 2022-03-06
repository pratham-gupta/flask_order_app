from flask import Flask
from flasgger import Swagger
import os


# base dir: dir to store DB files
base_dir = os.getcwd()

app = Flask(__name__)
swagger = Swagger(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{base_dir}/dev.sqlite"

import core.routes
