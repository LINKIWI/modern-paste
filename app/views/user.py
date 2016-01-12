from modern_paste import app
from uri.user import *
from api.decorators import render_view


@app.route(UserLoginInterfaceURI.path, methods=['GET'])
@render_view
def user_login_interface():
    return 'user/login.html', {}
