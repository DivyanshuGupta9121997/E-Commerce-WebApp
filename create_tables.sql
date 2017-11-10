drop database dhakadgarments$default;
create database dhakadgarments$default;
use dhakadgarments$default;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS ItemCategory;
DROP TABLE IF EXISTS Provider;
DROP TABLE IF EXISTS ProviderPhone;
DROP TABLE IF EXISTS Supplies;
DROP TABLE IF EXISTS Demand;
DROP TABLE IF EXISTS ItemDemand;
DROP TABLE IF EXISTS Itemp;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS ItemCart;
DROP TABLE IF EXISTS ItemCategory;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Feedback;
DROP TABLE IF EXISTS EmployeePhone;
DROP TABLE IF EXISTS CustomerPhone;

CREATE TABLE IF NOT EXISTS Customer(
	id int PRIMARY KEY AUTO_INCREMENT,
	username varchar(250) UNIQUE NOT NULL,
	email varchar(250) UNIQUE NOT NULL,
	first_name varchar(250) NOT NULL,
	last_name varchar(250),
	password varchar(250) NOT NULL,
	address varchar(250),
	phone_no varchar(20),
	cart_remarks varchar(2500),
	is_admin boolean CHECK( is_admin IN (1,0) ),
	is_activated char Default 'N' CHECK(is_activated IN ('Y','N'))
);

CREATE TABLE IF NOT EXISTS ItemCategory(
	id int PRIMARY KEY AUTO_INCREMENT,
	type_of_item varchar(250) NOT NULL,
	brand varchar(250),
	size varchar(250),
	quantity int DEFAULT 0 CHECK(quantity>=0),
	cost_price_pi float CHECK(cost_price_pi>=0),
	mrp float CHECK(mrp>=0),
	discount float CHECK(discount>=0),
	target_people_group varchar(250),
	photo longblob,
	UNIQUE (type_of_item, size)
);

CREATE TABLE IF NOT EXISTS Orders(
	id int PRIMARY KEY AUTO_INCREMENT,
	Orders_date_time datetime,
	dispatched_date_time datetime,
	received_date_time datetime,
	reference_phone_no varchar(20),
	reference_address varchar(2000),
	is_delivered char Default 'N' CHECK(is_delivered IN ('Y','N')),
	customer_id int,
	FOREIGN KEY (customer_id) REFERENCES Customer(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ItemOrders(
	orders_id int,
	item_category_id int,
	cost_price_pi float CHECK(cost_price_pi>=0),
	mrp float CHECK(mrp>=0),
	discount float CHECK(discount>=0),
	quantity int DEFAULT 1 CHECK(quantity>=1),
	PRIMARY KEY (orders_id,item_category_id),
	FOREIGN KEY (orders_id) REFERENCES Orders(id) ON DELETE CASCADE,
	FOREIGN KEY (item_category_id) REFERENCES ItemCategory(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ItemCart(
	customer_id int,
	item_category_id int,
	quantity int DEFAULT 1 CHECK(quantity>=1),
	PRIMARY KEY (customer_id,item_category_id),
	FOREIGN KEY (customer_id) REFERENCES Customer(id) ON DELETE CASCADE,
	FOREIGN KEY (item_category_id) REFERENCES ItemCategory(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Provider(
	id int PRIMARY KEY AUTO_INCREMENT,
	name varchar(250) NOT NULL,
	email varchar(256),
	address varchar(2500)
);

CREATE TABLE IF NOT EXISTS ProviderPhone(
	provider_id int,
	phone_no varchar(20),
	PRIMARY KEY (provider_id, phone_no),
	FOREIGN KEY (provider_id) REFERENCES Provider(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Supplies(
	provider_id int,
	item_categories_id int ,
	PRIMARY KEY (provider_id,item_categories_id),
	FOREIGN KEY (provider_id) REFERENCES Provider(id) ON DELETE CASCADE,
	FOREIGN KEY (item_categories_id) REFERENCES ItemCategory(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Demand(
	id int PRIMARY KEY AUTO_INCREMENT,
	demand_date_time datetime,
	provider_id int,
	FOREIGN KEY (provider_id) REFERENCES Provider(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ItemDemand(
	demand_id int ,
	item_categories_id int,
	PRIMARY KEY (demand_id,item_categories_id),
	FOREIGN KEY (demand_id) REFERENCES Demand(id) ON DELETE CASCADE,
	FOREIGN KEY (item_categories_id) REFERENCES ItemCategory(id) ON DELETE CASCADE
);

# Remove Item
CREATE TABLE IF NOT EXISTS Item(
	id int PRIMARY KEY AUTO_INCREMENT,
	item_categories_id int,
	date_of_purchase date,
	date_of_selling date,
	discount_offer float,
	FOREIGN KEY (item_categories_id) REFERENCES ItemCategory(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Employee(
	id int PRIMARY KEY AUTO_INCREMENT,
	name varchar(250),
	address varchar(2500),
	sex varchar(10) CHECK(type IN ('Male','Female','Other') ),
	base_salary float CHECK(base_salary > 0),
	bonus float CHECK(bonus>=0),
	decrement float DEFAULT 0.0 CHECK(decrement>=0),
	type_of_work varchar(250),
	family_background varchar(2500),
	bank_name  varchar(250),
	ac_no varchar(50),
	ifsc_code varchar(50),
	phone_no varchar(20)
);

CREATE TABLE IF NOT EXISTS Transaction(
	transaction_id int PRIMARY KEY AUTO_INCREMENT,
	order_id int,
	amount float CHECK(amount>=0),
	source_AC_no varchar(50),
	target_AC_no varchar(50),
	transaction_date_time datetime,
	FOREIGN KEY (order_id) REFERENCES Orders(id) ON DELETE CASCADE
);
CREATE TRIGGER upd_trig BEFORE UPDATE ON Transaction FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot update Transaction record';
CREATE TRIGGER del_trig BEFORE DELETE ON Transaction FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot delete Transaction record';

CREATE TABLE IF NOT EXISTS Feedback(
	id int PRIMARY KEY AUTO_INCREMENT,
	customer_id int,
	item_category_id int,
	feedback_text varchar(2500),
	vote int DEFAULT 0 CHECK(vote >= 0),
	feedback_date_time datetime,
	FOREIGN KEY (item_category_id) REFERENCES ItemCategory(id) ON DELETE CASCADE,
	FOREIGN KEY (customer_id) REFERENCES Customer(id) ON DELETE CASCADE
);



insert into Customer (username, email, first_name, last_name, password, address, phone_no, cart_remarks, is_admin) values('King','king@king.com','King','Khan',MD5('King'),'112 Lala Stree, Lajpat Nagar, Delhi', '9986568956','There are some electronics to be added in cart',0);
insert into Customer (username, email, first_name, last_name, password, address, phone_no, cart_remarks, is_admin) values('Admin','admin@admin.com','Admin','min',MD5('Admin'),'admin nagar', '9986568956','You can type your wish-list here.',1);

insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Leggies','Lyra','02',10,300.0,330.0,20,'Women');
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Cotswool','LUX','L',16,450.0,500.0,40,'Men');
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Diapers','BooBoo','S',16,40.0,50.0,10,'Kids');
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Diapers','BooBoo','L',16,450.0,500.0,10,'Kids');
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Formal-Suit','Armani','XL',15,4500.0,5000.0,300,'Men');
insert into ItemCategory (type_of_item,brand,size,quantity,cost_price_pi,mrp,discount,target_people_group) values('Designer-Saree','Shree','',100,2700.0,3000.0,200,'Women');



