from passlib.context import CryptContext
from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import declarative_base, mapped_column, sessionmaker

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def set_password(self, raw_password: str):
        """Устанавливает хешированный пароль"""
        self.password = pwd_context.hash(raw_password)

    def check_password(self, raw_password: str):
        """Проверяет пароль"""
        return pwd_context.verify(raw_password, self.password)

    def __repr__(self):
        return f"<User(username={self.username})>"


engine = create_engine("sqlite:///app/database/database.db", echo=False)
Base.metadata.create_all(engine)

session_factory: SessionType = sessionmaker(bind=engine)

def create_session() -> SessionType:
    with session_factory() as session:
        yield session