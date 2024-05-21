from flask import Flask, render_template, request, redirect,session
from pymongo import MongoClient

from web3 import Web3,HTTPProvider
import json

def connectWithBlockchain():
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    web3.eth.defaultAccount=web3.eth.accounts[0]
    
    with open('../build/contracts/supplychain.json') as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3

app = Flask(__name__)
app.secret_key='1234'

dbClient = MongoClient('mongodb://localhost:27017/')
db = dbClient['fvdb']
fvcol = db['fvcol1']

# Dummy data for demonstration purposes
users = []

@app.route('/')
def index():
    return render_template('demo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Query the database to find the user
        user = fvcol.find_one({'email': email, 'password': password})

        if user:
            # Redirect to admin panel if the user is an admin
            if user['role'] == 'admin':
                session['role']='admin'
                session['email']=email
                return redirect('/admin')
            # Redirect to retailer page if the user is a retailer
            elif user['role'] == 'retailer':
                session['role']='admin'
                session['email']=email
                return redirect('/retailer')
            # Redirect to consumer page if the user is a consumer
            elif user['role'] == 'consumer':
                session['role']='admin'
                session['email']=email
                return redirect('/consumer')
        
        # Redirect back to login page if authentication fails
        return redirect('/login')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        role = request.form.get('role')

        # Check if the user already exists
        existing_user = fvcol.find_one({'email': email})
        if existing_user:
            msg = 'User already exists!'
            return render_template('register.html', msg=msg)
        else:
            # Insert user details into the database
            fvcol.insert_one({
                'email': email,
                'password': password,
                'name': name,
                'phone': phone,
                'role': role
            })
            # Redirect to login page after successful registration
            return redirect('/login')

    return render_template('register.html')

# Routes for different user roles
@app.route('/admin')
def admin():
    # Dummy data for demonstration purposes
    contract,web3=connectWithBlockchain()
    _retailers,_rproducts,_rquantity,_rprice,_roderids,_rstatuses=contract.functions.rviewOrders().call()
    print(_roderids)
    data=[]
    for i in range(len(_roderids)):
        dummy=[]
        dummy.append(_roderids[i])
        dummy.append(_retailers[i])
        dummy.append(_rproducts[i])
        dummy.append(_rquantity[i])
        dummy.append(_rprice[i])
        dummy.append(_rstatuses[i])
        data.append(dummy)
    print(data)
    return render_template('admin.html', data=data)

@app.route('/consumer')
def consumer_page():
    c1=fvcol.find({'role':'retailer'})
    data=[]
    for i in c1:
        dummy=[]
        dummy.append(i['name'])
        dummy.append(i['email'])
        data.append(dummy)
    
    data1=[]
    
    contract,web3=connectWithBlockchain()
    _consumers,_cproducts,_cquantity,_cretailer,_corderids,_cstatuses=contract.functions.cviewOrders().call()

    for i in range(len(_corderids)):
        if _consumers[i]==session['email']:
            dummy=[]
            dummy.append(_cproducts[i])
            dummy.append(_cquantity[i])
            dummy.append(_cretailer[i])
            dummy.append(_corderids[i])
            dummy.append(_cstatuses[i])
            data1.append(dummy)
    
    return render_template('consumer.html',data=data,data1=data1)

@app.route('/retailer')
def retailer_page():
    contract,web3=connectWithBlockchain()
    _retailers,_rproducts,_rquantity,_rprice,_roderids,_rstatuses=contract.functions.rviewOrders().call()
    data=[]
    for i in range(len(_roderids)):
        if _retailers[i]==session['email']:
            dummy=[]
            dummy.append(_rproducts[i])
            dummy.append(_rquantity[i])
            dummy.append(_rprice[i])
            dummy.append(_roderids[i])
            dummy.append(_rstatuses[i])
            data.append(dummy)
    
    data1=[]
    _consumers,_cproducts,_cquantity,_cretailer,_corderids,_cstatuses=contract.functions.cviewOrders().call()
    for i in range(len(_corderids)):
        if _cretailer[i]==session['email']:
            dummy=[]
            dummy.append(_cproducts[i])
            dummy.append(_cquantity[i])
            dummy.append(_cretailer[i])
            dummy.append(_corderids[i])
            dummy.append(_cstatuses[i])
            data1.append(dummy)

    return render_template('retailer.html',data=data,data1=data1)

@app.route('/demo')
def demo_page():
    return render_template('demo.html')

@app.route('/retailerreg',methods=['post'])
def retailerreg():
    product=request.form['product']
    quantity=request.form['quantity']
    totalPrice=request.form['totalPrice']
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.raddOrder(session['email'],product,quantity,totalPrice).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/retailer')

@app.route('/logout')
def logout():
    session['role']=None
    session['email']=None
    return redirect('/')

@app.route('/consumerreg',methods=['post'])
def consumerreg():
    product=request.form['product']
    quantity=request.form['quantity']
    retailer=request.form['retailer']
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.caddOrder(session['email'],product,quantity,retailer).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/consumer')

@app.route('/cupdateOrder/<id1>/<id2>')
def cupdateOrder(id1,id2):
    id1=int(id1)
    id2=int(id2)
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.cupdateOrder(id1,id2).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/retailer')

@app.route('/rupdateOrder/<id1>/<id2>')
def rupdateOrder(id1,id2):
    id1=int(id1)
    id2=int(id2)
    contract,web3=connectWithBlockchain()
    tx_hash=contract.functions.rupdateOrder(id1,id2).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9001,debug=True)