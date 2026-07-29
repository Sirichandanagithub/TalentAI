from sqlalchemy import text
from app.database.session import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(result.scalar())
        print("✅ Database connected successfully!")
except Exception as e:
    print("❌ Connection failed")
    print(e)