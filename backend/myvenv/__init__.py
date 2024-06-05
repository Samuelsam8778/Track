import io
from flask import Flask # type: ignore
import boto3
from flask_cors import CORS # type: ignore
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .db import Config


db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

s3 = boto3.client('s3',
                  aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))


S3_BUCKET_NAME = os.getenv('BUCKET_NAME')
