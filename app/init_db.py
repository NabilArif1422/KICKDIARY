from app.database import engine, Base
from app.models import User, CustomMetric, Match, MatchMetricValue, Story, ActivityLog

def init_db():
    """Membuat seluruh tabel database sesuai model jika belum ada."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
