from flask import Flask, request, redirect, make_response, render_template_string, session
import threading
import time
import datetime
import random
import string, os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For sessions

# --- Хранилище пользователей ---
user_db = {
    'admin': {'password': 'admin123'},
    'user1': {'password': '1111'},
    'user2': {'password': ''.join(random.choices(string.ascii_letters + string.digits, k=8))}
}
print(f"[INFO] user2 password: {user_db['user2']['password']}")

# --- Флаг хранится у админа ---
admin_flag = "FLAG{this_is_the_secret_flag}"

# --- Комментарии ---
comments = []
comments.append({
    'author': 'admin',
    'text': 'dont change my password',
    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
})

# --- HTML Шаблоны ---
LOGIN_TEMPLATE = """
<!doctype html>
<html>
<head><title>Login</title></head>
<body>
  <h2>Login</h2>
  <form method="post" action="/login">
    <input name="username" placeholder="Username"><br><br>
    <input name="password" type="password" placeholder="Password"><br><br>
    <input type="submit" value="Login">
  </form>
  {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
</body>
</html>
"""

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>XSS Demo</title>
  <style>
    body {{ text-align: center; font-family: Arial, sans-serif; margin-top: 50px; }}
    img {{ width: 300px; }}
    form {{ margin-top: 20px; }}
    textarea {{ width: 300px; height: 100px; }}
    .comment {{ margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; }}
  </style>
</head>
<body>
  <h1><strong>Welcome, {username}</strong></h1>

  <form action="/comment" method="post">
    <textarea name="text" placeholder="Leave a comment..."></textarea><br>
    <input type="submit" value="Submit Comment">
  </form>

  <h2>Comments</h2>
  {comments}
</body>
</html>
"""


CHANGE_PASSWD_FORM = """
<!doctype html>
<html>
<head><title>Change Password</title></head>
<body>
  <h2>Change Password for {{username}}</h2>
  <form method="post" action="/change_passwd">
    <input type="password" name="new_password" placeholder="New password"><br><br>
    <input type="submit" value="Change Password">
  </form>
  <p><a href="/">Back to comments</a></p>
</body>
</html>
"""

FLAG_PAGE = """
<!doctype html>
<html>
<head><title>Secret Flag</title></head>
<body>
  <h2>Congratulations, {{username}}!</h2>
  <p>Your flag is: <b>{{flag}}</b></p>
</body>
</html>
"""

# --- Утилита рендера комментариев ---
def render_comments():
    result = ""
    for c in comments:
        result += f"""
        <div class='comment'>
            <b>{c['author']}</b> [{c['time']}]:<br>
            {c['text']}
        </div>
        """
    return result

# --- Роуты ---
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    username=session.get('username')
    resp = make_response(render_template_string(
        HTML_TEMPLATE.format(comments=render_comments(), username=username),
        
    ))

    # Если админ залогинен — устанавливаем куку с флагом
    # if session.get('username') == 'admin':
    #     resp.set_cookie('flag', admin_flag)
    return resp

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Если пользователь уже залогинен — показать имя и кнопку выхода
    if session.get('logged_in'):
        username = session.get('username')
        return f"""
        <!doctype html>
        <html>
        <head><title>Already logged in</title></head>
        <body>
          <p>You are already logged in as <b>{username}</b>.</p>
          <form method="post" action="/logout">
            <input type="submit" value="Logout">
          </form>
          <p><a href="/">Back to main</a></p>
        </body>
        </html>
        """

    # Иначе обычный логин
    error = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_db.get(username)

        if user and user['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            if username == 'admin':
                return redirect('/flag')
            return redirect('/')
        else:
            error = 'Invalid credentials'
    return render_template_string(LOGIN_TEMPLATE, error=error)
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')


@app.route('/comment', methods=['POST'])
def comment():
    if not session.get('logged_in'):
        return redirect('/login')
    
    username = session.get('username', 'Anonymous')
    text = request.form.get('text', '')
    comments.append({
        'author': username,
        'text': text,
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return redirect('/')


@app.route('/change_passwd', methods=['GET', 'POST'])
def change_passwd():
    if not session.get('logged_in'):
        return redirect('/login')

    username = session.get('username')
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if new_password:
            user_db[username]['password'] = new_password
            return f"Password for {username} changed to: {new_password}. <a href='/'>Back</a>"
        return "Password cannot be empty", 400

    return render_template_string(CHANGE_PASSWD_FORM, username=username)

@app.route('/flag')
def flag():
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect('/login')
    return render_template_string(FLAG_PAGE, username='admin', flag=admin_flag)

# --- Bot, который посещает страницу под админом ---
# def admin_bot():
#     with app.test_client() as client:
#         while True:
#             time.sleep(5)
#             print("[BOT] Admin bot visiting comments page...")
#             # Залогинимся под админом вручную в сессии клиента
#             with client.session_transaction() as sess:
#                 sess['logged_in'] = True
#                 sess['username'] = 'admin'

#             # Бот читает страницу, где может сработать XSS
#             client.get('/')

#             print("[BOT] Done visiting.")

if __name__ == '__main__':
    # threading.Thread(target=admin_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
