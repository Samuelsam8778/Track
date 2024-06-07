from . import db, app
from flask_bcrypt import Bcrypt
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_marshmallow import Marshmallow
bcrypt = Bcrypt()

ma = Marshmallow(app)


class User(db.Model):
    __tablename__ = 'track_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128))

    # def set_password(self, password):
    #     self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    #
    # def check_password(self, password):
    #     return bcrypt.check_password_hash(self.password_hash, password)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True  # If you have foreign keys and want to include them in the serialization


# Initialize schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

