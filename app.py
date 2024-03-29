from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.utils import secure_filename

# from functools import wraps
import random

# DB 기본 코드
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = 'be46366e89d9440ca2d8f8fbe05df574'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(50), nullable=False)
    id = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'{self.username} {self.id} {self.password}'

class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.String(100), db.ForeignKey('User.id'), nullable=False)
    image = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    explanation = db.Column(db.String(10000), nullable=False)

    def __repr__(self):
        return f'{self.image} {self.date} {self.place} {self.explanation}'

with app.app_context():
    db.create_all()

# 첫 화면, 로그인/회원가입 선택
@app.route('/')
def home():
    return render_template('home.html')

# 회원가입 화면
@app.route('/register/form/')
def register():
    return render_template('register.html')

# 회원정보 DB에 저장하기
@app.route('/member/register/', methods=['GET', 'POST'])
def mem_register():
    username_receive = request.args.get("username")
    id_receive = request.args.get("id")
    password_receive = request.args.get("password")

    if not all([username_receive, id_receive, password_receive]):
        msg = '모든 정보를 기입해주세요.'
        return render_template('register.html', data=msg)
    else:
        if User.query.filter_by(id=id_receive).all():
            msg = '이미 존재하는 아이디입니다.'
            return render_template('register.html', data=msg)
        else:
            user = User(username=username_receive, id=id_receive, password=password_receive)
            db.session.add(user)
            db.session.commit()
            msg = '가입이 완료되었습니다! 로그인 페이지로 이동합니다.'
            return render_template('login.html', data=msg)

# 로그인 화면
@app.route('/login/')
def login():
    return render_template('login.html')

# 로그인(jwt 활용법 따로 공부하기...)
@app.route('/member/login/', methods=['GET', 'POST'])
def mem_login():
    id_receive = request.args.get("id")
    password_receive = request.args.get("password")
    user = User.query.filter_by(id=id_receive).first()

    if not all([id_receive, password_receive]):
        msg = "빈칸을 모두 채워주세요"
        return render_template('login.html', data=msg)
    else:
        if not user or user.id != user.id or password_receive != user.password:
            msg = "아이디 및 비밀번호를 다시 확인해주세요"
            return render_template('login.html', data=msg)
        else:
            return redirect(url_for('memory'))

# 로그인 후 홈화면
@app.route('/memory/')
def memory():
    memory_list = Memory.query.all()
    memory_choice = random.choice(memory_list)
    return render_template('memory.html', data=memory_choice)

# 추억 추가 form
@app.route('/create/')
def create():
    return render_template('add_form.html')

# 추억 추가하기
@app.route('/memory/create/', methods=['GET', 'POST'])
def memory_create():
    if request.method == 'POST':
        date_receive = request.form['date']
        place_receive = request.form['place']
        exp_receive = request.form['explanation']

        f = request.files['file']
        if f and date_receive and place_receive and exp_receive:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # pythonanywhere 배포용 저장 경로
            # f.save('/home/yyan392/mysite/static/' + filename)

            memory = Memory(image=filename, date=date_receive, place=place_receive, explanation=exp_receive)
            db.session.add(memory)
            db.session.commit()
    return render_template('add_form.html')

# 수정 form
@app.route('/edit/', methods=['GET'])
def edit():
    id_receive = request.args.get("id")
    data = Memory.query.filter_by(id=id_receive).first()
    return render_template('edit_form.html', data=data)

# 수정하기
@app.route('/memory/edit/', methods=['GET'])
def memory_edit():
    id_receive = request.args.get("id")
    image_receive = request.args.get("image")
    date_receive = request.args.get("date")
    place_receive = request.args.get("place")
    exp_receive = request.args.get("explanation")

    data = Memory.query.filter_by(id=id_receive).first()

    if not all([place_receive, exp_receive]):
        return render_template('edit_form.html', data=data)
    
    if data.date != date_receive:
        data.date = date_receive
    if data.place != place_receive:
        data.place = place_receive
    if data.explanation != exp_receive:
        data.explanation = exp_receive
    db.session.add(data)
    db.session.commit()
    return redirect(url_for('memory'))

# 삭제하기
@app.route('/delete/')
def delete():
    id_receive = request.args.get("id")
    data = Memory.query.filter_by(id=id_receive).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('memory'))

# 전체 조회
@app.route('/show/all/', methods=['GET'])
def show_all():
    data = Memory.query.all()
    return render_template('show.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)