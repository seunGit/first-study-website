# 파이썬 모듈 : flask, pymongo, dnspython, certifi, pyjwt, datetime

from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
from pymongo import MongoClient
import datetime, jwt, json

import certifi

# ? 맥 환경 DB 초기화 코드( certifi가 필요 )
ca = certifi.where()
client = MongoClient(
    "mongodb+srv://test:sparta@cluster0.pkdgkh7.mongodb.net/?retryWrites=true&w=majority",
    tlsCAFile=ca,
)
db = client.dailyfit

app = Flask(__name__)

# ? .env에 저장해야하는데 테스트용이라서 여기에 저장
SECRET_KEY = "secretkey"


# ?
# token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.user.find_one({"id": payload['id']})
#         return render_template('index.html', nickname=user_info["nick"])
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
# ? 

# ! 메인페이지
@app.route('/', methods=["GET"])
def home_get():
    # ! request.cookies.get이 작동하는 이유 :: 브라우저에서 따로 스크립트파일에 코딩하지 않았지만, 쿠키가 저장되면 자동으로 전송
    return render_template('main.html')


@app.route('/', methods=["POST"])
def home_post():
    # ! 일단, signin에서 아이디/비밀번호를 입력하면, jwt토큰을 발행해서 정보를 가지고 있고, 쿠키에 저장이 되어있는 상태이다.
    # ! 여기서, 쿠키로 토큰을 받아서 -> 토큰이 존재하는 경우, 암호화 된 토큰을 쿠키에서 꺼낸다.
    # ! 복호화 된 토큰에서 payload의 id를 검색해서 디비에서 일치하면 id정보를 가져온다. 
    # ! id정보가 있다면 jsonify로 브라우저로 정보를 전송한다.
    token_receive = request.cookies.get("mytoken").strip("%22")
    if token_receive == None:
        print("토큰이 존재하지 않습니다.")
        return jsonify({"msg": "토큰이 존재하지 않습니다"})
    else:
        print("토큰이 존재합니다.")
        print(" ---- mytoken ---- : ", token_receive)
        try:
            print("test1지점")
            # ! "_id"를 False로 하지 않으면 전송에 문제가 생긴다. + # ! 토큰이 만료되었을 경우 아무 에러도 보여주지 않고 그냥 동작을 안한다. 히밤.. 주의하기(한참헤멤)
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            print("test2지점")
            user_info = db.users.find_one({'user_id': payload['id']}, {"_id": False, "user_pw": False})
            print("test3지점")
            print("user_info:", user_info)
            # j_user_id = json.dumps(user_id)
            return jsonify({'user_info': user_info})
        except jwt.ExpiredSignatureError:
            return jsonify({'msg': "토큰이 만료되었음"})
        except jwt.exceptions.DecodeError:
            return jsonify({'msg': '토큰이 존재하지 않음'})

    # return render_template('main.html')
    # # * user_info = db.user.find_one({"id":payload['id']})
    # try:
    #     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    #     # print("payload: ",payload)
    #     user_info = db.users.find_one({'user_id': payload['id']})
    #     # print(user_info)
    #     return render_template('main.html')
    # except jwt.ExpiredSignatureError:
    #     print("에러1 발생지점")
    #     # ? ----- redirect(url_for("함수",데이터)) -------
    #     return redirect(url_for("sign_in_get", msg="로그인 시간이 만료되었습니다."))
    # except jwt.exceptions.DecodeError:
    #     print("에러2 발생지점")
    #     return redirect(url_for("sign_in_get", msg="로그인 정보가 존재하지 않습니다."))


# ! 게시글 보기
@app.route('/readpost/', methods=["GET"])
def readpost_get():
    return render_template('readpost.html')


# ! 새글쓰기
@app.route('/writepost/', methods=["GET"])
def writepost_get():
    return render_template('writepost.html')


@app.route("/writepost/", methods=["POST"])
def writepost_post():
    token_receive = request.cookies.get("mytoken").strip("%22")
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({'user_id': payload['id']}, {"_id": False})
    user_id = user_info['user_id']
    day = datetime.datetime.now()
    upload_day = day.strftime("%x")
    upload_time = day.strftime("%X")
    # ! db.seq.update({"name" : "post"}, {"$inc" : {"val" : 1}})
    # ! db.article.update_one({'idx': int(idx)}, {'$inc': {'read_count': 1}})
    boardNum_receive = db.counter.find_one()['totalPosts'] + 1
    # boardSelect_receive = request.form['boardSelect_give']
    boardSubject_receive = request.form['boardSubject_give']
    boardContents_receive = request.form['boardContents_give']
    # "postingSelect":boardSelect_receive,
    doc = {
        "userId": user_id,
        "postingNum": boardNum_receive,
        "postingSubject": boardSubject_receive,
        "postingContents": boardContents_receive,
        "uploadDay": upload_day,
        "uploadTime": upload_time
    }
    db.posts.insert_one(doc)
    db.counter.update_one({"name": "postcount"}, {"$inc": {"totalPosts": 1}})
    return jsonify({'msg': '입력완료!'})


# ! 게시판 리스트
@app.route('/postlist/', methods=["GET"])
def postlist_get():
    return render_template('postlist.html')


# ! postlist => ajax /showposts get요청으로 게시판 리스트 갱신
@app.route("/showposts/", methods=["GET"])
def showposts_get():
    # cheer_list = list(db.cheer.find({}, {'_id': False}))
    # return jsonify({'cheer_list': cheer_list})
    posts_list = list(db.posts.find({}, {"_id": False}))
    return jsonify({"posts_list": posts_list});


# ! 회원가입 기능구현 - signup

# ? GET /signup/요청이 오면 실행
@app.route('/signup/')
def sign_up():
    return render_template('signup.html')


# ? user_id 조회를 통해 중복확인
@app.route('/signup/id_check', methods=['POST'])
def check_id():
    status = 1
    id_receive = request.form['id_give']
    users = list(db.users.find({}, {'_id': False}))
    print(users)
    for user in users:
        user_id = user['user_id']
        if user_id == id_receive:
            status = 0
            break
        else:
            status = 1

    return jsonify({'result': 'success', 'status': status})


# ? 회원가입 정보 DB 저장
@app.route('/signup/create', methods=['POST'])
def create_user():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    # ? 여기서 받아온 pw_receive를 암호화한다. -> 해아 하는 것 :
    # pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    doc = {
        'user_id': id_receive,
        'user_pw': pw_receive
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})


# ! 로그인 기능구현 - signin
# ? GET /signin/ 요청 
@app.route('/signin/')
def sign_in_get():
    return render_template('signin.html')


@app.route("/signin/", methods=["POST"])
def sign_in_post():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    # print(id_receive)
    # print(pw_receive)
    # pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'user_id': id_receive, 'user_pw': pw_receive})
    # print(result)
    # ? !!!!!!!!!!! 혹시 여기아래 payload가 토큰 시간을 지속시키는 코드인가? => ( ㅇㅇ exp가 만료시간을 지속시키는 )
    if result is not None:
        # time = datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
        # exp = str(time)
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)  # 언제까지 유효한지
        }

        # ! jwt토큰 암호화 생성 "secretkey"
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # print(jsonify({'result': 'success', 'token': token}))
        return jsonify({'result': 'success', 'token': token})
    else:
        # print(jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'}))
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
