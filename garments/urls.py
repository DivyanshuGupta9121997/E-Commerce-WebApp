from django.conf.urls import url
from . import views

app_name = 'garments'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^billing$', views.billing, name='billing'),
    url(r'^cart$', views.cart, name='cart'),
    url(r'^items$', views.items, name='items'),
    url(r'^items/(?P<is_search>[1])$', views.items, name='items1'),
    url(r'^login_user$', views.login_user, name='login_user'),
    url(r'^logout_user$', views.logout, name='logout_user'),
    url(r'^remove_from_cart/(?P<item_category_id>[0-9]+)$', views.delete_item_category_from_cart, name='remove_from_cart'),
    url(r'^add_to_cart/(?P<item_category_id>[0-9]+)$', views.add_item_category_to_cart, name='add_to_cart'),
    url(r'^place_order/(?P<amount>[0-9\.]+)$', views.place_order, name='place_order'),
    url(r'^admin_home$', views.admin_home, name='admin_home'),
    url(r'^user_profile$', views.user_profile, name='user_profile'),
    url(r'^sign_up$', views.sign_up, name='sign_up'),
    url(r'^sign_up/(?P<is_modify>[0-9]+)$', views.sign_up, name='sign_up'),    
    url(r'^sign_up_page$', views.sign_up_page, name='sign_up_page'),
    url(r'^detail/(?P<item_category_id>[0-9]+)$', views.item_detail, name='item_detail'),
    url(r'^add_feedback/(?P<item_category_id>[0-9]+)$', views.add_feedback, name='add_feedback'),
    url(r'^view_table/(?P<table_name>[0-9]+)$', views.view_table, name='view_table'),
    url(r'^mark_delivered/(?P<order_id>[0-9]+)$', views.mark_delivered, name='mark_delivered'),
    url(r'^order_details/(?P<order_id>[0-9]+)/(?P<return_to>[A-Z]+)$', views.order_details, name='order_details'),
    url(r'^delete_item_page$', views.delete_item_page, name='delete_item_page'),
    url(r'^delete_item/(?P<item_id>[0-9]+)$', views.delete_item, name='delete_item'),
    url(r'^delete_order_page$', views.delete_order_page, name='delete_order_page'),
    url(r'^delete_order/(?P<order_id>[0-9]+)$', views.delete_order, name='delete_order'),
    url(r'^insert_item$', views.insert_item, name='insert_item'),
    url(r'^insert_item_page$', views.insert_item_page, name='insert_item_page'),
    url(r'^modify_item$', views.modify_item, name='modify_item'),
    url(r'^modify_order_page$', views.modify_order_page, name='modify_order_page'),
    url(r'^modify_order$', views.modify_order, name='modify_order'),
    url(r'^women_items$', views.women_items, name='women_items'),
    url(r'^men_items$', views.men_items, name='men_items'),
    url(r'^kids_items$', views.kids_items, name='kids_items'),
    url(r'^user_order$', views.user_order, name='user_order'),
    url(r'^user_profile$', views.user_profile, name='user_profile'),
    url(r'^post_sign_up/(?P<hashed_username>[\s\S]+)$', views.post_sign_up, name='post_sign_up'),
    url(r'^transaction_status$', views.transaction_status, name='transaction_status'),

    # url(r'^add_to_cart/(?P<item_category_id>[0-9]+)/(?P<quantity>[0-9]+)$', views.add_item_category_to_cart, name='add_to_cart'),
]










