from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from services.auth_service import login_required
from services.user_service import add_interest, get_interests
from services.alert_service import send_email_alert, send_slack_alert
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# OAuth 초기화 및 등록
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# 라우팅은 동일하게 유지
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/login")
def login():
    return oauth.google.authorize_redirect(redirect_uri=url_for("callback", _external=True))

@app.route("/callback")
def callback():
    token = oauth.google.authorize_access_token()
    user = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo").json()
    print("USER:", user)
    session["user"] = user
    return redirect("/dashboard")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html", email=session['user']['email'])

@app.route("/api/interests", methods=["POST"])
@login_required
def register_interest():
    data = request.get_json()
    return add_interest(session['user']['email'], data["ticker"])

@app.route("/api/interests")
@login_required
def list_interests():
    return get_interests(session['user']['email'])

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/api/interests/<ticker>", methods=["DELETE"])
@login_required
def remove_interest(ticker):
    # 관심 종목 삭제 로직
    try:
        # user_service에서 관심 종목 삭제 함수 호출
        result = remove_interest_by_ticker(session['user']['email'], ticker)
        return jsonify({"success": True, "message": f"{ticker} 종목이 삭제되었습니다."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/alerts", methods=["GET"])
@login_required
def get_alerts():
    # 알림 목록 조회
    try:
        # alert_service에서 사용자 알림 목록 조회
        alerts = get_user_alerts(session['user']['email'])
        return jsonify({"success": True, "alerts": alerts})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/alerts", methods=["POST"])
@login_required
def create_alert():
    # 알림 생성
    try:
        data = request.get_json()
        # alert_service에서 알림 생성
        result = create_user_alert(
            session['user']['email'],
            data["ticker"],
            data["type"],
            data["condition"],
            data["value"],
            data["method"]
        )
        return jsonify({"success": True, "message": "알림이 설정되었습니다."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/alerts/<alert_id>", methods=["DELETE"])
@login_required
def delete_alert(alert_id):
    # 알림 삭제
    try:
        # alert_service에서 알림 삭제
        result = delete_user_alert(session['user']['email'], alert_id)
        return jsonify({"success": True, "message": "알림이 삭제되었습니다."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)