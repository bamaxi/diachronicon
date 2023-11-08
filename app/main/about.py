from datetime import datetime
from flask import render_template

from . import bp


@bp.route('/about/')
def main():
    return render_template(
        'about.html', title='Описание',
        year=datetime.now().year,
    )