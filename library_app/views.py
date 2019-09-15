from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from library_app.models import *
import hashlib

# 已经登录的用户字典
# 键值对：
#   'user_token': 'number'
user_login_token = {}

# 返回的状态信息
# 对于任意一个请求，都会有其中一条信息
return_message = {
    'OK':                     (0, 'ok'),
    'BadRequest':             (1, 'bad request'),
    'UserNotFoundError':      (2, 'user not found'),
    'UserTokenError':         (3, 'user_token error'),
    'PasswordError':          (4, "user's passwored error"),
    'PermissionError':        (5, 'Permission denied'),
    'UserAlreadyExistsError': (6, 'user already exist'),
    'CategoryAlreadyExistsError': (7, 'category already exist'),
    'CategoryNotFoundError':  (8, 'category not found'),
    'BookAlreadyExistsError': (9, 'book already exist'),
    'BookNotFoundError':      (10, 'book not found'),
    'LendInfoNotFoundError':  (11, 'lend info not found'),
}

def response(info='OK', data={}):
    """
    Http应答Json数据，包含所有的http响应
    info：将返回的位于return_message中的状态信息，默认'OK'
    data: 附加的数据
    最终返回：
     {'code': code, 'message': message, 'data': data}
    """

    code, message = return_message[info]
    return JsonResponse({
        'code': code, 
        'message': message, 
        'data': data,
    }, json_dumps_params={'ensure_ascii': False})


def get_arg(request, args, method='POST'):
    re = []
    
    for arg in args:
        re.append(getattr(request, method).get(arg))
    if all(re):
        return tuple(re)

def check_arg(is_admin, can_lend):
    return is_admin in ['0', '1'] and can_lend in ['0', '1']

def get_user(user_token):
    number = user_login_token.get(user_token)
    if number:
        try:
            return User.objects.get(number=number)
        except:
            pass



############################# URL视图 ###########################

def index(request):
    """
    测试服务器是否在工作
    返回'OK'
    """

    return response(data=request.POST)

def login(request):
    """
    用户登录
    url: /login
    请求方法: POST
    请求参数：
      number: 借阅证（必须）
      password: 密码（必须）
      is_admin: 是否是管理员（必须，取值0, 1）
    如果登录成功，data里将包含用户标记user_token，否则返回相关错误
    """

    re = get_arg(request, ('number', 'password', 'is_admin'))
    if not re:
        return response('BadRequest')
    number, password, is_admin = re
    if is_admin not in ['0', '1']:
        return response('BadRequest')

    # 尝试从数据库中获取该用户，并判断能否登录
    try:
        user = User.objects.get(number=number)
    except:
        return response('UserNotFoundError')
    if user.password != password:
        return response('PasswordError')
    if int(is_admin) != user.is_admin:
        return response('UserNotFoundError')

    # 通过md5生成user_token
    md5 = hashlib.md5(bytes('library_sedglocerxxcf', encoding='utf-8'))
    md5.update((number + 'library_xxxfgh').encode())
    user_token = md5.hexdigest()
    # 将生成的user_token添加到登录用户字典中，表示该用户已经登录
    user_login_token[user_token] = number
    # 返回user_token
    return response('OK', {'user_token':user_token})


def logout(request):
    """
    用户登出
    url: /logout
    请求方法: POST
    请求参数：
      user_token: 用户标志（必须）
    如果登出成功，返回'OK'，否则返回相关错误
    """

    re = get_arg(request, ('user_token', ))
    if not re:
        return response('BadRequest')
    user_token, = re
    try:
        user_login_token.pop(user_token)
    except KeyError:
        return response('UserTokenError')
    return response('OK')
    

def user_info(request):
    """
    获取用户信息
    url: /user_info
    请求方法: POST
    请求参数：
      user_token: 用户标志（必须）
    如果找到信息，data将包含用户信息，否则返回相关错误
    """

    # 获取用户token
    re = get_arg(request, ('user_token', ))
    if not re:
        return response('BadRequest')
    user_token, = re
    # 获取用户对象
    user = get_user(user_token)
    if not user:
        return response('UserTokenError')
    # 返回用户信息
    return response(data={
        'name': user.name,
        'number': user.number,
        'is_admin': user.is_admin,
        'can_lend': user.can_lend,
        'college': user.college,
        #'image': user.image,
    })

def add_user(request):
    """
    添加用户
    url: /add_user
    请求方法: POST
    请求参数：
      user_token: 用户标志（必须）
    如果添加成功，返回ok找到信息，否则返回相关错误
    注意，调用该API的用户必须是管理员
    """

    # 获取用户token
    re = get_arg(request, ('user_token', 'number', 'password', 'name', 'is_admin', 'can_lend', 'college'))
    if not re:
        return response('BadRequest')
    user_token, is_admin, can_lend = re[0], re[4], re[5]
    # 获取用户对象
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')
    if not check_arg(is_admin, can_lend):
        return response('BadRequest')

    user = User()
    _, user.number, user.password, user.name, user.is_admin, user.can_lend, user.college = re

    try:
        user = User.objects.get(number=user.number)
    except:
        user.is_admin, user.can_lend = int(is_admin), int(can_lend)
        user.save()
        print("[添加新用户：" + str(user) + "]")
        return response('OK')
    return response('UserAlreadyExistsError')

def change_user_info(request):
    """
    添加用户
    url: /change_user_info
    请求方法: POST
    请求参数：
      user_token: 用户标志（必须）
    如果修改成功，返回ok找到信息，否则返回相关错误
    注意，调用该API的用户必须是管理员
    """

    # 获取用户token
    re = get_arg(request, ('user_token', 'number', 'password', 'name', 'is_admin', 'can_lend', 'college'))
    if not re:
        return response('BadRequest')
    user_token, number, is_admin, can_lend = re[0], re[1], re[4], re[5]
    # 获取用户对象
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    if not check_arg(is_admin, can_lend):
        return response('BadRequest')
    
    try:
        user = User.objects.get(number=number)
    except:
        return response('UserNotFoundError')   
    _, _, user.password, user.name, user.is_admin, user.can_lend, user.college = re
    user.is_admin, user.can_lend = int(is_admin), int(can_lend)
    user.save()
    print("[修改用户：" + str(user) + "]")
    return response('OK')

def change_password(request):
    re = get_arg(request, ("user_token", "old_password", "new_password"))
    if not re:
        return response('BadRequest')
    user_token, old_password, new_password = re
    
    user = get_user(user_token)
    if not user:
        return response('UserTokenError')
    if user.password != old_password:
        return response('PasswordError')
    user.password = new_password
    user.save()
    return response('OK')

def get_user_info(request):
    re = get_arg(request, ("user_token", "number"))
    if not re:
        return response('BadRequest')
    user_token, number = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')
    try:
        user = User.objects.get(number=number)
    except:
        return response('UserNotFoundError')
    return response('OK', {
        "number": user.number,
        'name': user.name,
        'college': user.college,
        'is_admin': user.is_admin,
        'can_lend': user.can_lend,
        'password': user.password,
    })


def remove_user(request):
    re = get_arg(request, ("user_token", "number"))
    if not re:
        return response('BadRequest')
    user_token, number = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        user = User.objects.get(number=number)
    except:
        return response('UserNotFoundError')
    user.delete()
    return response('OK')

def search_user(request):
    re = get_arg(request, ("user_token", "type", "words"))
    if not re:
        return response('BadRequest')
    user_token, type_, words = re
    if type_ not in ['name', 'number', 'college', 'admin', 'student', 'can_lend', "all"]:
        return response('BadRequest')

    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    words = words.replace("*", "")
    if type_ == 'admin':
        type_, words = 'is_admin', '1'
    elif type_ == 'student':
        type_, words = 'is_admin', '0'
    elif type_ == 'can_lend':
        words = '1'

    data = {"length": 0, "users": []}
    for user in User.objects.all():
        if type_ == 'all' or words in str(getattr(user, type_)):
            data["length"] += 1
            data["users"].append({
                "number": user.number,
                'name': user.name,
                'college': user.college,
                'is_admin': user.is_admin,
                'can_lend': user.can_lend,
                #'password': user.password,
            })
    return response('OK', data)

def get_category(request):
    re = get_arg(request, ("user_token",))
    if not re:
        return response('BadRequest')
    user_token, = re
    user = get_user(user_token)
    if not user:
        return response('UserTokenError')

    try:
        Category.objects.get(name=Category.NULL_CATEGORY_NAME)
    except:
        category = Category()
        category.name = Category.NULL_CATEGORY_NAME
        category.book_count = 0
        category.save()

    categories = Category.objects.all()
    data = {"length": 0, 'categories': []}
    for category in categories:
        data['length'] += 1
        data['categories'].append({
            'name': category.name,
            'book_count': category.book_count,
        })
    return response('OK', data)

def add_category(request):
    re = get_arg(request, ("user_token", "name"))
    if not re:
        return response('BadRequest')
    user_token, name = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        category = Category.objects.get(name=name)
    except:
        category = Category()
        category.name = name
        category.book_count = 0
        category.save()
        return response('OK')
    return response('CategoryAlreadyExistsError')

def change_category(request):
    re = get_arg(request, ("user_token", "name1", "name2"))
    if not re:
        return response('BadRequest')
    user_token, name1, name2 = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        category = Category.objects.get(name=name1)
    except:
        return response('CategoryNotFoundError')

    try:
        category = Category.objects.get(name=name2)
    except:
        category.delete()
        category.name = name2
        category.save()

        Book.objects.filter(category=name1).update(category=name2)

        return response('OK')
    return response('CategoryAlreadyExistsError')


def remove_category(request):
    re = get_arg(request, ("user_token", "name"))
    if not re:
        return response('BadRequest')
    user_token, name = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        category = Category.objects.get(name=name)
        null_category = Category.objects.get(name=Category.NULL_CATEGORY_NAME)
    except:
        return response('CategoryNotFoundError')
    
    null_category.book_count += category.book_count
    Book.objects.filter(category=name).update(category=Category.NULL_CATEGORY_NAME)

    category.delete()
    null_category.save()
    return response('OK')


def add_book(request):
    arg = ('user_token', 'isbn', 'name', 'author', 'category', 'page', 'price', 'press', 'count', 'des')
    re = get_arg(request, arg)
    if not re:
        return response('BadRequest')
    user_token, isbn, category, page, count = re[0], re[1], re[4], re[5], re[8]
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')
    try:
        int(page)
        int(count)
    except:
        return response('BadRequest')

    try:
        category = Category.objects.get(name=category)
    except:
        return response('CategoryNotFoundError')

    try:
        isbn = Book.objects.get(isbn=isbn)
    except:
        book = Book()

        (_, book.isbn, book.name, book.author, book.category, book.page, book.price, 
        book.press, book.storage_count, book.des) = re
        book.page = int(page)
        image = request.FILES.get("image")

        if image:
            image.name = isbn + image.name
            book.image = image
        book.save()

        category.book_count += 1
        category.save()
        return response('OK')
    return response('CategoryAlreadyExistsError')

def change_book(request):
    arg = ('user_token', 'isbn', 'name', 'author', 'category', 'page', 'price', 'press', 'count', 'des')
    re = get_arg(request, arg)
    if not re:
        return response('BadRequest')
    user_token, isbn, category, page, count = re[0], re[1], re[4], re[5], re[8]
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        int(page)
        int(count)
    except:
        return response('BadRequest')

    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return response('BookNotFoundError')
    try:
        new_category = Category.objects.get(name=category)
        old_category = Category.objects.get(name=book.category)
    except:
        return response('CategoryNotFoundError')
    
    (_, _, book.name, book.author, book.category, book.page, book.price, 
    book.press, book.storage_count, book.des) = re
    image = request.FILES.get("image")
    if image:
        image.name = isbn + image.name
        book.image = image

    book.save()

    new_category.book_count += 1
    new_category.save()
    old_category.book_count -= 1
    old_category.save()
    return response('OK')

def remove_book(request):
    arg = ('user_token', 'isbn')
    re = get_arg(request, arg)
    if not re:
        return response('BadRequest')
    user_token, isbn = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return response('BookNotFoundError')
    try:
        category = Category.objects.get(name=book.category)
    except:
        return response('CategoryNotFoundError')

    book.image.delete()
    book.delete()
    category.book_count -= 1
    category.save()
    return response('OK')

def get_book(request):
    re = get_arg(request, ("user_token", "isbn"))
    if not re:
        return response('BadRequest')
    user_token, isbn = re
    user = get_user(user_token)
    if not user:
        return response('UserTokenError')

    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return response('BookNotFoundError')

    try:
        url = book.image.url
    except:
        url = ''

    return response('OK', {
        'isbn': book.isbn,
        'name': book.name,
        'author': book.author,
        'category': book.category,
        'press': book.press,
        'price': book.price,
        'count': book.storage_count,
        'lend_count': book.lend_count,
        'des': book.des,
        'page': book.page,
        'image': url
    })

def search_book(request):
    re = get_arg(request, ("user_token", "category", "search_by", "words"))
    if not re:
        return response('BadRequest')
    user_token, category, search_by, words = re
    print(re)
    if search_by not in ['isbn', 'name', 'author']:
        return response('BadRequest')
    
    if category != "*":
        try:
            category = Category.objects.get(name=category)
        except:
            return response('CategoryNotFoundError')
    if category == "*":
        books = Book.objects.all()
    else:
        books = Book.objects.filter(category=category)

    data = {"length": 0, "books" : []}
    words = words.replace("*", "")
    for book in books:
        if words in getattr(book, search_by):
            try: 
                url = book.image.url
            except:
                url = ''

            data['length'] += 1
            data['books'].append({
                'isbn': book.isbn,
                'name': book.name,
                'author': book.author,
                'category': book.category,
                'press': book.press,
                'price': book.price,
                'count': book.storage_count,
                'lend_count': book.lend_count,
                'des': book.des,
                'page': book.page,
                'image': url
            })
    return response('OK', data)

def lend_book(request):
    arg = ('user_token', 'isbn', 'number', 'date', 'days', 'forfeit')
    re = get_arg(request, arg)
    if not re:
        return response('BadRequest')
    user_token, isbn, number, date, days, forfeit = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        user = User.objects.get(number=number)
    except:
        return response('UserNotFoundError')
    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return response('BookNotFoundError')

    if book.storage_count <= 0:
        return response('BookNotFoundError')

    lend = LendInfo()
    lend.isbn = isbn
    lend.number = number
    lend.days = days
    lend.lend_date = date
    lend.return_date = ""
    lend.book_status = 0
    lend.status = 1
    lend.save()

    book.storage_count -= 1
    book.lend_count += 1
    book.save()
    return response('OK')

def return_book(request):
    arg = ('user_token', 'isbn', 'number', 'date', 'forfeit', "book_status")
    re = get_arg(request, arg)
    if not re:
        return response('BadRequest')
    user_token, isbn, number, date, forfeit, book_status = re
    admin = get_user(user_token)
    if not admin:
        return response('UserTokenError')
    if not admin.is_admin:
        return response('PermissionError')

    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return response('BookNotFoundError')

    try:
        lends = LendInfo.objects.filter(number=number, isbn=isbn)
    except:
        return response('LendInfoNotFoundError')

    lend = None
    for _lend in lends:
        if _lend.status == 1:
            lend = _lend
            break
    if not lend:
        return response('LendInfoNotFoundError')

    lend.status += 1
    lend.return_date = date
    if int(forfeit):
        lend.forfeit = 0
    lend.save()

    book.storage_count += 1
    book.lend_count -= 1
    book.save()
    return response('OK')
