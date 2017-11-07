# E-Commerce-WebApp
Dhakad Garments : An Online Garments Store

## Run in mysql>
source C:\Users\krish\Desktop\DhakadGarments\create_tables.sql


## Insert Data in Tables
### Add Customer
insert into customer (username, email, first_name, last_name, password) values('King','king@king.com','King','Khan','King');

### Add Item_category
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Leggies','Lyra','02',10,220.0,330.0,50,'Women');
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Cotswool','LUX','L',16,450.0,500.0,80,'Men');

### Add Item_category to cart

