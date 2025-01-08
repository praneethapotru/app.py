from flask import Flask,render_template,request,flash,url_for,session,redirect
from otp import genotp
from cmail import sendmail 
import mysql.connector
from adminmail import adminsendmail
from adminotp import adotp
import os
import razorpay
RAZORPAY_KEY_ID='rzp_test_Ie8LX3TQLG3o2l'
RAZORPAY_KEY_SECRET='8y6OP9TBCtLfkJBeHHxchuvb'
client=razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))
from itemid import itemidotp
mydb=mysql.connector.connect(host='localhost',user='root',password='praneeth@123',db='ecommerce')
app=Flask(__name__)
app.secret_key='12345678'
@app.route('/')
def base():
    return render_template('welcome.html')
@app.route('/homepage')
def home1():
    return render_template('homepage.html')
@app.route('/reg',methods=['GET','POST'])
def register():
    if request.method=="POST":
        username=request.form['username']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select email from signup')
        data=cursor.fetchall()  
        cursor.execute('select mobile from signup')
        edata=cursor.fetchall()
        if(mobile,)in edata:
            flash('User already exist')
            return render_template('register.html')
        if(email,)in data:
            flash('Email address already exists')
            return render_template('register.html')
        cursor.close() 
        otp=genotp()
        subject='thanks for registering to the application'
        body=f'use this otp to register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,username=username,mobile=mobile,email=email,address=address,password=password)
    else:
        return render_template('register.html')
@app.route('/otp/<otp>/<username>/<mobile>/<email>/<address>/<password>',methods=['GET','POST'])
def otp(otp,username,mobile,email,address,password):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mydb.cursor()
            lst=[username,mobile,email,address,password]
            query='insert into signup values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,username=username,mobile=mobile,email=email,address=address,password=password)
    return render_template('otp.html',otp=otp,username=username,mobile=mobile,email=email,address=address,password=password)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from signup where username=%s and password=%s',[username,password])
        count=cursor.fetchone()
        print(count)
        if count==0:
            flash('Invalid email or password')
            return render_template('login.html')
        else:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for('home1'))
    return render_template('login.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('home1'))
    else:
        flash('already logged out!')
@app.route('/adminsignup',methods=['GET','POST'])
def adminsignup():
    if request.method=='POST':
        name=request.form['username']
        mobile=request.form['mobile']
        email=request.form['email']
        password=request.form['password']
        
        cursor=mydb.cursor()
        cursor.execute('select email from adminsignup')
        data=cursor.fetchall()
        cursor.execute('select mobile from adminsignup')
        edata=cursor.fetchall()
        #print(data)
        if (mobile, ) in edata:
            flash('User already exisit')
            return render_template('adminsignup.html')
        if (email, ) in data:
            flash('Email id already exisit')
            return render_template('adminsignup.html')
        cursor.close()
        adminotp=adotp()
        subject='thanks for registering to the application'
        body=f'use this adminotp to register {adminotp}'
        sendmail(email,subject,body)
        print(name,adminotp)
        return render_template('adminotp.html',adminotp=adminotp,name=name,mobile=mobile,email=email,password=password)
    else:
        return render_template('adminsignup.html')    
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        cursor=mydb.cursor()
        cursor.execute('select count(*) from adminsignup where email=%s and password=%s',[email,password])
        count=cursor.fetchone()[0]
        print(count)
        if count==0:
            flash('Invalid email or password')
            return render_template('adminlogin.html')
        else:
            session['admin']=email
            return redirect(url_for('adminhome'))
    return render_template('adminlogin.html')
@app.route('/adminhome')
def adminhome():
    if session.get('admin'):
        return render_template('admindashboard.html')
    else:
        #flash('login first')
        return redirect(url_for('adminlogin'))
@app.route('/adminlogout')
def adminlogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('adminlogin'))
    else:
        flash('already logged out!')
        return redirect(url_for('adminlogin'))
@app.route('/adminotp/<adminotp>/<name>/<mobile>/<email>/<password>',methods=['GET','POST'])
def adminotp(adminotp,name,mobile,email,password):
    if request.method=='POST':
        uotp=request.form['otp']
        if adminotp==uotp:
            cursor=mydb.cursor()
            lst=[name,mobile,email,password]
            query='insert into adminsignup values(%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mydb.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('adminlogin'))
        else:
            flash('Wrong otp')
            return render_template('adminotp.html',adminotp=adminotp,name=name,mobile=mobile,email=email,password=password)     
@app.route('/additems', methods=['GET', 'POST'])
def additems():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        quantity = request.form['qty']
        category = request.form['category']
        price = request.form['price']
        image = request.files['image']
        
        # Validate category
        valid_categories = ['electronics', 'grocery', 'fashion', 'home']
        if category not in valid_categories:
            flash('Invalid Category. Please select a valid option.')
            return render_template('items.html')
        
        # Validate price and quantity
        try:
            
            price = int(price)  # Convert price to float
            quantity = int(quantity)  # Convert quantity to int
        except ValueError:
            flash('Invalid price or quantity')
            return render_template('items.html')
        
        # Generate unique item ID
        idotp = itemidotp()
        filename = idotp + '.jpg'
        
        try:
            # Insert data into the database
            cursor = mydb.cursor()
            cursor.execute('INSERT INTO additems(itemid, name, description, qty, category, price) VALUES(%s, %s, %s, %s, %s, %s)',
                           [idotp, name, description, quantity, category, price])
            mydb.commit()

            # Save the image to the static folder
            path = os.path.dirname(os.path.abspath(__file__))
            static_path = os.path.join(path, 'static')
            image.save(os.path.join(static_path, filename))

            flash('Item added successfully!')
        except Exception as e:
            print(f"Error adding item: {e}")
            flash('Error adding item. Please try again.')

        return render_template('items.html')

    return render_template('items.html')

@app.route('/dashboard')
def dashboardpage():
    cursor=mydb.cursor()
    cursor.execute('select *from additems')
    items=cursor.fetchall()
    print(items)
    return render_template('dashboard.html',items=items)
@app.route('/status')
def status():
    cursor=mydb.cursor()
    cursor.execute('select * from additems')
    items=cursor.fetchall()
    return render_template('status.html',items=items)
@app.route('/updateproducts/<itemid>',methods=['GET','POST'])
def updateproducts(itemid):
    if session.get('admin'):
        print(itemid)
        cursor=mydb.cursor()
        cursor.execute('select name,description,qty,category,price from additems where itemid=%s',[itemid])
        items=cursor.fetchone()
        print(items)
        cursor.close()
        if request.method=="POST":
           name=request.form['name']
           description=request.form['description']
           quantity=request.form['qty']
           category=request.form['category']
           price=request.form['price']
           cursor=mydb.cursor()
           cursor.execute('update additems set name=%s,description=%s,qty=%s,category=%s,price=%s where itemid=%s',[name,description,quantity,category,price,itemid])
           mydb.commit()
           cursor.close()
           return redirect(url_for('adminhome'))
        return render_template('updateproducts.html',items=items)
    else:
        return redirect(url_for('adminlogin'))
@app.route('/deleteproducts/<itemid>')
def deleteproducts(itemid):
    cursor=mydb.cursor()
    cursor.execute('delete from additems where itemid=%s',[itemid])
    mydb.commit()
    cursor.close()
    path=os.path.dirname(os.path.abspath(__file__))
    static_path=os.path.join(path,'static')
    filename=itemid+'.jpg'
    os.remove(os.path.join(static_path,filename))
    flash('deleted')
    return redirect(url_for('status'))
@app.route('/index')
def index():
    cursor=mydb.cursor(buffered=True)
    cursor.execute('SELECT itemid,name,qty,category,price FROM additems')
    item_data=cursor.fetchall()
    print(item_data)
    return render_template('index.html',item_data=item_data)
@app.route('/addcart/<itemid>/<name>/<category>/<price>/<quantity>',methods=['GET','POST'])
def addcart(itemid,name,category,price,quantity):
    if not session.get('user'):
        return redirect(url_for('login'))
    else:
        print(session)
        if itemid not in session.get(session['user'],{}):
            if session.get(session['user']) is None:
                session[session['user']]={}
            session[session['user']][itemid]=[name,price,1,f'{itemid}.jpg',category]
            session.modified=True
            flash(f'{name} added to cart')
            return '<h2> add to cart </h2>'
        session[session['user']][itemid][2]+=1
        session.modified=True
        flash(f'{name} quantity increased in the cart')
        return redirect(url_for('addedsuccess'))
@app.route('/addedsucess')
def addedsuccess():
    return render_template('addedsuccess.html')

@app.route('/viewcart')
def viewcart():
    if not session.get('user'):
        return redirect(url_for('login'))
    user_cart=session.get(session.get('user'))#retrive the cart items from the session
    if not user_cart:
        items='empty'
    else:
        items=user_cart   #fetch the items from the session
    if items=='empty':
        return '<h3> Your cart is empty</h3>'
    return render_template('cart.html',items=items)
@app.route('/cartpop/<itemid>')
def cartpop(itemid):
    if session.get('user'):
        #print(session)
        session[session.get('user')].pop(itemid)
        session.modified=True
        flash('item removed')
        #print(session)
        return redirect(url_for('viewcart'))
    else:
        return redirect(url_for('login'))
@app.route('/dis/<itemid>')
def dis(itemid):
    cursor=mydb.cursor()
    cursor.execute('select *from additems where itemid=%s',[itemid])
    items=cursor.fetchone()
    return render_template('discription.html',items=items)
@app.route('/category/<category>',methods=['GET','POST'])
def category(category):
    if session.get('user'):
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select *from additems where category=%s',[category])
        data=cursor.fetchall()
        cursor.close()
        return render_template('categories.html',data=data)
    else:
        return redirect(url_for('login'))
#for payment-->id,name,price
@app.route('/pay/<itemid>/<name>/<price>',methods=['GET','POST'])
def pay(itemid,name,price):
    try:
        # Get the quantity from the form
        qty=request.form['qyt']
        qty=int(qty)
        # Calculate the total amount in paise (price is in rupees)
        total_price = price *qty
        print(price)
        total_price=int(total_price)
        print(type(total_price))
        #Ensure integer multiplication

        print(f'creating payment for item:{itemid},name:{name},Total price:{total_price}')

        #create Razopay order
        order=client.order.create({
            'amount':total_price*100,
            'currency':'INR',
            'payment_capture':'1'
        })
        print(f"Order created:{order}")
        print(itemid)
        return render_template('pay.html',order=order,itemid=itemid,name=name,price=total_price,qty=qty)
    except Exception as e:
        #Log the error and return a 400 response
        print(f"Error creating order:{str(e)}")
        return str(e), 400
@app.route('/success',methods=['POST'])
def success():
    if session.get('user'):
       payment_id=request.form.get('razorpay_payment_id') 
       order_id=request.form.get('razorpay_order_id')
       signature=request.form.get('razorpay_signature')
       name=request.form.get('name')
       itemid=request.form.get('itemid')
       total_price=request.form.get('total_price')
       total_price=int(total_price)
       qty=request.form.get('qyt')
       #Verification process
       print(itemid)
       params_dict={
           'razorpay_order_id':order_id,
           'razorpay_payment_id':payment_id,
           'razorpay_signature':signature
       }
       try:
           client.utility.verify_payment_signature(params_dict)
           cursor=mydb.cursor(buffered=True)
           cursor.execute('insert into orders(itemid,item_name,qty,total_price,user) values(%s,%s,%s,%s,%s)',[itemid,name,qty,total_price,session.get('user')])
           mydb.commit()
           cursor.close()
           flash('Order placed sucessfully')
           return redirect(url_for('orders'))
       except razorpay.errors.SignatureVerificationError:
           return 'Payment verification failed!',400
    else:
        return redirect(url_for('login'))


@app.route('/orders')
def orders():
    if session.get('user'):
        user=session.get('user')
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select *from orders where user=%s',[user])
        data=cursor.fetchall()
        print(data)
        cursor.close()
        return render_template('orderdisplay.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        message=request.form['message']
        cursor=mydb.cursor()
        cursor.execute("insert into contacts(name, email, meassgae) values (%s, %s, %s)", (name, email, message))
        mydb.commit()
        cursor.close()
        flash("your message has been sent successfully!")
        return redirect(url_for('home1'))
    return render_template('contact.html')
@app.route('/search',methods=['GET','POST'])
def search():
    if request.method=='POST':
        name=request.form['search']
        cursor=mydb.cursor()
        cursor.execute('select * from additems where name=%s',[name])
        data=cursor.fetchall()
        return render_template('dashboard.html',items=data)
if __name__ == '__main__':
    app.run(debug=True)