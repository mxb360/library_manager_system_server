from django.db import models

class User(models.Model):
    name = models.CharField(max_length=128)
    number = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    is_admin = models.SmallIntegerField(default=0)
    can_lend = models.SmallIntegerField(default=1)
    college = models.CharField(max_length=128)
    image = models.ImageField(upload_to="static/user", default="")

    class Meta:
        db_table = 'lms_user'

class Book(models.Model):
    name = models.CharField(max_length=128)
    author = models.CharField(max_length=128)
    isbn = models.CharField(max_length=128)
    image = models.ImageField(upload_to='static/book/', default="")
    des = models.TextField(verbose_name='简介') 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    press = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    storage_count = models.IntegerField(default=0) 
    lend_count = models.IntegerField(default=0) 
    page = models.IntegerField(default=0) 

    class Meta:
        db_table = 'lms_book'

class Category(models.Model):
    NULL_CATEGORY_NAME = ''

    name = models.CharField(max_length=128)
    book_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'lms_category'

class LendInfo(models.Model): 
    lend_id = models.CharField(max_length=128)
    number = models.CharField(max_length=128)
    isbn = models.CharField(max_length=128)
    lend_date = models.CharField(max_length=20) 
    days = models.IntegerField(default=0) 
    return_date = models.CharField(max_length=20) 
    forfeit = models.DecimalField(max_digits=10, decimal_places=2) 
    book_status = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'lms_lend_info'

class Comment(models.Model): 
    number = models.CharField(max_length=128)
    isbn = models.CharField(max_length=128)
    comment = models.TextField()

    class Meta:
        db_table = 'lms_comment'
