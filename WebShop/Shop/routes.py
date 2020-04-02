from flask import render_template, request, redirect, url_for, make_response, session
from sqlalchemy import func
from datetime import date, timedelta, datetime
import random
import sys
from Shop import app, db, mongo

@app.route('/')
def welcome():
    return render_template('landing.html')

@app.route('/reporting', methods=['GET','POST'])
def reporting():
    if request.method == 'POST':
        requested = request.form['id']
        requested = 'Seller'+str(requested)
        products = [product['_id'] for product in mongo.Product.find({"seller":requested})]
        orders = [order['_id'] for order in mongo.Order.find({ "content.product":{"$in":products}})]
        for order in orders:
            reporting = mongo.Delivery.aggregate([
            {
                "$match":{
                    "_id.Order" : {"$in":orders},
                    "date" : {"$gte":datetime.utcnow()-timedelta(days=365),"$lte":datetime.utcnow()}
                    }
                },
                {
                    "$group":{"_id":"$_id.Delivery_Person", "count":{"$sum":1}}
            }
            ])
        return render_template('reporting.html', reporting = reporting, requested = requested)
    else:
        return render_template('reporting.html', reporting = None)

@app.route('/home')
def homepage():
    cookies = request.cookies
    loged = False
    if 'User' in session:
        username = session['User']
        output = 'Welcome ' + username
        loged = True
    else:
        output = 'Welcome to the webshop!'
    return render_template('home.html', output = output, loged = loged)


@app.route('/login',methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        uname = request.form['username']
        password = request.form['password']
        user = mongo.User.find_one({'_id' : uname})
        if user == None:
            error = 'User not found'
        elif password == user['password']:
            session['User'] = user['_id']
            orders = mongo.Order.find().count() + 1
            order = {
                '_id' : 'Order'+str(orders),
                'date' : datetime.utcnow(),
                'payment' : 'Card',
                'content' :[]
            }
            mongo.Order.insert_one(order)
            mongo.Buyer.update_one(
                {'_id' : uname},
                {'$push' : {'orders' : 'Order'+str(orders)}}
            )
            session['Order'] = 'Order'+str(orders)
            return redirect('/home')
        else:
            error = 'Wrong Password'

    return render_template('login.html', error=error)

@app.route("/register_buyer", methods=["GET", "POST"])
def register_buyer():
    error = None
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        bday = request.form['bday']
        fname = request.form['fname']
        lname = request.form['lname']
        city = request.form['city']
        zip = request.form['zip']
        street = request.form['street']
        telephone = request.form['telephone']

        try:
            user = {
                '_id' : uname,
                'password' : passw,
                'birthdate' : bday,
                'first_name' : fname,
                'last_name' : lname
            }

            mongo.User.insert_one(mongo_user)

            buyer = {
                '_id' : uname,
                'parent' : uname,
                'adress' : {
                    'city' : city,
                    'zip_code' : zip,
                    'street' : street
                },
                'telephone_number' : telephone,
                'orders' : []
            }

            mongo.Buyer.insert_one(buyer)

            session['User'] = uname
            orders = mongo.Order.find().count() + 1
            order = {
                '_id' : 'Order'+str(orders),
                'date' : datetime.utcnow(),
                'payment' : 'Bank',
                'content' :[]
            }
            mongo.Order.insert_one(order)
            mongo.Buyer.update_one(
                {'_id' : uname},
                {'$push' : {'orders' : 'Order'+str(orders)}}
            )
            session['Order'] = 'Order'+str(orders)
            return redirect('/home')
        except:
            error = 'Username exists'
    return render_template("register_buyer.html", error=error)

@app.route("/register_seller", methods=["GET", "POST"])
def register_seller():
    error = None
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        bday = request.form['bday']
        fname = request.form['fname']
        lname = request.form['lname']
        mode = request.form['mode']
        try:
            user = {
                '_id' : uname,
                'password' : passw,
                'birthdate' : bday,
                'first_name' : fname,
                'last_name' : lname
            }
            mongo.User.insert_one(mongo_user)

            seller = {
                '_id' : 'Seller'+ str(mongo.Seller.find().count()+1),
                'parent' : uname,
                'mode' : mode,
                'rating' : 5
            }
            mongo.Seller.insert_one(seller)
            session['User'] = uname
            return redirect('/home')
        except:
            error = 'Username exists'
    return render_template("register_seller.html", error=error)


@app.route('/products', methods=["GET", "POST"])
def list_products():
    products = list(mongo.Product.find({'quantity' : {'$gt':0}}))

    for product in products:
        seller = mongo.Seller.find_one({"_id":product["seller"]})
        product['seller_rating'] = seller['rating']

    content = {}
    price = 0

    if 'Order' in session:
         order_id = session['Order']
         order = mongo.Order.find_one({"_id":order_id})
         for prod in order['content']:
            product = mongo.Product.find_one({"_id":prod['product']})
            content[prod['product']] = [product["name"], [int(prod['quantity']),round(float(product["price"]),2)]]

    if request.method == "POST":
        data = request.get_json(force=True)
        pr_nr = data.get("id")
        sel_quantity = data.get("quantity")
        selected = mongo.Product.find_one({"_id":pr_nr})

        prev_quantity = selected['quantity']
        mongo.Order.update_one(
            {'_id' : session['Order']},
            {'$push' : {'content' :
                        {'product' : pr_nr,
                         'quantity' : sel_quantity
                         }}}
        )
        mongo.Product.update_one(
            {'_id' : pr_nr },
            {'$set' : {'quantity':prev_quantity - int(sel_quantity)}}
        )
        return redirect('/products')

    for item in content.values():
        price += item[1][0] * item[1][1]
    round(price,2)
    return render_template('products.html', products = products , content = content, number = len(content), price = price)

@app.route('/confirmed',methods=["GET","POST"])
def confirm_order():
    user = session['User']
    order = session['Order']
    deliverer_count = mongo.Delivery_Person.find().count()
    dp = 'DP' + str(random.randint(1,deliverer_count))
    delivery_date = datetime.utcnow()+timedelta(days=random.randint(1,7))
    delivery = {
        '_id' : {'Delivery_Person' : dp, 'Order' : order},
        'Buyer' : user,
        'date' : delivery_date
    }
    mongo.Delivery.insert_one(delivery)
    dp = mongo.Delivery_Person.find_one({'_id' : dp})

    orders = mongo.Order.find().count() + 1
    order2 = {
        '_id' : 'Order'+str(orders),
        'date' : datetime.utcnow(),
        'payment' : 'Bank',
        'content' :[]
    }
    mongo.Order.insert_one(order2)
    mongo.Buyer.update_one(
        {'_id' : user},
        {'$push' : {'orders' : 'Order'+str(orders)}}
    )
    session['Order'] = 'Order'+str(orders)

    return render_template('confirmed.html', dp = dp, delivery_date = delivery_date, order = order)
