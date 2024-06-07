import io
from flask import Flask # type: ignore
import boto3
from flask_cors import CORS # type: ignore
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .db import Config
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_marshmallow import Marshmallow


db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.config['JWT_SECRET_KEY'] = 'track_001'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

CORS(app)

s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))


S3_BUCKET_NAME = os.getenv('BUCKET_NAME')
