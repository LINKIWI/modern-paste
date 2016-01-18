from modern_paste import app

from api.decorators import render_view


@app.errorhandler(404)
@render_view
def not_found(e):
    return 'error/not_found.html', {}


@app.errorhandler(500)
@render_view
def internal_server_error(e):
    return 'error/internal_server_error.html', {}
