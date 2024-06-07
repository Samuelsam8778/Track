import io
from flask import request, send_file, jsonify
from botocore.exceptions import NoCredentialsError
from .models import User, UserSchema
from . import app, s3, S3_BUCKET_NAME
from . import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/upload_track", methods=["GET,", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files['file']
    try:
        s3.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
        return "File Uploaded Successfully"
    except NoCredentialsError:
        return "Enter Valid Credential"


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        mp3_data = obj['Body'].read()
        return send_file(
            io.BytesIO(mp3_data),
            mimetype='audio/mpeg'
        )
    except NoCredentialsError:
        return "AWS credentials not available."


@app.route('/get_all_tracks', methods=['GET'])
def get_all_tracks():
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
        files = [obj['Key'] for obj in response['Contents']]
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if User.query.filter_by(email=email).first():
        return "Email Id already Exist"

    new_user = User(username=username, email=email, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return "User Added Successfully"


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        access_token = create_access_token(identity={"email": email, "role": user.role})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            print(claims['sub']['role'], "*********************")
            if claims['sub']['role'] != role:
                return jsonify(msg="Access forbidden: You do not have the required permissions"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/users_list', methods=['GET'])
@jwt_required()
@role_required('Admin')
def user_list():
    users_list = User.query.all()
    return users_schema.dump(users_list)


if __name__ == "__main__":
    app.run(debug=True)
