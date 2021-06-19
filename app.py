from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
import MySQLdb.cursors
import re
from werkzeug.utils import secure_filename
import os
import urllib.request
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
flag = 0
warning=""
warningseller=""
lower=0
higher=1000000000
likedalready=""
cart_total=0

app.secret_key = 'asecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'MySQL_password24'
app.config['MYSQL_DB'] = 'ecommercelogin'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = 'Log In'
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if check_password_hash (account['password'], password):
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully'
			return redirect(url_for('profile'))
		else:
			msg = 'Incorrect username or password'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = 'Register'
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		password=generate_password_hash(password)
		email = request.form['email']
		cursor = mysql.connection.cursor()
		cursor.execute('SELECT * FROM accounts WHERE email = % s', (email, ))
		account = cursor.fetchone()
		if account:
		    msg='This email is already registered'
		    return render_template('register.html', msg = msg)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'The username is already taken'
		elif username=='' or password=='' or email=='':
			msg = 'Please fill out the form completely'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers'
		else:
			cursor.execute('INSERT INTO accounts (username, password, email) VALUES (% s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered'
	elif request.method == 'POST':
		msg = 'Please fill out the form completely'
	return render_template('register.html', msg = msg)

@app.route('/profile', methods =['GET', 'POST'])
def profile():
	global likedalready
	likedalready=""
	global warning
	warning=""
	global warningseller
	warningseller=""
	if 'username' not in session:
		return redirect(url_for('login'))
	images_present=[]
	availability=[]
	prices=[]
	tis=[]
	des=[]

	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE price>=%s AND price<=%s', (lower, higher, ))
	files_are = cursor.fetchall()
	for file in files_are:
		images_present.append(str(file['file_name'])+"."+file['file_type'])
		prices.append(file['price'])
		tis.append(file['title'])
		des.append(file['description'])
		if file['quantity']==0:
			availability.append("Sold out")
		else:
			availability.append("Available for purchase")
	return render_template('index.html', imglis=zip(images_present, availability, prices, tis, des), low=lower, high=higher)

@app.route('/seller', methods =['GET', 'POST'])
def seller():
	global likedalready
	likedalready=""
	global warning
	warning=""
	images_present=[]
	product_quans=[]
	prices=[]
	tis=[]
	des=[]
	mn=[]
	gt=[]
	gmi=[]
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE id = % s', (session['id'], ))
	files_are = cursor.fetchall()
	for file in files_are:
		images_present.append(str(file['file_name'])+"."+file['file_type'])
		product_quans.append(file['quantity'])
		prices.append(file['price'])
		tis.append(file['title'])
		des.append(file['description'])
		mn.append(file['merchantname'])
		gt.append(file['gateway'])
		gmi.append(file['gatewaymerchantid'])
	return render_template('seller.html', lis=zip(images_present, product_quans, prices, tis, des, mn, gt, gmi), warning=warningseller)

@app.route("/upload",methods=["POST","GET"])
def upload():
	global warningseller
	warningseller=""
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	now = datetime.now()
	nowt=now.strftime("%m_%d_%Y_%H_%M_%S_%f")
	if request.method == 'POST':
		file = request.files.get('files')
		qnt = request.form['qnt']
		price = request.form['price']
		title = request.form['title']
		mn = request.form['merchantname']
		gt = request.form['gateway']
		gmi = request.form['gatewaymerid']
		description = request.form['description']
		if file and allowed_file(file.filename):
			ftype=file.filename.rsplit('.', 1)[1].lower()
			cur.execute("INSERT INTO images (id, uploaded_on, file_type, quantity, price, title, description, merchantname, gateway, gatewaymerchantid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",[session['id'], nowt, ftype, qnt, price, title, description, mn, gt, gmi])
			mysql.connection.commit()
			cur.close()
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM images WHERE id = % s AND uploaded_on = %s', (session['id'], nowt, ))
			file_is = cursor.fetchone()
			if file_is:
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(file_is['file_name'])+"."+ftype))
			else:
				flash('File could not be uploaded')
		flash('File successfully uploaded')
	return redirect(url_for('seller'))

@app.route('/delsel', methods =['GET', 'POST'])
def delsel():
	global warningseller
	warningseller=""
	filetolike=request.form['remove_from_seller']
	filetodelid=int(filetolike.rsplit('.', 1)[0])
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("DELETE FROM images WHERE file_name=%s AND id=%s",[filetodelid, session['id']])
	mysql.connection.commit()
	cur.close()
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("DELETE FROM cart WHERE file_address=%s",[filetolike])
	mysql.connection.commit()
	cur.close()
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("DELETE FROM liked WHERE file_address=%s",[filetolike])
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('seller'))

@app.route('/alterqtn', methods =['GET', 'POST'])
def alterqtn():
	filetocart=request.form['alter_qtn']
	fileid=int(filetocart.rsplit('.', 1)[0])
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE file_name = % s', (fileid, ))
	files_are = cursor.fetchone()
	qnt=files_are['quantity']
	cursor.close()
	return render_template('update.html', qnt=qnt, fileid=fileid, field="quantity")

@app.route('/updatequan', methods =['GET', 'POST'])
def updatequan():
	qnt=request.form['qnt']
	fileid=request.form['update']
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("UPDATE images SET quantity=%s WHERE file_name=%s",[qnt, fileid])
	mysql.connection.commit()
	cur.close()
	global warningseller
	warningseller="quantity updated"
	return redirect(url_for('seller'))

@app.route('/alterprice', methods =['GET', 'POST'])
def alterprice():
	filetocart=request.form['alter_price']
	fileid=int(filetocart.rsplit('.', 1)[0])
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE file_name = % s', (fileid, ))
	files_are = cursor.fetchone()
	qnt=files_are['price']
	cursor.close()
	return render_template('update.html', qnt=qnt, fileid=fileid, field="price")

@app.route('/updateprice', methods =['GET', 'POST'])
def updateprice():
	qnt=request.form['price']
	fileid=request.form['updatep']
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("UPDATE images SET price=%s WHERE file_name=%s",[qnt, fileid])
	mysql.connection.commit()
	cur.close()
	fil=str(fileid)
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("UPDATE cart SET price=%s WHERE file_address=%s OR file_address=%s OR file_address=%s OR file_address=%s",[qnt, fil+".png", fil+".jpg", fil+".jpeg", fil+".gif"])
	mysql.connection.commit()
	cur.close()
	global warningseller
	warningseller="price updated"
	return redirect(url_for('seller'))

#cart
@app.route('/others', methods =['GET', 'POST'])
def others():
	global cart_total
	cart_total=0
	global likedalready
	likedalready=""
	global warningseller
	warningseller=""
	in_cart=[]
	prices=[]
	titles=[]
	descs=[]
	mn=[]
	gt=[]
	gmi=[]
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM cart WHERE id = % s', (session['id'], ))
	files_are = cursor.fetchall()
	for file in files_are:
		in_cart.append(file['file_address'])
		prices.append(file['price'])
		cart_total+=file['price']
		titles.append(file['title'])
		descs.append(file['description'])
		mn.append(file['merchantname'])
		gt.append(file['gateway'])
		gmi.append(file['gatewaymerchantid'])
	cursor.close()
	# if flag==1:
	# 	flag=0
	# 	return flash('Product out of stock... Can not add to cart')
	return render_template('others.html', imglis=zip(in_cart, prices, titles, descs, mn, gt, gmi), msg=warning, bill=cart_total)

# app.route('/flash/<message>')
# def flash(message):
#   return render_template('flash.html', msg=message)

@app.route('/putcart', methods =['GET', 'POST'])
def putcart():
	filetocart=request.form['add_to_cart']
	fileid=int(filetocart.rsplit('.', 1)[0])
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE file_name = % s', (fileid, ))
	files_are = cursor.fetchone()
	qnt=files_are['quantity']
	price=files_are['price']
	tis=files_are['title']
	des=files_are['description']
	mn=files_are['merchantname']
	gt=files_are['gateway']
	gmi=files_are['gatewaymerchantid']
	qnt=max(qnt, 0)
	cursor.close()
	if qnt==0:
		# flag=1
		global warning
		warning="product out of stock... Could not add to cart"
		return redirect(url_for('others'))
		
	else:
		cursor = mysql.connection.cursor()
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("UPDATE images SET quantity=%s WHERE file_name=%s",[qnt-1, fileid])
		mysql.connection.commit()
		cur.close()
		cursor = mysql.connection.cursor()
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("INSERT INTO cart (file_address, id, price, title, description, merchantname, gateway, gatewaymerchantid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",[filetocart, session['id'], price, tis, des, mn, gt, gmi])
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('others'))

@app.route('/remcart', methods =['GET', 'POST'])
def remcart():
	global warning
	warning=""
	filetolike=request.form['remove_from_cart']
	fileid=int(filetolike.rsplit('.', 1)[0])
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE file_name = % s', (fileid, ))
	files_are = cursor.fetchone()
	qnt=files_are['quantity']
	cursor.close()
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("UPDATE images SET quantity=%s WHERE file_name=%s",[qnt+1, fileid])
	mysql.connection.commit()
	cur.close()
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("DELETE FROM cart WHERE file_address=%s AND id=%s",[filetolike, session['id']])
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('others'))

@app.route('/liked', methods =['GET', 'POST'])
def liked():
	global warningseller
	warningseller=""
	global warning
	warning=""
	in_like=[]
	prices=[]
	tis=[]
	des=[]
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM liked WHERE id = % s', (session['id'], ))
	files_are = cursor.fetchall()
	for file in files_are:
		in_like.append(file['file_address'])
		tis.append(file['title'])
		des.append(file['description'])
		prices.append(file['price'])
	return render_template('liked.html', imglis=zip(in_like, prices, tis, des), msg=likedalready)

@app.route('/putlike', methods =['GET', 'POST'])
def putlike():
	fil=request.form['add_to_likes']
	fileid=int(fil.rsplit('.', 1)[0])
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM images WHERE file_name = % s', (fileid, ))
	files_are = cursor.fetchone()
	price=files_are['price']
	tis=files_are['title']
	des=files_are['description']
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM liked WHERE file_address = % s AND id=%s', (fil, session['id']))
	files_are = cursor.fetchone()
	if files_are:
		global likedalready
		likedalready='Product already in your likes'
		return redirect(url_for('liked'))

	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("INSERT INTO liked (file_address, id, title, description, price) VALUES (%s, %s, %s, %s, %s)",[fil, session['id'], tis, des, price])
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('liked'))

@app.route('/dislike', methods =['GET', 'POST'])
def dislike():
	global likedalready
	likedalready=""
	filetolike=request.form['remove_from_likes']
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("DELETE FROM liked WHERE file_address=%s AND id=%s",[filetolike, session['id']])
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('liked'))

@app.route('/userupdate', methods =['GET', 'POST'])
def userupdate():
	return render_template('enterpassword.html', msg='')

@app.route('/updateuser', methods =['GET', 'POST'])
def updateuser():
	password=request.form['pass']
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
	account = cursor.fetchone()
	if(check_password_hash(account['password'], password)):
		return render_template('userupdate.html', msg='', add=account['address'], zip=account['zip'], zip2=account['zip2'])
	else:
		return render_template('enterpassword.html', msg='Wrong Password! Try again')
	
@app.route('/infoupdatepage', methods=['GET', 'POST'])
def infoupdatepage():
	button=request.form['update']
	if button=="addupd":
		add=request.form['add']
		zip=request.form['zip']
		zip2=request.form['zip2']
		cursor = mysql.connection.cursor()
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("UPDATE accounts SET address=%s, zip=%s, zip2=%s WHERE id=%s",[add, zip, zip2, session['id']])
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('checkout'))
	name=request.form['name']
	passw=request.form['pass']
	passw=generate_password_hash(passw)
	if(passw!=''):
		cursor = mysql.connection.cursor()
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("UPDATE accounts SET password=%s WHERE id=%s",[passw, session['id']])
		mysql.connection.commit()
		cur.close()
	add=request.form['add']
	zip=request.form['zip']
	zip2=request.form['zip2']
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("UPDATE accounts SET address=%s, zip=%s, zip2=%s WHERE id=%s",[add, zip, zip2, session['id']])
	mysql.connection.commit()
	cur.close()
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("UPDATE accounts SET username=%s WHERE id=%s",[name, session['id']])
	mysql.connection.commit()
	cur.close()
	return render_template('userupdate.html', msg='Information Updated Successfully', add=add, zip=zip, zip2=zip2)


@app.route('/about', methods =['GET', 'POST'])
def about():
	return render_template('about.html')

@app.route('/pricerange', methods =['GET', 'POST'])
def pricerange():
	global lower
	lower=request.form['from1']
	global higher
	higher=request.form['to1']
	return redirect(url_for('profile'))

@app.route('/pricerangeall', methods =['GET', 'POST'])
def pricerangeall():
	global lower
	lower=0
	global higher
	higher=1000000000
	return redirect(url_for('profile'))

@app.route('/search', methods =['GET', 'POST'])
def search():
	global warning
	warning=""
	global warningseller
	warningseller=""
	images_present=[]
	availability=[]
	prices=[]
	tis=[]
	des=[]
	searchwords=request.form['search'].split()
	allwords=''
	if searchwords==[]:
		redirect(url_for('profile'))
	# allwords+=searchwords[0]
	# for word in searchwords:
	# 	allwords+=' AND '
	# 	allwords+=word
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	if 1:
		i=searchwords[0]
		temp='%'
		temp+=i
		temp+='%'
		cursor.execute('SELECT * FROM images WHERE price>=%s AND price<=%s AND title LIKE %s', (lower, higher, temp))
		files_are = cursor.fetchall()
		for file in files_are:
			images_present.append(str(file['file_name'])+"."+file['file_type'])
			prices.append(file['price'])
			tis.append(file['title'])
			des.append(file['description'])
			if file['quantity']==0:
				availability.append("Sold out")
			else:
				availability.append("Available for purchase")
		flag1=0
		finlis=[]
		av=[]
		pr=[]
		ti=[]
		de=[]
		index=-1
		for sentence in tis:
			index+=1
			for word in searchwords:
				word = word.upper()
				sentence1 = sentence.upper()
				lis = sentence1.split()
				if lis.count(word) ==0:
					flag1=1
					break
			print(searchwords)
			print(sentence)
			if flag1==1:
				flag=0
				continue
			finlis.append(images_present[index])
			av.append(availability[index])
			pr.append(prices[index])
			ti.append(sentence)
			de.append(des[index])
	if len(finlis)==0:
		redirect(url_for('profile'))
	return render_template('index.html', imglis=zip(finlis, av, pr, ti, de), low=lower, high=higher)

@app.route('/checkout', methods =['GET', 'POST'])
def checkout():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM cart WHERE id = % s', (session['id'], ))
	cartelem = cursor.fetchall()
	if not cartelem:
		global warning
		warning='Your cart is empty'
		return redirect(url_for('others'))
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
	cartelem2 = cursor.fetchone()
	if cartelem2['zip']==0 or cartelem2['zip2']=='':
		return render_template('userupdate.html', msg='Update your address')
	cartlis=[]
	in_cart=[]
	prices=[]
	titles=[]
	descs=[]
	mn=[]
	gt=[]
	gmi=[]
	for file in cartelem:
		in_cart.append(file['file_address'])
		prices.append(file['price'])
		titles.append(file['title'])
		descs.append(file['description'])
		mn.append(file['merchantname'])
		gt.append(file['gateway'])
		gmi.append(file['gatewaymerchantid'])
	merchant=gmi[0]
	for g in gmi:
		print(g)
		print(merchant)
		if merchant!=g:
			print('here')
			warning="More than one merchants in cart... Can not purchase items together"
			return redirect(url_for('others'))
	cursor = mysql.connection.cursor()
	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("DELETE FROM cart WHERE id=%s",[session['id']])
	mysql.connection.commit()
	cur.close()
	return render_template('checkout.html', bill=cart_total, imglis=zip(in_cart, prices, titles, descs), mn=mn[0], gt=gt[0], gmi=gmi[0])

# @app.route('/display/<filename>')
# def display_image(filename):
# 	#print('display_image filename: ' + filename)
# 	return redirect(url_for('static', filename='uploads/' + filename), code=301)
