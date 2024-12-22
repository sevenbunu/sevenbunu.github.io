from flask import Flask, request, redirect, session, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Секретный ключ для сессий

# GitHub OAuth конфигурация
GITHUB_CLIENT_ID = 'your_client_id_here'
GITHUB_CLIENT_SECRET = 'your_client_secret_here'
GITHUB_REDIRECT_URI = 'http://localhost:5000/auth/github/callback'  # URL для обратного вызова

@app.route('/')
def index():
    return '<h1>Добро пожаловать! <a href="/auth/github">Войти через GitHub</a></h1>'


@app.route('/auth/github')
def github_login():
    # Перенаправляем пользователя на GitHub для авторизации
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=user"
    return redirect(github_auth_url)


@app.route('/auth/github/callback')
def github_callback():
    # Получаем код из запроса
    code = request.args.get('code')
    if not code:
        return "Ошибка: отсутствует код авторизации", 400

    # Обмениваем код на токен доступа
    token_url = "https://github.com/login/oauth/access_token"
    headers = {'Accept': 'application/json'}
    data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()

    if 'access_token' not in response_data:
        return "Ошибка при получении токена", 400

    access_token = response_data['access_token']

    # Получаем данные пользователя с помощью токена доступа
    user_info_url = "https://api.github.com/user"
    headers = {'Authorization': f'token {access_token}'}
    user_response = requests.get(user_info_url, headers=headers)
    user_data = user_response.json()

    # Сохраняем данные пользователя в сессии или базе данных
    session['user'] = {
        'id': user_data['id'],
        'login': user_data['login'],
        'name': user_data.get('name'),
        'avatar_url': user_data['avatar_url']
    }

    return f"""
    <h1>Добро пожаловать, {user_data.get('name', user_data['login'])}!</h1>
    <img src="{user_data['avatar_url']}" alt="Avatar" style="width:100px; height:100px;">
    <p><a href="/">На главную</a></p>
    """


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)