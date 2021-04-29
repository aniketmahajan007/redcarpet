from flask import Flask
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

from routes.agent import *
from routes.admin import *
from routes.combine import *
from routes.users import *


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)