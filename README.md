# Secure RESTful API with Flask & MySQL

## Overview
This project is a secure RESTful API built using Flask and MySQL. It features user authentication with JWT tokens and Two-Factor Authentication (2FA) using TOTP via Google Authenticator. Additionally, it allows authenticated users to manage products (CRUD operations).

## Features
- User registration with password hashing (bcrypt) and 2FA secret generation
- Two-Factor Authentication (TOTP) with QR code generation (Compatible with Google Authenticator)
- JWT-based authentication with token validation
- CRUD operations for products (Create, Read, Update, Delete)
- Middleware for token authentication

## Technologies Used
- Python (Flask)
- MySQL
- Flask-MySQLdb
- JWT (PyJWT)
- bcrypt (for password hashing)
- pyotp (for 2FA with Google Authenticator)
- qrcode (for QR code generation)

## Installation

### Prerequisites
Make sure you have the following installed:
- Python 3
- MySQL
- pip (Python package manager)

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/ghaza1/SecureAPI-Flask-Using-Google-Authenticator.git
   cd SecureAPI-Flask-Using-Google-Authenticator
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-mysqldb pyjwt bcrypt pyotp qrcode
   ```

3. Configure MySQL database:
   - Create a database named `secure_api`
   - Use the following schema:
     ```sql
     CREATE TABLE users (
         id INT AUTO_INCREMENT PRIMARY KEY,
         username VARCHAR(255) UNIQUE NOT NULL,
         password VARCHAR(255) NOT NULL,
         twofa_secret VARCHAR(255) NOT NULL,
         last_token TEXT
     );
     
     CREATE TABLE products (
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(255) NOT NULL,
         description TEXT,
         price DECIMAL(10,2) NOT NULL,
         quantity INT NOT NULL
     );
     ```


4. Run the application:
   ```bash
   python app.py
   ```

## API Endpoints

### User Authentication
#### Register a New User
- **Endpoint:** `POST /register`
- **Request Body:**
  ```json
  {
    "username": "testuser",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User registered successfully",
    "secret": "JBSWY3DPEHPK3PXP"
  }
  ```

#### Generate QR Code for 2FA (Google Authenticator Compatible)
- **Endpoint:** `GET /qrcode/<username>`
- **Response:** PNG image (QR Code for Google Authenticator)
![QR](/qr.png)



#### Login with 2FA
- **Endpoint:** `POST /login`
- **Request Body:**
  ```json
  {
    "username": "testuser",
    "password": "securepassword",
    "otp": "123456"
  }
  ```
- **Response:**
  ```json
  {
    "token": "jwt_token_here"
  }
  ```

### Product Management (Authenticated Users Only)
#### Create a Product
- **Endpoint:** `POST /product`
- **Headers:**
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Request Body:**
  ```json
  {
    "name": "Laptop",
    "description": "High-end gaming laptop",
    "price": 1500.99,
    "quantity": 10
  }
  ```
- **Response:**
  ```json
  {
    "message": "Product created successfully"
  }
  ```

#### Get All Products
- **Endpoint:** `GET /products`
- **Headers:**
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Response:**
  ```json
  [
    {
      "id": 1,
      "name": "Laptop",
      "description": "High-end gaming laptop",
      "price": 1500.99,
      "quantity": 10
    }
  ]
  ```

#### Update a Product
- **Endpoint:** `PUT /products/<product_id>`
- **Headers:**
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Request Body:**
  ```json
  {
    "name": "Updated Laptop",
    "description": "Updated description",
    "price": 1700.99,
    "quantity": 8
  }
  ```
- **Response:**
  ```json
  {
    "message": "Product updated"
  }
  ```

#### Delete a Product
- **Endpoint:** `DELETE /products/<product_id>`
- **Headers:**
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Response:**
  ```json
  {
    "message": "Product deleted"
  }
  ```

## Security Features
- **Password Hashing:** Uses bcrypt to securely store user passwords.
- **Two-Factor Authentication:** Users must verify their login using an OTP from Google Authenticator.
- **JWT Authentication:** Secure authentication mechanism for API requests.
- **Token Revocation:** Tokens are stored in the database to prevent reuse of old tokens.

## License
This project is open-source and available under the MIT License.

