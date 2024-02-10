from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Table, Numeric
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import func
from datetime import datetime, timezone
from crypto_track.enums import TimeOptions

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Association Table for the many-to-many relationship between User and Crypto
user_crypto_association = Table('user_crypto', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('crypto_id', ForeignKey('cryptos.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    joined_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tracking_cryptos = relationship(
        "Crypto",
        secondary=user_crypto_association,
        back_populates="tracked_by_users")
    how_often = Column(Enum(TimeOptions))

    def __repr__(self) -> str:
        return f'User(id={self.id}, name={self.name}, joined_date={self.joined_date}, how_often={self.how_often.value})'

class Crypto(Base):
    __tablename__ = "cryptos"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    symbol = Column(String(10), unique=True)
    prices = relationship("Price", back_populates="crypto")
    tracked_by_users = relationship(
        "User",
        secondary=user_crypto_association,
        back_populates="tracking_cryptos")
    
    def __repr__(self) -> str:
        return f"Crypto(id={self.id}, name='{self.name}', symbol='{self.symbol}', current_price='[dynamic]')"

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    crypto_id = Column(Integer, ForeignKey('cryptos.id'))
    price = Column(Numeric(precision=10, scale=2))
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    crypto = relationship("Crypto", back_populates="prices")


    def __repr__(self) -> str:
            return f"Price(id={self.id}, crypto_id={self.crypto_id}, price={self.price}, date='{self.date.isoformat()}')"
