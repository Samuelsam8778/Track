import io
from flask import request, send_file, jsonify # type: ignore
from botocore.exceptions import NoCredentialsError
from .models import User
from . import app, s3,S3_BUCKET_NAME


@app.route("/upload_track", methods=["GET,","POST"])
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


@app.route('/get_all_tracks', methods = ['GET'])
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

    if User.query.filter_by(email=email).first():
        return "Email Id already Exist"
    
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
               


if __name__ == "__main__":
    app.run(debug=True)