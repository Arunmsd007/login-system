Secure Authentication System with Flask and MongoDB

This is a full-stack web application demonstrating a secure, feature-rich authentication and session management system. It features a Python backend built with Flask and a modern, responsive frontend built with HTML, Tailwind CSS, and vanilla JavaScript.

Live Demo: https://login-system-7t50.onrender.com/

📋 Project Outcome

This project successfully implements a secure login system that provides:

Secure User Registration: Passwords are never stored in plain text. They are securely hashed using bcrypt before being stored in the database.

Secure Authentication: The system uses JSON Web Tokens (JWT) for stateless and secure user authentication.

Secure Session Management: User login and logout times are tracked, providing administrators with a clear view of user activity.

✨ Key Features

JWT Authentication: Secure, stateless authentication using PyJWT.

Password Encryption: bcrypt is used for one-way hashing of user passwords.

Role-Based Access Control: Differentiates between regular user roles and admin roles, showing different views upon login.

Admin Dashboard: A secure, admin-only dashboard to view all user login/logout sessions and delete session records.

Forgot Password: Allows users to securely reset their password.

Session Tracking: Logs user login and logout times to a separate collection for auditing.

Modern Frontend: A responsive UI with a real-time password strength meter and show/hide password toggles for better usability.

🛠️ Technologies Used

Backend: Python, Flask, Gunicorn

Database: MongoDB (via Atlas)

Authentication: PyJWT (JSON Web Tokens), bcrypt (Password Hashing)

Frontend: HTML5, CSS3, JavaScript, Tailwind CSS

Deployment: Configured for Render (or any other PaaS)

🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

Prerequisites

Python 3.8+

A MongoDB Atlas account (the free tier is sufficient)

1. Clone the Repository

git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name


2. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

Install all the required Python libraries from the requirements.txt file.

pip install -r requirements.txt


4. Configure Environment Variables

Create a file named .env in the root of your project folder. This file will hold your secret keys. This file should never be committed to GitHub.

# .env file

# Your MongoDB Atlas connection string
MONGO_URI='mongodb+srv://<username>:<password>@yourcluster.mongodb.net/my_app_db?retryWrites=true&w=majority'

# A strong, random secret key for signing JWTs
SECRET_KEY='your_strong_random_secret_key'


Replace the MONGO_URI with your own connection string from MongoDB Atlas.

Generate a SECRET_KEY by running this command in your terminal: python -c "import secrets; print(secrets.token_hex(32))"

5. Create Your First Admin User

The application requires at least one admin user to access the dashboard.

Run the application (python app.py) and register a user through the web interface.

Go to your MongoDB Atlas dashboard, navigate to the users collection, and find the user you just created.

Edit the user document and add a new field:

Field: role

Value: admin

Save the change. This user now has admin privileges.

🏃 Running the Application

Start the Flask Backend Server:

python app.py
