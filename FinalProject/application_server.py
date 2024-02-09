import os
from flask import Flask,render_template,request,session,redirect,url_for,make_response
from collections import defaultdict
import sqlite3  
  
app=Flask(__name__)
app.secret_key="54321"
@app.route('/userloginpage')
def userloginpage():
   return render_template('userloginpage.html')

@app.route('/usersignuppage')
def usersignuppage():
   return render_template('usersignuppage.html')

@app.route('/')
def index():
   return render_template('userloginpage.html')

#login
@app.route('/userlogin',methods=['POST'])
def userlogin():
    print(request.form['useremail'])
    print(request.form['userpassword'])
    connection=sqlite3.connect("coffee_store.db")
    cursor_ref=connection.cursor()
    query="select name from sqlite_master WHERE type='table' AND name='userregistrations'"
    cursor_ref.execute(query)
    first_record=cursor_ref.fetchone()
    if first_record is None:
       return render_template('userloginpage.html')
    else:
      query="SELECT useremail FROM userregistrations WHERE useremail='"+request.form['useremail']+"' AND userpassword='"+request.form['userpassword']+"';"
      cursor_ref.execute(query) 
      user=cursor_ref.fetchone()
      if user is None:
         return render_template('userloginpage.html')
      else:
         session['useremail']=request.form['useremail']
         return menu()

#register if you dont have an account
@app.route('/userregistration',methods=['POST'])
def userregistration():
     print(request.form['userfullname'])
     print(request.form['usercontact'])
     print(request.form['useremail'])
     print(request.form['userpassword'])

     connection=sqlite3.connect("coffee_store.db")  
     cursor_ref=connection.cursor()
     query="select name from sqlite_master WHERE type='table' AND name='userregistrations'"
     cursor_ref.execute(query)
     first_record=cursor_ref.fetchone()
     if first_record is None:
         connection.execute("create table userregistrations(userfullname TEXT UNIQUE,usercontact TEXT,useremail TEXT,userpassword TEXT)") 
         cursor_ref.execute("INSERT into userregistrations(userfullname,usercontact,useremail,userpassword) values(?,?,?,?)",(request.form['userfullname'],request.form['usercontact'],request.form['useremail'],request.form['userpassword']))
         print("User data inserted successfully")
         connection.commit()
         cursor_ref.close()
         connection.close()
     else:
        cursor_ref.execute("INSERT into userregistrations(userfullname,usercontact,useremail,userpassword) values(?,?,?,?)",(request.form['userfullname'],request.form['usercontact'],request.form['useremail'],request.form['userpassword']))
        print("User data inserted successfully")
        connection.commit()
        cursor_ref.close()
        connection.close()
     return render_template('userloginpage.html')

#adding items to the menu
@app.route('/additem',methods=['POST'])
def additem():
  if not os.path.exists('static'):
     os.makedirs('static')
  if request.method=='POST' and 'Image' in request.files:
     print(request.form['ItemName'])
     print(request.form['ItemCategory'])
     print(request.form['Price'])
     print(request.form['Quantity'])
     Image=request.files['Image']
     connection=sqlite3.connect("coffee_store.db")  
     cursor_ref=connection.cursor()
     query="select name from sqlite_master WHERE type='table' AND name='items'"
     cursor_ref.execute(query)
     first_record=cursor_ref.fetchone()
     if first_record is None:
         connection.execute("create table items(itemid INTEGER PRIMARY KEY AUTOINCREMENT,itemname TEXT,itemcategory TEXT,price INTEGER,qty INTEGER,imagename TEXT)") 
         cursor_ref.execute("INSERT into items(itemname,itemcategory,price,qty,imagename) values(?,?,?,?,?)",(request.form['ItemName'],request.form['ItemCategory'],request.form['Price'],request.form['Quantity'],Image.filename))
         print("data inserted successfully")
         connection.commit()
         cursor_ref.close()
         connection.close()
         Image.save('static/'+Image.filename)
         return "image uploaded successfully"
     else:
         cursor_ref.execute("INSERT into items(itemname,itemcategory,price,qty,imagename) values(?,?,?,?,?)",(request.form['ItemName'],request.form['ItemCategory'],request.form['Price'],request.form['Quantity'],Image.filename))
         print("data inserted successfully")
         connection.commit()
         cursor_ref.close()
         connection.close()
         Image.save('static/'+Image.filename)
         return "image uploaded successfully"
  else:
     return "Upload Failed"
 
#menu
@app.route('/menu')
def menu(): 
  print('useremail' in session)
  if 'useremail' in session:   
    connection=sqlite3.connect("coffee_store.db")  
    cursor_ref=connection.cursor()
    query="SELECT * FROM items;"
    cursor_ref.execute(query)
    result_records=cursor_ref.fetchall()
    print(result_records)
    record_dict=defaultdict(lambda:([],[],[],[],[],[]))
    for data in result_records:
       itemid,itemname,itemcategory,price,qty,imagename=data
       record_dict[itemcategory][0].append(itemid)
       record_dict[itemcategory][1].append(itemname)
       record_dict[itemcategory][2].append(price)
       record_dict[itemcategory][3].append(qty)
       record_dict[itemcategory][4].append(imagename)
    for data in record_dict:
      tuple_list=record_dict[data]
      for i in range(len(tuple_list[0])):
        print(tuple_list[0][i])
        print(tuple_list[1][i])
        print(tuple_list[2][i])
        print(tuple_list[3][i])
        print(tuple_list[4][i])
    cursor_ref.close()
    connection.close()
    #return render_template('menu.html',record_dict=record_dict)
    response_info=render_template('menu.html',record_dict=record_dict)
    response=make_response(response_info)
    response.headers['Cache-Control']='no-cache,no-store,must-revalidate'
    response.headers['pragma']='no-cache'
    response.headers['Expires']='0'
    return response
  else:
     return render_template('userloginpage.html')


@app.route('/userorder',methods=['POST'])
def userorder():
   if request.method=='POST':
     connection=sqlite3.connect("coffee_store.db")  
     cursor_ref=connection.cursor()
     query="select name from sqlite_master WHERE type='table' AND name='orders'"
     cursor_ref.execute(query)
     first_record=cursor_ref.fetchone()
     if first_record is None:
         connection.execute("create table orders(orderid INTEGER PRIMARY KEY AUTOINCREMENT,useremail TEXT,status TEXT)") 
         connection.commit()
         connection.execute("create table orderitems(orderid INTEGER,itemid INTEGER,userqty INTEGER,foreign key(orderid) references orders(orderid),foreign key(itemid) references items(itemid))") 
         connection.commit()
         #cursor_ref.close()
         #connection.close()
         print("tables created successfully")


     orders=request.json
     print("JSON DATA")
     print(orders)
     cursor_ref.execute("INSERT into orders(useremail,status) values(?,?)",(session.get('useremail'),'no'))    
     connection.commit()
     cursor_ref.execute("SELECT last_insert_rowid()")
     lastorderid=cursor_ref.fetchone()[0]
     userqty1=1
     for itemid1 in orders:
        cursor_ref.execute("SELECT qty FROM items WHERE itemid=?", (itemid1,))
        item_quantity = cursor_ref.fetchone()[0]
        if item_quantity >= userqty1:
          new_quantity = item_quantity - userqty1
          cursor_ref.execute("UPDATE items SET qty=? WHERE itemid=?", (new_quantity, itemid1))
          connection.commit()
          print(f"Item quantity updated for item {itemid1}. New quantity: {new_quantity}")
        else:
           return "Unable to process your order"
     for itemid1 in orders:
       cursor_ref.execute("INSERT into orderitems(orderid,itemid,userqty) values(?,?,?)",(lastorderid,itemid1,userqty1))    
       connection.commit()
       print("orderitems data inserted successfully")
     print(session.get('useremail'))
     #session.clear()
     #connection=sqlite3.connect("coffee_store.db")  
     #cursor_ref=connection.cursor()
     for itemid in orders:
       query="SELECT * FROM items WHERE itemid="+itemid+";"
       cursor_ref.execute(query)
       result_records=cursor_ref.fetchall()
       print(result_records)
     cursor_ref.close()
     connection.close()
     return "Order Placed Successfully"

@app.route('/logout')
def logout():
   session.pop('useremail',None)
   return redirect(url_for('userloginpage'))

@app.route('/managerloginpage')
def managerloginpage():
   return render_template('managerloginpage.html')

@app.route('/managerlogin',methods=['POST'])
def managerlogin():
   if request.method=='POST':
     print(request.form['manageremail'])
     print(request.form['managerpassword'])
     if request.form['manageremail']=="admin@gmail.com" and request.form['managerpassword']=="admin":
       return render_template('additemform.html')
     else:  
       return render_template('managerloginpage.html')

@app.route('/additemform')
def additemform():
    return render_template('additemform.html')

@app.route('/updateitemform')
def updateitemform():
    connection=sqlite3.connect("coffee_store.db")  
    cursor_ref=connection.cursor()
    query="SELECT * FROM items;"
    cursor_ref.execute(query)
    result_records=cursor_ref.fetchall()
    print(result_records)
    cursor_ref.close()
    connection.close()
    return render_template('updateitemform.html',result_records=result_records)


@app.route('/updateprod',methods=['POST','GET'])
def updateprod():
    itemid = request.args['itemid']
   
    itemname = request.args['itemname']
    
    itemcategory = request.args['ItemCategory']
    
    price = request.args['price']
    quantity = request.args['quantity']
    
    conn = sqlite3.connect("coffee_store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET itemname = ?,itemcategory = ?,price = ?,qty = ? WHERE itemid = ?;", (itemname, itemcategory, price, quantity, itemid))
    conn.commit()
    conn.close()
    return render_template('updateitemform.html')

    if request.method == 'POST':
        itemid = request.form['itemid']
        itemname = request.form['itemname']
        itemcategory = request.form['itemcategory']
        price = request.form['price']
        quantity = request.form['quantity']
        print(itemid)
        conn = sqlite3.connect("coffee_store.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE items
            SET itemname = ?,
                itemcategory = ?,
                price = ?,
                quantity = ?,
            WHERE itemid = ?;
        """, (itemname, itemcategory, price, quantity, itemid))
        conn.commit()
        conn.close()
    return render_template('updateitemform.html')

@app.route('/orders')
def orders():
    connection=sqlite3.connect("coffee_store.db")  
    cursor_ref=connection.cursor()
    query="SELECT * FROM items i,orders o,orderitems oi WHERE i.itemid=oi.itemid AND o.orderid=oi.orderid AND o.status='no';"
    cursor_ref.execute(query)
    columns=[description[0] for description in cursor_ref.description]
    result_records=cursor_ref.fetchall()
    print("Displaying orders")
    print(columns)
    print(result_records)
    result_dict={}
    for tp in result_records:
        dictKey=tp[6]
        dictvalue=(tp[0],tp[1],tp[2],tp[3],tp[7],tp[8])
        if dictKey in result_dict:
            result_dict[dictKey].append(dictvalue)
        else:
            result_dict[dictKey]=[dictvalue]
    print(result_dict) 
    print("Printing tuples data")
    for dictobj in result_dict:
        tup_list=result_dict[dictobj]
        print(dictobj)
        for tpobj in tup_list:
          print(tpobj[0],tpobj[1],tpobj[2],tpobj[3],tpobj[4],tpobj[5])
    cursor_ref.close()
    connection.close()
    return render_template('orders.html',record_dict=result_dict)

@app.route('/updateorder')
def updateorder():
    orderId=request.args['q'];
    print("updating table")
    print(orderId)
    conn = sqlite3.connect("coffee_store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='yes' WHERE orderid = ?;", (orderId))
    conn.commit()
    conn.close()
    return orders() 

@app.route('/managerlogout')
def managerlogout():
   return render_template('managerloginpage.html')

@app.route('/checkinventory')
def checkinventory():
    connection=sqlite3.connect("coffee_store.db")  
    cursor_ref=connection.cursor()
    query="SELECT * FROM items;"
    cursor_ref.execute(query)
    result_records=cursor_ref.fetchall()
    return render_template('inventorydetails.html',result_records=result_records)

if __name__=='__main__':
  app.run()