'''                             INVENTORY MANAGER
About:A Simple inventory mangement system to store stock details like 
incoming of stocks and outgoing of stocks along with displaying entered 
quantity and also includes stores bills of orders confirmed

Date:1/10/2024

Features:
1.Add stocks details like price,quantity,name of product 
2.Update stock details like price and quantity of a existing stock
3.Delete an existing stock
4.Storing customer info
5.login page for basic security 
'''
from flask import*
import sqlite3
app=Flask(__name__)
app.config['MY_SECRET_USERNAME']='Denzil'
app.config['MY_SECRET_PASSWORD']='1234'
connect=sqlite3.connect('stock.db')
connect.execute('CREATE TABLE IF NOT EXISTS stocks(id INTEGER PRIMARY KEY AUTOINCREMENT,prod TEXT,rate FLOAT,quan INTEGER)') 
def get_db():
    conn=sqlite3.connect('stock.db')
    conn.row_factory=sqlite3.Row
    return conn
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if username==app.config['MY_SECRET_USERNAME']:
            if password==app.config['MY_SECRET_PASSWORD']:
                return redirect(url_for('index'))
        else:
            return render_template('landingpage.html')
    else:
        return render_template('login.html')
@app.route('/index')
def index():
    return render_template('Homepage.html')
@app.route('/add',methods=['GET','POST'])
def add():
    if request.method=='POST':
        product=request.form['product']
        rate=request.form['rate']
        quantity=request.form['quantity']
        with get_db()as con:
            curr=con.cursor()
            curr.execute('INSERT INTO stocks(prod,rate,quan)VALUES(?,?,?)',(product,rate,quantity))
            con.commit()
            return redirect(url_for('index'))
    else:
        return render_template('add.html')
@app.route('/view')
def view():
    with get_db()as con:
        curr=con.cursor()
        curr.execute('SELECT * FROM stocks')
        data=curr.fetchall()
        return render_template('view.html',data=data)
@app.route('/bill',methods=['POST'])
def bill():
    selected_ids=request.form.getlist('selected_stocks')
    con=get_db()
    placeholder=','.join(['?']*len(selected_ids))
    query=f'SELECT * FROM stocks WHERE id IN({placeholder})'
    selected_stocks=con.execute(query,selected_ids).fetchall()
    total=0
    detailed_stock=[]
    for stock in selected_stocks:
        desired_qty_str=request.form.get(f"quantity_{stock['id']}",'0')
        try:
            desired_qty=int(desired_qty_str)
            if desired_qty<0:
                desired_qty=0
        except ValueError:
            desired_qty=0
        new_quantity=stock['quan']-desired_qty
        con.execute('UPDATE stocks SET quan=? WHERE id=?',(new_quantity,stock['id']))
        con.commit()
        if desired_qty>stock['quan']:
            desired_qty=stock['quan']
        subtotal=stock['rate']*desired_qty
        total+=subtotal
        if desired_qty>0:
            detailed_stock.append({
                'name':stock['prod'],
                'rate':stock['rate'],
                'desired_qty':desired_qty,
                'subtotal':subtotal
            })
    if not detailed_stock:
        return redirect(url_for('view'))
    return render_template('billpage.html',stocks=detailed_stock,total=total)
@app.route('/update_stock',methods=['GET','POST'])
def update_stock():
    con=get_db()
    data=con.execute('SELECT * FROM stocks').fetchall()
    if request.method=='POST':
        selected_id=request.form.getlist('selected')
        con=get_db()
        placeholder=','.join(['?']*len(selected_id))
        query=f'SELECT * FROM stocks WHERE id IN({placeholder})'
        selected_stocks=con.execute(query,selected_id).fetchall()
        for stock in selected_stocks:
            update_qty_str=request.form.get(f'quantity{stock['id']}','0')
            try:
                update_qty=int(update_qty_str)
                if update_qty<0:
                    update_qty=0
            except ValueError:
                update_qty=0
            updated_qty=stock['quan']+update_qty
            con.execute('UPDATE stocks SET quan=? WHERE id=?',(updated_qty,stock['id']))
            con.commit()
        return redirect(url_for('index'))
    else:
        return render_template('updatepage.html',data=data)
@app.route('/delete',methods=['GET','POST'])
def delete():
    con=get_db()
    data=con.execute('SELECT * FROM stocks').fetchall()
    if request.method=='POST':
        product=request.form['product']
        con.execute('DELETE FROM stocks WHERE prod=?',(product,))
        con.commit()
        return redirect(url_for('index'))
    else:
        return render_template('deletepage.html',data=data) 
if __name__=='__main__':
    app.run(debug=True)