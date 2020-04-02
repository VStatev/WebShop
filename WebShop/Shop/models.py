from flask_sqlalchemy import SQLAlchemy

from datetime import date, timedelta, datetime

import random

from faker import Faker

from Shop import db


faker = Faker()

class User(db.Model):
    __tablename__ = 'User'
    username = db.Column(db.String(40), primary_key=True)
    password = db.Column(db.String(40))
    email = db.Column(db.String(40))
    birthdate = db.Column(db.Date, default=datetime.now().date())
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))


    def __init__(self, username, password, email, birthdate, first_name, last_name):
        self.username = username
        self.password = password
        self.email = email
        self.birthdate = birthdate
        self.first_name = first_name
        self.last_name = last_name

class Messages(db.Model):
    __tablename__ = 'Messages'
    uname1 = db.Column(db.String(40), db.ForeignKey('User.username'), primary_key=True)
    uname2 = db.Column(db.String(40), db.ForeignKey('User.username'), primary_key=True)
    message = db.Column(db.String(120), primary_key=True)

    def __init__(self, uname1, uname2, message):
        self.uname1 = uname1
        self.uname2 = uname2
        self.message = message


class Seller(db.Model):
    __tablename__ = 'Seller'
    sellerID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), db.ForeignKey('User.username'))
    mode = db.Column(db.String(6))
    rating = db.Column(db.Float)


    def __init__ (self, username, mode, rating):
        self.username = username
        self.mode = mode
        self.rating = rating



class Buyer(db.Model):
    __tablename__ = 'Buyer'
    username = db.Column(db.String(40), db.ForeignKey('User.username'), primary_key=True)
    city = db.Column(db.String(40))
    zip_code = db.Column(db.Integer)
    street = db.Column(db.String(40))
    telephone_number = db.Column(db.String(25))


    def __init__(self, username, city, zip_code, street, telephone_number):
        self.username = username
        self.city = city
        self.zip_code = zip_code
        self.street = street
        self.telephone_number = telephone_number


class Product(db.Model):
    __tablename__ = 'Product'
    product_number = db.Column(db.Integer, primary_key=True)
    sellerID = db.Column(db.Integer, db.ForeignKey('Seller.sellerID'))
    name = db.Column(db.String(40))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    description = db.Column(db.String(120))

    def __init__(self, sellerID, name, price, quantity, description):
        self.sellerID = sellerID
        self.name = name
        self.price = price
        self.quantity = quantity
        self.description = description


class Order(db.Model):
    __tablename__ = 'Order'
    order_number = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, default=datetime.now().date())
    payment = db.Column(db.String(4))

    def __init__(self,date,payment):
        self.date = date
        self.payment = payment


class Placed_Order(db.Model):
    __tablename__ = 'PlacedOrder'
    username = db.Column(db.String(40), db.ForeignKey('Buyer.username'), primary_key=True)
    order_number = db.Column(db.Integer, db.ForeignKey('Order.order_number'), primary_key=True)

    def __init__(self, username, order_number):
        self.username = username
        self.order_number = order_number



class Order_Content(db.Model):
    __tablename__ = 'OrderContent'
    order_number = db.Column(db.Integer, db.ForeignKey('Order.order_number'), primary_key=True)
    product_number = db.Column(db.Integer, db.ForeignKey('Product.product_number'), primary_key=True)

    def __init__(self,order_number,product_number):
        self.order_number = order_number
        self.product_number = product_number



class Delivery_Person(db.Model):
    __tablename__ = 'DeliveryPerson'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(40))
    telephone_number = db.Column(db.String(25))


    def __init__(self,first_name, last_name, telephone_number):
        self.first_name = first_name
        self.last_name = last_name
        self.telephone_number = telephone_number


class Delivery(db.Model):
    __tablename__ = 'Delivery'
    order_number = db.Column(db.Integer, db.ForeignKey('Order.order_number'), primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('DeliveryPerson.id'), primary_key=True)
    username = db.Column(db.String(40), db.ForeignKey('Buyer.username'))
    date = db.Column(db.Date, default=datetime.now().date())

    def __init__(self,order_number,id, username, date):
        self.order_number = order_number
        self.id = id
        self.username = username
        self.date = date
