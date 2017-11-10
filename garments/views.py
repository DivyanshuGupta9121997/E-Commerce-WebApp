from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
# from .forms import CartForm
from django.db import connection,IntegrityError
from datetime import datetime

from django.core.mail import send_mail

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# from . import messager
from django.contrib.sites.shortcuts import get_current_site
# # from cryptography.fernet import Fernet
# # key='pGWp5lViKbMrOTFesoBU78ie2BZzFDVYRkWTcJJJ1vs='
# # cipher_suite = Fernet(key)
# # cipher_text = cipher_suite.encrypt("A really secret message. Not for prying eyes.")
# # plain_text = cipher_suite.decrypt(cipher_text)

# import hashlib
# # p='vishal'.encode('utf-8')
# salt='9876abcd'.encode('utf-8')
# # var2 =  hashlib.sha256(p+salt).hexdigest()


# Views Utils
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def write_file(filename,s):
    with open(filename, 'wb') as f:
        f.write(s)

def transaction_status(request):
    pass


# Views Utils --- User
#----------------------------------------------------- Authentication -----------------------------------------------------
def authenticate(username, password, is_admin):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * from Customer where username = '{}' AND password = MD5('{}') AND is_admin = {} AND is_activated='Y';".format(username, password, is_admin))
        result = dictfetchall(cursor)
    if len(result)>0:
        return result[0]
    return None

def login(request, user, is_admin):
    request.session['id'] = user['id']
    request.session['username'] = user['username']
    request.session['first_name'] = user['first_name']
    request.session['last_name'] = user['last_name']
    request.session['email'] = user['email']
    request.session['phone_no'] = user['phone_no']
    request.session['address'] = user['address']
    request.session['password'] = user['password']
    request.session['cart_remarks'] = user['cart_remarks']
    request.session['is_admin'] = user['is_admin']


def is_authenticated(request):
    if request.session.has_key('username'):
        return True
    return False

def is_authenticated_as_admin(request):
    if request.session.has_key('username') and request.session.has_key('is_admin')==True and not(request.session['is_admin']==0):
        return True
    return False

#----------------------------------------------------- Index -----------------------------------------------------


def get_best_deals(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ItemCategory ORDER BY discount/mrp DESC LIMIT 10;')
        result = dictfetchall(cursor)
    return result

def index(request):
    best_deals = get_best_deals(request)
    if is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        for item in best_deals:
            if item['photo'] is not None:
                write_file('./garments/static/garments/images/img-{}.jpg'.format(item['id']) ,  item['photo'])
        if is_authenticated_as_admin(request):
            return render(request, 'garments/index.html', {'admin':'True','cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals})
        else:
            return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals})
    else:
        return render(request, 'garments/index.html', {'error':'True', 'best_deals':best_deals})

#----------------------------------------------------- //Index -----------------------------------------------------


def logout(request):
    try:
        del request.session['username']
        del request.session['first_name']
        del request.session['last_name']
        del request.session['email']
        del request.session['address']
        del request.session['password']
        del request.session['cart_remarks']
        del request.session['id']
        del request.session['phone_no']
        del request.session['is_admin']
    except KeyError:
        best_deals = get_best_deals(request)
        return render(request, 'garments/index.html', {'best_deals':best_deals,'error':'True', 'error_message': 'You have already logged Out.' })
    return index(request)# return render(request, 'garments/index.html', {'error':'True' })



# Login View
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        is_admin = str(request.POST['is_admin'])
        user = authenticate(username=username, password=password, is_admin=is_admin)
        # return HttpResponse("SELECT * from Customer where username = '{}' AND password = MD5('{}') AND is_admin = {} AND is_activated='Y';".format(username, password, is_admin))
        if user is not None:
            login(request, user, is_admin)
            user_id = request.session['id']
            cart_items = get_cart_items(user_id)
            if user['is_admin']==0:
                return render(request, 'garments/index.html',{'cart_items':cart_items, 'first_name':user['first_name']})
            else:
                return render(request, 'garments/index.html',{'admin':'True', 'cart_items':cart_items, 'first_name':user['first_name']})
        else:
            return render(request, 'garments/index.html', {'error':'True','error_message': 'Invalid username or password. Or Please confirm email if you already signed up.' })
    return render(request, 'garments/index.html', {'error':'True', 'error_message': 'Invalid method' })

def sign_up(request, is_modify=None):
    if request.method == "POST":
        username = request.POST["username"]
        email_id = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        password = request.POST["password1"]
        password_conf = request.POST["password2"]
        address = request.POST["address"]
        phone_no = request.POST["phone_no"]
        is_admin = 0
        if not(password == password_conf):
            return render(request, 'garments/sign_up.html', {'error':'True','error_message': 'password Mismatch' })
        try:
            with connection.cursor() as cursor:
                if is_modify is None:
                    cursor.execute("INSERT INTO Customer (username, email, password, address, first_name, last_name, phone_no, is_admin, is_activated) VALUES ('{}','{}',MD5('{}'),'{}','{}','{}',{},{},'Y');".format(username, email_id, password, address, first_name, last_name, phone_no, is_admin))
                    cursor.execute("SELECT MD5('{}')".format(username))
                    r = cursor.fetchall()
                else:
                    cursor.execute("UPDATE Customer SET username='{}', email='{}', password=MD5('{}'), address='{}', first_name='{}', last_name='{}', phone_no={};".format(username, email, p, address, first_name, last_name, phone_no))
        except IntegrityError:
            return render(request, 'garments/index.html', {'error':'True', 'error_message': 'Username already registered.' })
        current_site = get_current_site(request)
        # message = 'Please confirm your account on Dhakadgarments by this link : {}'.format(current_site.domain+'/'+hashed_username)
        # messager.sendSMS(phone_no,message,'7726029635','dhakad17')
        return render(request, 'garments/index.html',{'error':'True', 'error_message': 'You need to confirm your account through the link sent to you on your email. You won\'t be able to log in otherwise.' })
    return render(request, 'garments/index.html', {'error':'True', 'error_message': 'Invalid method' })

# Sign Up view
def sign_up_page(request):
    if is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/sign_up.html', {'cart_items':cart_items, 'first_name':user['first_name'],'error_message': 'you already registered' })
    else:
        return render(request, 'garments/sign_up.html')

def post_sign_up(request, hashed_username=None):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Customer WHERE MD5(username)='{}';".format(hashed_username))
        r = dictfetchall(cursor)
        if len(r)==0:
            return render(request, 'garments/index.html', {'error':'True', 'error_message': 'Invalid method' })
        else:
            cursor.execute("UPDATE Customer SET is_activated = 'Y' WHERE MD5(username)='{}';".format(hashed_username))
            cursor.execute("SELECT * FROM Customer WHERE MD5(username)='{}';".format(hashed_username))
            user = dictfetchall(cursor)[0]
            login(request, user, 0)
    return render(request, 'garments/index.html', {'error':'True', 'error_message': 'Invalid method' })

#----------------------------------------------------- //Authentication -----------------------------------------------------






#----------------------------------------------------- ADMIN -----------------------------------------------------

def admin_home(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/admin_manage_tables.html', {'admin':'True', 'cart_items':cart_items, 'first_name': first_name})
    elif is_authenticated(request):
        return render(request, 'garments/index.html',{'cart_items':cart_items, 'first_name':user['first_name'], 'error_message':'You need to log in as Administrator for the URL you are trying to access.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })

def order_details(request, order_id, return_to):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT ic.id as item_id, ic.type_of_item as item, ic.brand as brand, ic.size as size, io.cost_price_pi as cost_price_pi, io.mrp as mrp, io.discount as discount, io.quantity as quantity, o.is_delivered as is_delivered FROM ItemOrders as io, ItemCategory as ic, Orders as o WHERE io.orders_id={} AND o.id={} AND io.item_category_id=ic.id;'.format(order_id,order_id))
            rows = cursor.fetchall()
            cursor.execute('SELECT o.is_delivered as is_delivered FROM Orders as o WHERE o.id={};'.format(order_id))
            r = cursor.fetchall()[0][0]
            column_heads = ["item_id","item","brand","size","cost_price_pi","mrp","discount","quantity","is_delivered"]
        if return_to=='V':
            return render(request, 'garments/view_table.html', {'is_delivered':r,'order_id': order_id,'show_links' : 'Order_detail','admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
        elif return_to=='D':
            return render(request, 'garments/delete_table.html', {'order_id': order_id,'show_links' : 'Order_detail','admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT ic.id as item_id, ic.type_of_item as item, ic.brand as brand, ic.size as size, io.cost_price_pi as cost_price_pi, io.mrp as mrp, io.discount as discount, io.quantity as quantity, o.is_delivered as is_delivered FROM ItemOrders as io, ItemCategory as ic, Orders as o WHERE io.orders_id={} AND o.id={} AND io.item_category_id=ic.id;'.format(order_id,order_id))
            rows = cursor.fetchall()
            cursor.execute('SELECT o.is_delivered as is_delivered FROM Orders as o WHERE o.id={};'.format(order_id))
            r = cursor.fetchall()[0][0]
            column_heads = ["item_id","item","brand","size","cost_price_pi","mrp","discount","quantity","is_delivered"]
            return render(request, 'garments/view_table.html', {'is_delivered':r,'order_id': order_id,'show_links' : 'Order_detail','cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})



def mark_delivered(request,order_id):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        received_date_time = str(datetime.now())
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Orders SET is_delivered='Y', received_date_time = {} WHERE id={};".format(order_id,received_date_time))
        return order_details(request, order_id, 'V')


def view_table(request, table_name=None, error_message=None):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        sql, column_heads, rows='', [], []
        show_links = 'N'
        TableName = ''
        if table_name == '2':
            column_heads = ['id','username','first_name','last_name','email','password','address','phone_no']
            sql = "SELECT {} FROM Customer;".format( ','.join(column_heads) )
            TableName='Customers'
        elif table_name == '1':
            column_heads = ['id','type_of_item','brand','size','quantity','cost_price_pi','mrp','discount','target_people_group']
            sql = "SELECT {} FROM ItemCategory;".format( ','.join(column_heads) )
            TableName = 'Items'
        elif table_name == '3':
            column_head=["transaction_id","order_id","username","amount","source_AC_no","target_AC_no","transaction_date_time"]
            sql = 'SELECT t.transaction_id, t.order_id, c.username, t.amount, t.source_AC_no, t.target_AC_no, t.transaction_date_time FROM Transaction as t, Orders as o, Customer as c WHERE t.order_id=o.id AND c.id=o.customer_id;'
            TableName = 'Transactions'
        elif table_name == '4':
            column_head = ["id","name","phone_no","address","sex","base_salary","bonus","decrement","type_of_work","family_background","bank_name","ac_no","ifsc_code"]
            sql = 'SELECT * FROM Employee;'
            TableName = 'Employees'
        elif table_name == '5':
            column_heads = ["id","Orders_date_time","dispatched_date_time","received_date_time","reference_address","reference_phone_no","is_delivered","username","first_name"]
            sql = 'SELECT o.id as order_id, o.orders_date_time as order_time, o.dispatched_date_time as dispatched_time, o.received_date_time as received_date, o.reference_address as address, o.reference_phone_no as phone_no,o.is_delivered as is_delivered, c.username as username, c.first_name as first_name  FROM Orders as o, Customer as c WHERE c.id=o.customer_id;'
            show_links = 'Order'
        elif table_name == 'provider':
            pass
        elif table_name == 'demands':
            pass
        elif table_name == 'feedbacks':
            pass
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        if error_message is None:
            return render(request, 'garments/view_table.html', {'Table_name':TableName, 'show_links':show_links,'admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
        else:
            return render(request, 'garments/view_table.html', {'error_message':error_message,'Table_name':TableName, 'show_links':show_links,'admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def user_order(request):
    if is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        sql, column_heads, rows='', [], []
        show_links = 'N'
        column_heads = ["id","Orders_date_time","dispatched_date_time","received_date_time","reference_address","reference_phone_no","is_delivered","username","first_name"]
        sql = 'SELECT o.id as order_id, o.orders_date_time as order_time, o.dispatched_date_time as dispatched_time, o.received_date_time as received_date, o.reference_address as address, o.reference_phone_no as phone_no,o.is_delivered as is_delivered, c.username as username, c.first_name as first_name  FROM Orders as o, Customer as c WHERE c.id=o.customer_id AND c.id={};'.format(user_id)
        show_links = 'Order'
        TableName = 'Previous Orders'
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        if is_authenticated_as_admin(request):
            return render(request, 'garments/view_table.html', {'Table_name':TableName, 'show_links':show_links,'admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
        else:
            return render(request, 'garments/view_table.html', {'Table_name':TableName, 'show_links':show_links, 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
    else :
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in to access the URL.' })


def delete_item_page(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        column_heads = ['id','type_of_item','brand','size','quantity','cost_price_pi','mrp','discount','target_people_group']
        sql = "SELECT {} FROM ItemCategory;".format( ','.join(column_heads) )
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        TableName = 'Items'
        show_links = 'Items'
        return render(request, 'garments/delete_table.html', {'Table_name':TableName, 'show_links':show_links,'admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })



def delete_item(request, item_id):
    if is_authenticated_as_admin(request):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ItemCategory WHERE id={};".format(item_id))
        return delete_item_page(request)
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def delete_order_page(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        column_heads = ["id","Orders_date_time","dispatched_date_time","received_date_time","reference_address","reference_phone_no","is_delivered","username","first_name"]
        sql = 'SELECT o.id as order_id, o.orders_date_time as order_time, o.dispatched_date_time as dispatched_time, o.received_date_time as received_date, o.reference_address as address, o.reference_phone_no as phone_no,o.is_delivered as is_delivered, c.username as username, c.first_name as first_name  FROM Orders as o, Customer as c WHERE c.id=o.customer_id;'
        show_links = 'Order'
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        TableName = 'Orders'
        return render(request, 'garments/delete_table.html', {'Table_name':TableName, 'show_links':show_links,'admin':'True', 'cart_items':cart_items, 'first_name': first_name, 'rows':rows, 'column_heads':column_heads})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def delete_order(request, order_id):
    if is_authenticated_as_admin(request):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Orders WHERE id={};".format(order_id))
        return delete_order_page(request)
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })

def insert_item_page(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/insert_item_page.html',{'admin':'True','cart_items':cart_items, 'first_name': first_name})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def modify_item_page(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        if request.method == "POST":
            # return HttpResponse('sorry')
            if not request.POST['id'].strip() == '':
                item_id = request.POST['id']
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM ItemCategory WHERE id=%s",(item_id,))
                    r = dictfetchall(cursor)[0]
                    r['admin'] = 'True'
                    r['cart_items']=cart_items
                    r['first_name']= first_name
                return render(request, 'garments/insert_item_page.html',r)
            else:
                return view_table(request,'1','You Need to give Item_id to update an item.')
        else:
            return render(request, 'garments/index.html', {'admin':'True','first_name':first_name,'error_message': 'Invalid method' })
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def modify_item(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        if request.method == "POST":
            if not request.POST['id'].strip() == '':
                item_id = request.POST['id']
                type_of_item = request.POST['type_of_item']
                brand = request.POST['brand']
                size = request.POST['size']
                quantity = request.POST['quantity']
                cost_price_pi = request.POST['cost_price_pi']
                mrp = request.POST['mrp']
                discount = request.POST['discount']
                target_people_group = request.POST['target_people_group']
                photo = request.FILES['photo'].read()
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE ItemCategory SET type_of_item=%s, brand=%s, size=%s, quantity=%s, cost_price_pi=%s, mrp=%s, discount=%s, target_people_group=%s, photo=%s WHERE id=%s",(type_of_item, brand, size, quantity, cost_price_pi, mrp, discount, target_people_group,item_id, photo))
                return view_table(request,'1')
            else:
                return view_table(request,'1','You Need to give Item_id to update an item.')
        else:
            return render(request, 'garments/index.html', {'admin':'True','first_name':first_name,'error_message': 'Invalid method' })
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def modify_order_page(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/Modify_Order_Page.html',{'admin':'True','cart_items':cart_items, 'first_name': first_name})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })


def modify_order(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        if request.method == "POST":
            Orders_date_time = str(datetime.now())
            reference_phone_no = request.POST["reference_phone_no"]
            reference_address = request.POST["reference_address"]
            customer_id = request.POST["customer_id"]
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Orders (orders_date_time, reference_phone_no, reference_address, customer_id) VALUES ('{}','{}','{}',{});".format(Orders_date_time, reference_phone_no, reference_address, customer_id))
            return view_table(request,'5')
        else:
            return render(request, 'garments/index.html', {'admin':'True','first_name':first_name,'error_message': 'Invalid method' })
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })



def delete_user_feedback(request):
    pass

def delete_item_category_feedback(request):
    pass

def apply_discount_to_item(request): # NOTE it is item
    pass

def user_profile(request):
    if is_authenticated(request):
        first_name = request.session['first_name']
        last_name = request.session['last_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        in_dict = {'cart_items':cart_items, 'first_name':first_name, 'full_name':first_name+' '+last_name}
        in_dict['first_name'] = first_name
        in_dict['last_name'] = last_name
        in_dict['username'] = request.session['username']
        in_dict['email'] = request.session['email']
        in_dict['password'] = request.session['email']
        in_dict['address'] = request.session['address']
        in_dict['phone_no'] = request.session['phone_no']
        in_dict['cart_remarks'] = request.session['cart_remarks']
        if is_authenticated_as_admin(request):
            in_dict['admin']='True'
            return render(request, 'garments/user_profile.html',in_dict)
        else:
            return render(request, 'garments/user_profile.html',in_dict)
    else:
        return render(request, 'garments/user_profile.html', {'error_message': 'You need to Log In to be able to see your profile.'})


#----------------------------------------------------- //ADMIN -----------------------------------------------------












#----------------------------------------------------- Items -----------------------------------------------------


def filter_items(request):
    sql = 'SELECT * from ItemCategory'
    display_brand_string = 'No Constraint'
    display_category_string = 'No Constraint'
    price_range = '0 Rs. - 10000 Rs. '
    if request.method == "POST":
        brands = request.POST.getlist('brand')
        categories = request.POST.getlist('category')
        price_range = request.POST['price_range']
        sort_by = request.POST.getlist('sort_by')
        if not((len(brands)==1) and (len(categories)==1)):
            sql+=' WHERE '
            if not(len(brands)==1):
                sql+=' brand IN {} '.format( '("{}")'.format('","'.join([str(b) for b in brands if not(b=='all')])) )
                display_brand_string = ', '.join([str(b) for b in brands if not(b=='all')])
            if not(len(categories)==1):
                if not(len(brands)==1):
                    sql+=' AND '
                sql+=' target_people_group IN {}'.format( '("{}")'.format('","'.join([str(c) for c in categories if not(c=='all')])) )
                display_category_string = ', '.join([str(c) for c in categories if not(c=='all')])
            MIN, MAX = [ int(s[:-4].strip()) for s in  price_range.split('-')]
            sql += ' AND mrp BETWEEN {} AND {}'.format(MIN, MAX)
        else:
            MIN, MAX = [ int(s[:-4].strip()) for s in  price_range.split('-')]
            sql += ' WHERE mrp BETWEEN {} AND {}'.format(MIN, MAX)
        if not(len(sort_by)==0):
            sql+=' ORDER BY '
            if sort_by=='Name':
                sql+=' type_of_item'
            elif sort_by=='Price':
                sql+=' mrp'
            elif sort_by=='Quantity':
                sql+=' quantity'
    sql+=';'
    # return HttpResponse(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = dictfetchall(cursor)
        return (display_brand_string, display_category_string, price_range, result)

def search_items(request):
    if request.method == "POST":
        search_string = request.POST['search_box']
        d = {'ss':search_string, }
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM ItemCategory WHERE (type_of_item LIKE "%{ss}%") OR (brand LIKE "%{ss}%");'.format(**d))
            result = dictfetchall(cursor)
            # return HttpResponse('SELECT * FROM ItemCategory WHERE (type_of_item LIKE "%{ss}%") OR (brand LIKE "%{ss}%");'.format(**d))
    return (search_string, result)

def items(request, is_search = None):
    # return search_items(request)
    # return filter_items(request)
    search_string, display_brand_string, display_category_string, price_range = None, 'No Constraint','No Constraint','0 Rs. - 10000 Rs. '
    if is_search is not None:
        search_string, item_categories = search_items(request)
    else:
        display_brand_string, display_category_string, price_range, item_categories = filter_items(request)
    for item in item_categories:
        if item['photo'] is not None:
            write_file('./garments/static/garments/images/img-{}.jpg'.format(item['id']) ,  item['photo'])
    with connection.cursor() as cursor:
        cursor.execute('SELECT DISTINCT(brand) FROM ItemCategory;')
        brands = [i['brand'] for i in dictfetchall(cursor)]
        cursor.execute('SELECT DISTINCT(target_people_group) FROM ItemCategory;')
        categories = [i['target_people_group'] for i in dictfetchall(cursor)]
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html', {'admin':'True','first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html',{'first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range })
    else:
        return render(request, 'garments/items.html', {'error': 'True', 'item_categories':item_categories, 'brands':brands, 'category':categories , "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})


def women_items(request):
    search_string, display_brand_string, display_category_string, price_range = None, 'No Constraint','Women','0 Rs. - 10000 Rs. '
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ItemCategory WHERE target_people_group IN ("Women", "women", "girls", "Girls");')
        item_categories = dictfetchall(cursor)
        cursor.execute('SELECT DISTINCT(brand) FROM ItemCategory;')
        brands = [i['brand'] for i in dictfetchall(cursor)]
        cursor.execute('SELECT DISTINCT(target_people_group) FROM ItemCategory;')
        categories = [i['target_people_group'] for i in dictfetchall(cursor)]
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html', {'admin':'True','first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html',{'first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range })
    else:
        return render(request, 'garments/items.html', {'error': 'True', 'item_categories':item_categories, 'brands':brands, 'category':categories , "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})


def kids_items(request):
    search_string, display_brand_string, display_category_string, price_range = None, 'No Constraint','Kids','0 Rs. - 10000 Rs. '
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ItemCategory WHERE target_people_group IN ("Kids", "kids");')
        item_categories = dictfetchall(cursor)
        cursor.execute('SELECT DISTINCT(brand) FROM ItemCategory;')
        brands = [i['brand'] for i in dictfetchall(cursor)]
        cursor.execute('SELECT DISTINCT(target_people_group) FROM ItemCategory;')
        categories = [i['target_people_group'] for i in dictfetchall(cursor)]
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html', {'admin':'True','first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html',{'first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range })
    else:
        return render(request, 'garments/items.html', {'error': 'True', 'item_categories':item_categories, 'brands':brands, 'category':categories , "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})

def men_items(request):
    search_string, display_brand_string, display_category_string, price_range = None, 'No Constraint','Men','0 Rs. - 10000 Rs. '
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ItemCategory WHERE target_people_group IN ("Men", "men", "boys", "Boys");')
        item_categories = dictfetchall(cursor)
        cursor.execute('SELECT DISTINCT(brand) FROM ItemCategory;')
        brands = [i['brand'] for i in dictfetchall(cursor)]
        cursor.execute('SELECT DISTINCT(target_people_group) FROM ItemCategory;')
        categories = [i['target_people_group'] for i in dictfetchall(cursor)]
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html', {'admin':'True','first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/items.html',{'first_name':first_name, 'cart_items':cart_items, 'item_categories':item_categories, 'brands':brands, 'category':categories, "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range })
    else:
        return render(request, 'garments/items.html', {'error': 'True', 'item_categories':item_categories, 'brands':brands, 'category':categories , "display_brand_string":display_brand_string, "display_category_string":display_category_string, "price_range":price_range})


#----------------------------------------------------- //Items -----------------------------------------------------




#----------------------------------------------------- DETAIL -----------------------------------------------------

def get_feedbacks_for_item_category(request,item_category_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT f.feedback_date_time ,f.id, f.feedback_text as feedback_text, f.vote as votes, c.username as username FROM Feedback as f, Customer as c WHERE f.item_category_id={} AND f.customer_id=c.id ORDER BY f.feedback_date_time;'.format(item_category_id))
        feedbacks = dictfetchall(cursor)
        return feedbacks


def item_detail(request,item_category_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from ItemCategory WHERE id={};'.format(item_category_id))
        r = dictfetchall(cursor)
        if len(r)==0:
            return render(request, 'garments/cart.html', {'error':'True','error_message': 'Trying to access a non existing URL.',})
        else:
            item = r[0]
            if item['photo'] is not None:
                write_file('./garments/static/garments/images/img-{}.jpg'.format(item['id']) ,  item['photo'])
            final_price = float(item['mrp'])-float(item['discount'])
            feedbacks = get_feedbacks_for_item_category(request, item_category_id)
            if is_authenticated(request):
                username = request.session['username']
                first_name = request.session['first_name']
                return render(request, 'garments/detail.html', {'item':item, 'final_price':final_price,'feedbacks':feedbacks ,'username':username ,'first_name':first_name})
            else:
                return render(request, 'garments/detail.html', {'error': 'True','item':item, 'final_price':final_price ,'feedbacks':feedbacks })


def add_feedback(request,item_category_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * from ItemCategory WHERE id={};'.format(item_category_id))
        r = dictfetchall(cursor)
        if len(r)==0:
            return render(request, 'garments/cart.html', {'error':'True','error_message': 'Trying to access a non existing URL.',})
        else:
            if request.method == "POST":
                if is_authenticated(request):
                    feedback = request.POST['feedback']
                    user_id = request.session['id']
                    feedback_date_time = str(datetime.now())
                    with connection.cursor() as cursor:
                        # return HttpResponse('INSERT INTO Feedback (item_category_id, customer_id, feedback_text) VALUES ({},{},"{}");'.format(item_category_id, user_id, feedback))
                        cursor.execute('INSERT INTO Feedback (item_category_id, customer_id, feedback_text,feedback_date_time) VALUES ({},{},"{}","{}");'.format(item_category_id, user_id, feedback, feedback_date_time))
                    return item_detail(request,item_category_id)
                else:
                    return item_detail(request,item_category_id)
    first_name = request.session['first_name']
    return render(request, 'garments/index.html', {'first_name':first_name,'error_message': 'Invalid method' })

#----------------------------------------------------- //DETAIL -----------------------------------------------------



#----------------------------------------------------- CART -----------------------------------------------------
def get_cart_items(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * from ItemCategory as icat, ItemCart as icart  WHERE (icart.customer_id = {} AND icat.id = icart.item_category_id);".format(user_id))
        result = dictfetchall(cursor)
    return result

def cart(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        cart_remark = request.session['cart_remarks']
        return render(request, 'garments/cart.html',{'admin':'True','first_name':first_name, 'cart_items':cart_items, 'cart_remark':cart_remark })
    if is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        cart_remark = request.session['cart_remarks']
        return render(request, 'garments/cart.html',{'first_name':first_name, 'cart_items':cart_items, 'cart_remark':cart_remark })
    else:
        return render(request, 'garments/cart.html', {'error':'True','error_message': 'You need to Log In to be able to see your cart.',})

def add_item_category_to_cart(request,item_category_id):
    if request.method == "POST":
        if is_authenticated(request):
            user_id = request.session['id']
            quantity = request.POST['quantity']
            d = {'icid':item_category_id,'cid':user_id,'qty':quantity}
            # return HttpResponse("<h1>HI!  user:{cid}, qty:{qty}, item: {icid}</h1>".format(**d))
            with connection.cursor() as cursor:
                try:
                    cursor.execute("START TRANSACTION;")
                    cursor.execute("SELECT EXISTS(SELECT * FROM ItemCategory WHERE id={icid} AND quantity >= {qty} ) as is_item_available;".format(**d))
                    r = dictfetchall(cursor)
                    # return HttpResponse("<h1>{}.</h1>".format(str(r)) )
                    cond_1 = ( r[0]['is_item_available'] > 0)
                    cursor.execute("SELECT EXISTS(SELECT * FROM ItemCart WHERE customer_id={cid} AND item_category_id={icid} ) as is_already_in_cart;".format(**d))
                    r = dictfetchall(cursor)
                    cond_2 = not (r[0]['is_already_in_cart'] > 0)
                    # return HttpResponse("<h1>{}.</h1>".format(str(r)) )
                    if cond_1 and cond_2 :
                        cursor.execute("INSERT INTO ItemCart (customer_id,item_category_id,quantity) VALUES ({cid},{icid},{qty});".format(**d))
                    elif cond_1:
                        cursor.execute("UPDATE ItemCart SET quantity=quantity+{qty} WHERE customer_id={cid} AND item_category_id={icid};".format(**d))
                    else:
                        first_name = request.session['first_name']
                        cart_items = get_cart_items(user_id)
                        cart_remark = request.session['cart_remarks']
                        return render(request, 'garments/cart.html',{'first_name':first_name, 'cart_items':cart_items, 'cart_remark':cart_remark, 'error_message': 'Sorry Item not available in sufficient quantity to add to your cart.' })
                    cursor.execute("COMMIT;")
                    return cart(request)
                except IntegrityError:
                    cursor.execute("ROLLBACK;")
                    first_name = request.session['first_name']
                    cart_items = get_cart_items(user_id)
                    cart_remark = request.session['cart_remarks']
                    return render(request, 'garments/cart.html',{'first_name':first_name, 'cart_items':cart_items, 'cart_remark':cart_remark, 'error_message': 'An error occured. Please try again later.' })
        else:
            return render(request, 'garments/index.html', {'error':'True', 'error_message': 'You can not access a cart which does not belong to you.' })
    else:
        return render(request, 'garments/index.html', {'error':'True', 'error_message': 'An error occured. Please try again later.'})


def delete_item_category_from_cart(request,item_category_id):
    if is_authenticated(request):
        user_id = request.session['id']
        with connection.cursor() as cursor:
            cursor.execute("DELETE from ItemCart where customer_id = '{}' AND item_category_id = '{}';".format(user_id, item_category_id))
        return cart(request)
    else:
        return render(request, 'garments/index.html', {'error':'True', 'error_message': 'You can not access a cart which does not belong to you.' })

#----------------------------------------------------- //CART -----------------------------------------------------





#----------------------------------------------------- BILLING -----------------------------------------------------
def billing(request):
    if is_authenticated(request):
        first_name = request.session['first_name']
        last_name = request.session['last_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        delivery_charge = 25.00
        tax_percentage = 10.00
        total = sum([c['quantity']*(c['mrp']) for c in cart_items])
        discount = sum([c['quantity']*(-c['discount']) for c in cart_items])
        tax = total*(tax_percentage/100)
        total = total+tax+discount+delivery_charge
        in_dict = {'cart_items':cart_items, 'first_name':first_name, 'full_name':first_name+' '+last_name}
        in_dict['total'] = total
        in_dict['discount'] = discount
        in_dict['tax'] = tax
        in_dict['delivery_charge'] = delivery_charge
        in_dict['user_phone_no'] = request.session['phone_no']
        in_dict['user_address'] = request.session['address']
        if is_authenticated_as_admin(request):
            in_dict['admin']='True'
            return render(request, 'garments/billing.html',in_dict)
        else:
            return render(request, 'garments/billing.html',in_dict)
    else:
        return render(request, 'garments/billing.html', {'error_message': 'You need to Log In to be able to see your bills.'})


def place_order(request, amount):# Proceed to pay
    if request.method == "POST":
        if is_authenticated(request):
            user_id = request.session['id']
            ref_phone_no = request.POST['phone_no']
            ref_address = request.POST['address']
            order_date_time = str(datetime.now())
            with connection.cursor() as cursor:
                try:
                    cursor.execute("COMMIT;")
                    cursor.execute("START TRANSACTION;")
                    cursor.execute('SELECT * FROM ItemCart as t1,ItemCategory as t2 WHERE t1.item_category_id=t2.id AND customer_id={};'.format(user_id))
                    item_in_cart = dictfetchall(cursor)
                    for item in item_in_cart:
                        item['icid'], item['qty'] = item['item_category_id'], item['quantity']
                    cond_1 = True # All items in cart are available
                    for item in item_in_cart:
                        cursor.execute("SELECT EXISTS(SELECT * FROM ItemCategory WHERE id={icid} AND quantity >= {qty} ) as is_item_available;".format(**item))
                        r = dictfetchall(cursor)
                        cond_1 = ((cond_1) and ( r[0]['is_item_available'] > 0))
                    if cond_1:
                        # make an order
                        cursor.execute('INSERT INTO Orders (orders_date_time, customer_id, reference_phone_no, reference_address) VALUES ("{}",{},{},"{}");'.format(order_date_time, user_id, ref_phone_no, ref_address))
                        # cursor.execute('Select * from Orders;')
                        # return HttpResponse("<h1> {} </h1>".format(dictfetchall(cursor)))
                        # cursor.execute('SELECT id as order_id FROM Orders WHERE NOT(Orders_date_time="{}") AND customer_id={};'.format(order_date_time, user_id))
                        cursor.execute("SELECT  LAST_INSERT_ID() AS order_id;")
                        r = dictfetchall(cursor)
                        order_id = r[0]['order_id']
                        # add all such items to ItemOrder
                        for item in item_in_cart:
                            cursor.execute("INSERT INTO ItemOrders (orders_id,item_category_id,quantity,cost_price_pi,mrp,discount) VALUES ('{}',{},{},{},{},{});".format(order_id, item['icid'], item['qty'],item['cost_price_pi'],item['mrp'],item['discount']))
                        # delete all items from ItemCart
                        for item in item_in_cart:
                            cursor.execute("DELETE from ItemCart where customer_id = {} AND item_category_id = {};".format(user_id, item['icid']))
                    else:
                        return render(request, 'garments/billing.html', {'error_message': 'Seems like somebody else ordered the item you wish to order.'})
                    cursor.execute("COMMIT;")
                    first_name = request.session['first_name']
                    cart_items = get_cart_items(user_id)
                    cart_remark = request.session['cart_remarks']
                    return render(request, 'garments/transaction.html',{'Amount':amount, 'OrderID':order_id, 'first_name':first_name, 'cart_items':cart_items } )
                except IntegrityError:
                    cursor.execute("ROLLBACK;")
                    return None
        else:
            return render(request, 'garments/index.html', {'error':'True', 'error_message': 'You can not access a bill which does not belong to you.' })
    else:
        return render(request, 'garments/index.html', {'error':'True', 'error_message': 'An error occured. Please try again later.'})




#----------------------------------------------------- //BILLING -----------------------------------------------------

def insert_item(request):
    if is_authenticated_as_admin(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)        
        if request.method == "POST":
            type_of_item = request.POST['type_of_item']
            brand = request.POST['brand']
            size = request.POST['size']
            quantity = request.POST['quantity']
            cost_price_pi = request.POST['cost_price_pi']
            mrp = request.POST['mrp']
            discount = request.POST['discount']
            target_people_group = request.POST['target_people_group'].lower()
            photo = request.FILES['photo'].read()
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO ItemCategory (type_of_item, brand, size, quantity, cost_price_pi, mrp, discount, target_people_group, photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(type_of_item, brand, size, quantity, cost_price_pi, mrp, discount, target_people_group, photo))
            return view_table(request,'1')
        else:
            return render(request, 'garments/index.html', {'first_name':first_name,'error_message': 'Invalid method' })
    elif is_authenticated(request):
        first_name = request.session['first_name']
        user_id = request.session['id']
        cart_items = get_cart_items(user_id)
        return render(request, 'garments/index.html', {'cart_items':cart_items, 'first_name': first_name, 'best_deals':best_deals,'error_message': 'Need to log in as admin to access the URL.'})
    else:
        return render(request, 'garments/index.html', {'error':'True','error_message': 'Need to log in as admin to access the URL.' })



# {% extends 'shoeshowroom/template.html' %}

# {% load staticfiles %}
# {% block content %}
    
#     <form method="post" enctype="multipart/form-data">
#         {% csrf_token %}
#         <input type="file" name="myfile">
#         <button type="submit">Upload</button>
#     </form>

#   {% if uploaded_file_url %}
#     <p>File uploaded at: <a href="{{ uploaded_file_url }}">{{ uploaded_file_url }}</a></p>
#   {% endif %}

#   <img src="data:image/png;base64,{{image}}" width="150" height="150" alt="cant find"/>
  

# {% endblock %}