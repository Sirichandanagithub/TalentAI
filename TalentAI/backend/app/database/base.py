from app.database.base_class import Base

# Import all models so Alembic can detect them
from app.auth.models import User
from app.resume.models import Resume