from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import jwt
import datetime
import qrcode
import io
import pyotp
import bcrypt
from functools import wraps

app = Flask(__name__)

# Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'secure_api'
app.config['SECRET_KEY'] = 'ahmed!@@546551563456ffdefcvescsdfvkm'

mysql = MySQL(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = data['user']

            cur = mysql.connection.cursor()
            cur.execute("SELECT last_token FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()

            if not user or user[0] != token:
                return jsonify({'message': 'Invalid or expired token!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'message': 'Invalid input data'}), 400

        username = data['username']
        password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        secret = pyotp.random_base32()
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, twofa_secret) VALUES (%s, %s, %s)", 
                    (username, password, secret))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'message': 'User registered successfully', 'secret': secret})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/qrcode/<username>', methods=['GET'])
def generate_qr(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT twofa_secret FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    totp = pyotp.TOTP(user[0])
    uri = totp.provisioning_uri(username, issuer_name='SecureAPI')
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf.getvalue(), 200, {'Content-Type': 'image/png'}

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['username', 'password', 'otp']):
            return jsonify({'message': 'Invalid input data'}), 400

        username = data['username']
        password = data['password']
        otp = data['otp']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            cur.close()
            return jsonify({'message': 'Invalid credentials'}), 401

        totp = pyotp.TOTP(user[3])
        if not totp.verify(otp):
            cur.close()
            return jsonify({'message': 'Invalid 2FA code'}), 401

        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, 
                           app.config['SECRET_KEY'], algorithm='HS256')

        cur.execute("UPDATE users SET last_token = %s WHERE username = %s", (token, username))
        mysql.connection.commit()
        cur.close()

        return jsonify({'token': token})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product', methods=['POST'])
@token_required
def create_product():
    try:
        data = request.get_json()

        if not isinstance(data, dict):  
            return jsonify({'message': 'Invalid JSON format, expected an object'}), 400

        if not all(key in data for key in ('name', 'description', 'price', 'quantity')):
            return jsonify({'message': 'Missing required fields'}), 400

        name = data['name']
        description = data['description']
        price = data['price']
        quantity = data['quantity']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products (name, description, price, quantity) VALUES (%s, %s, %s, %s)",
                    (name, description, price, quantity))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Product created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET'])
@token_required
def get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    
    products_list = [{'id': p[0], 'name': p[1], 'description': p[2], 'price': p[3], 'quantity': p[4]} for p in products]
    
    return jsonify(products_list)

@app.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('name', 'description', 'price', 'quantity')):
            return jsonify({'message': 'Missing required fields'}), 400

        cur = mysql.connection.cursor()
        cur.execute("UPDATE products SET name=%s, description=%s, price=%s, quantity=%s WHERE id=%s",
                    (data['name'], data['description'], data['price'], data['quantity'], product_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Product updated'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product deleted'})

if __name__ == '__main__':
    app.run(debug=True)
