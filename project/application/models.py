#from flask import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List ### New import
from sqlalchemy import ForeignKey, Float

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)


service_mechanics = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('ticket_id', db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'), primary_key=True)
)

inventory_service = db.Table(
    'inventory_service',
    Base.metadata,
    db.Column('ticket_id', db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('inventory_id', db.ForeignKey('inventory.id'), primary_key=True)
)

class Customers(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[int] = mapped_column(db.Integer, nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    service_tickets: Mapped[List['Service_tickets']] = db.relationship('Service_tickets', back_populates='customers') #New relationship attribute
    
class Service_tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date] = mapped_column(db.Date)
    VIN: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    service_desc: Mapped[str] = mapped_column(db.String(400), nullable=False)
    customers_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))
    
    customers: Mapped['Customers'] = db.relationship(back_populates='service_tickets')
    
    mechanics: Mapped[List['Mechanics']] = db.relationship(secondary=service_mechanics, back_populates='service_tickets')
    inventory: Mapped[List['Inventory']] = db.relationship(secondary=inventory_service, back_populates='service_tickets')

class Mechanics(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[int] = mapped_column(db.Integer, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    
    service_tickets: Mapped[List['Service_tickets']] = db.relationship(secondary=service_mechanics, back_populates='mechanics')    

class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)    
    service_tickets: Mapped[List['Service_tickets']] = db.relationship(secondary=inventory_service, back_populates='inventory')