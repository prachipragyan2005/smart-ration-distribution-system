from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User(
        username="admin",
        password=generate_password_hash("1234"),
        role="admin"
    )
    db.session.add(user)
    db.session.commit()

print("User Added Successfully ✅")