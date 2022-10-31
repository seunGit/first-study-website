from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('main_page.html')


@app.route('/list/')
def border_list():
    return render_template('border_list.html')


@app.route('/posting/')
def posting_page():
    return render_template('posting_page.html')


@app.route('/read/')
def read_post():
    return render_template('read_post.html')


# @app.route("/list", methods=["GET"])
# def border_list_get():
#     return jsonify({'msg': 'GET 연결 완료!'})
#
#
# @app.route("/mars", methods=["POST"])
# def web_mars_post():
#     sample_receive = request.form['sample_give']
#     print(sample_receive)
#     return jsonify({'msg': 'POST 연결 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=10005, debug=True)
