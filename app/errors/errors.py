from datetime import datetime
from flask import render_template, url_for
from markupsafe import Markup, escape

from . import bp


@bp.app_errorhandler(404)
def not_found_error(error,):
    return render_template(
        'errors/404.html', title='Не найдено :(',
        year=datetime.now().year,
    ), 404


@bp.app_errorhandler(405)
def bad_method_error(error,):
    search_link = Markup(f'<a href="{ url_for("search.search") }">cтраницу поиска</a>')
    return render_template(
        'errors/405.html', title='Не найдено :(',
        message=f"Возможно, вы искали {search_link}",
        year=datetime.now().year,
    ), 404


@bp.app_errorhandler(500)
def internal_error(error):
    return render_template(
        'errors/500.html', title='Ошибка :(',
        year=datetime.now().year,
    ), 500
