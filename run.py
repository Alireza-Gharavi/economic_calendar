from flask import Flask
from V1 import blueprint as api
from flask_cors import CORS
import os

app = Flask('__name__')


os.system("python db_manager.py&")

app.register_blueprint(api, url_prefix='/Economic_Calendar/v1')

CORS(app, resource={r"*/": {"origins":"*"}})


if __name__ == '__main__' :
    app.run(host="0.0.0.0", port=5000)
