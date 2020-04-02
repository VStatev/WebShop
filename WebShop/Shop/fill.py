from flask import Flask
from datetime import date, timedelta, datetime
import random
from pymongo import MongoClient
from faker import Faker
from Shop.models import *
from Shop import db, mongo
import sys

#app = Flask(__name__)
#password = os.environ['MYSQL_ROOT_PASSWORD']
#db = os.environ['MYSQL_DATABASE']
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:'+password+'@'+ip/'+db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/imse_test'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = os.urandom(24)
#db = SQLAlchemy(app)
#client = MongoClient('mongodb://localhost:27017')
#mongo = client.imse

fake = Faker()

def fill_db():
    print("Starting to fill MySQL Database",file=sys.stdout)
    db.drop_all()
    db.create_all()
    for i in range(0,1000):
        si = str(i)
        user = User('uname'+ si ,'pass'+si, 'email'+si, datetime.now().date(), fake.first_name(), fake.last_name())
        db.session.add(user)
        db.session.commit()

        if i % 2 == 0:
            seller = Seller('uname'+si, 'VIP', round(random.uniform(1.0,5.0),2))
            db.session.add(seller)
            db.session.commit()

            for j in range(1,10):
                sj = str(j)
                id = db.session.query(Seller).count()
                sid = str(id)
                product = Product(id, 'Product Name'+sid +'_'+sj, round(random.uniform(3.0,15.0),2), random.randint(1,10) ,'Description of Product')
                db.session.add(product)
                db.session.commit()


        if i % 2 == 1:
            buyer = Buyer('uname'+si, 'Vienna', 1000+i, 'Street'+si, '+43688'+si)
            db.session.add(buyer)
            db.session.commit()

            for j in range(0,4):
                if j % 2 == 0:
                    order = Order(datetime.now().date()-timedelta(days=random.randint(1,730)),'Card')
                else:
                    order = Order(datetime.now().date()-timedelta(days=random.randint(1,730)),'Bank')

                db.session.add(order)
                db.session.commit()

                placed = Placed_Order('uname'+si, db.session.query(Order).count())
                db.session.add(placed)
                db.session.commit()

        if i % 10 == 0:
            person = Delivery_Person(fake.first_name(), fake.last_name(), fake.phone_number())
            db.session.add(person)
            db.session.commit()


        if(i in range(1,4)):
            sim = str(i-1)
            message = Messages('uname'+si, 'uname'+ sim, 'message')
            db.session.add(message)
            db.session.commit()

    for i in range(1, db.session.query(Order).count()):
        for j in range(i, i+2):
            oc = Order_Content(i,j)
            db.session.add(oc)
            db.session.commit()

    deliverer_count = db.session.query(Delivery_Person).count()

    for i in range(0, 100):
        delivery = Delivery(i+1, random.randint(1,deliverer_count), Placed_Order.query.filter_by(order_number=i+1).first().username, Order.query.filter_by(order_number=i+1).first().date + timedelta(days=random.randint(1,7)))
        db.session.add(delivery)
        db.session.commit()
    print("MySQL Database is filled", file=sys.stdout)
def migrate():
    print("Migrating data to MongoDB",file=sys.stdout)
    mongo.User.drop()
    mongo.Buyer.drop()
    mongo.Seller.drop()
    mongo.Product.drop()
    mongo.Delivery_Person.drop()
    mongo.Order.drop()
    mongo.Delivery.drop()

    users = User.query.all()
    for user in users:
        mongo_user={
            '_id' : user.username,
            'password' : user.password,
            'email' : user.email,
            'birthdate' : fake.date_time_between(start_date='-30y', end_date='-15y', tzinfo=None),
            'first_name' : user.first_name,
            'last_name' : user.last_name
        }
        mongo.User.insert_one(mongo_user)

    buyers = Buyer.query.all()
    for buyer in buyers:
        mongo_buyer = {
            '_id' : buyer.username,
            'parent' : buyer.username,
            'adress' : {
                'city' : buyer.city,
                'zip_code' : buyer.zip_code,
                'street' : buyer.street
            },
            'telephone_number' : buyer.telephone_number,
            'orders' : []
        }
        mongo.Buyer.insert_one(mongo_buyer)

    sellers = Seller.query.all()
    for seller in sellers:
        products = Product.query.filter_by(sellerID = seller.sellerID).all()
        mongo_seller = {
            '_id' : 'Seller'+ str(seller.sellerID),
            'parent' : seller.username,
            'mode' : seller.mode,
            'rating' : seller.rating,
        }
        mongo.Seller.insert_one(mongo_seller)
        for product in products:
            mongo_product = {
                '_id' : 'Product' + str(product.product_number),
                'seller' : mongo_seller['_id'],
                'name' : product.name,
                'price' : product.price,
                'quantity' : product.quantity,
                'description' : product.description
            }
            mongo.Product.insert_one(mongo_product)

    dps = Delivery_Person.query.all()
    for dp in dps:
        mongo_dp = {
            '_id' : 'DP' + str(dp.id),
            'first_name' : dp.first_name,
            'last_name' : dp.last_name,
            'telephone_number' : dp.telephone_number
        }
        mongo.Delivery_Person.insert_one(mongo_dp)

    orders = Order.query.all()
    for order in orders:
        po = Placed_Order.query.filter_by(order_number = order.order_number).first()
        oc = Order_Content.query.filter_by(order_number = order.order_number).all()
        mongo_order = {
            '_id' : 'Order' + str(order.order_number),
            'date' : fake.date_time_between(start_date='-2y', end_date='now', tzinfo=None),
            'payment' : order.payment,
            'content' : []
        }
        for order in oc:
            mongo_order['content'].append({
                'product' : 'Product'+str(order.product_number),
                'quantity' : random.randint(1,5)
            })
        mongo.Order.insert_one(mongo_order)

        mongo.Buyer.update_one(
            {'_id' : po.username},
            {'$push' : {'orders' : 'Order'+str(po.order_number)}}
        )

    deliveries = Delivery.query.all()
    for delivery in deliveries:
        mongo_delivery = {
            '_id' : {'Delivery_Person' : 'DP'+str(delivery.id), 'Order' : 'Order'+str(delivery.order_number)},
            'Buyer' : delivery.username,
            'date' : mongo.Order.find_one({'_id': 'Order'+str(delivery.order_number)})['date']+timedelta(days=random.randint(1,7))
        }
        mongo.Delivery.insert_one(mongo_delivery)
    print("Migration finished",file=sys.stdout)
