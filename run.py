from core import app
from core.models import db

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)