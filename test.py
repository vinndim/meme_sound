import json

from flask import Flask, url_for, request, render_template

app = Flask(__name__)


@app.route('/<title>')
@app.route('/index/<title>')
def index(title):
    return render_template('index.html', title=title)


@app.route('/training/<prof>')
def training(prof):
    return render_template('training.html', prof=prof)


@app.route('/list_prof/<list_prof>')
def list_prof(list_prof):
    professions = ['инженер-исследователь', 'пилот', 'строитель', 'экзобиолог', 'врач',
                   'инженер по терраформированию', 'климатолог', 'специалист по радиационной защите',
                   'астрогеолог', 'гляциолог', 'инженер жизнеобеспечения', 'метеоролог', 'оператор марсохода',
                   'киберинженер',
                   'штурман', 'пилот дронов']
    return render_template('list_prof.html', list=list_prof, professions=professions)


@app.route('/answer')
@app.route('/auto_answer')
def answer():
    form = {
        'title': 'Автоматический ответ',
        'surname': 'Иванов',
        'name': 'Никита',
        'education': '0 класс',
        'profession': 'нет',
        'sex': 'male',
        'motivation': 'Всегда хотел засьтрять в яме!',
        'ready': 'Всегда готов!!!'
    }
    return render_template('auto_answer.html', answer=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
