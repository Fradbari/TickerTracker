from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy import func as sa_func
from src.shared.infra.database import Base

class AppConfig(Base):
    __tablename__ = "app_config"

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa_func.now(), onupdate=sa_func.now())

    def __repr__(self) -> str:
        return f"<AppConfig(key={self.key})>"
