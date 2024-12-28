from flask_sqlalchemy import SQLAlchemy
from src.db.models import BaseModel

db: SQLAlchemy = SQLAlchemy(model_class=BaseModel)

