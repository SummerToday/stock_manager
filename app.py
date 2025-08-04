from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from services.auth_service import login_required
from services.user_service import add_interest, get_interests, remove_interest_by_ticker
from services.alert_service import (
    send_email_alert, send_slack_alert, get_user_alerts, 
    create_user_alert, delete_user_alert
)
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

# 기본 라우팅
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

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

# 관심 종목 API
@app.route("/api/interests", methods=["POST"])
@login_required
def register_interest():
    data = request.get_json()
    return add_interest(session['user']['email'], data["ticker"], data.get("name"))

@app.route("/api/interests")
@login_required
def list_interests():
    return get_interests(session['user']['email'])

@app.route("/api/interests/<ticker>", methods=["DELETE"])
@login_required
def remove_interest(ticker):
    try:
        result = remove_interest_by_ticker(session['user']['email'], ticker)
        return jsonify({"success": True, "message": f"{ticker} 종목이 삭제되었습니다."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 알림 API
@app.route("/api/alerts", methods=["GET"])
@login_required
def get_alerts():
    try:
        alerts = get_user_alerts(session['user']['email'])
        return jsonify({"success": True, "alerts": alerts})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/alerts", methods=["POST"])
@login_required
def create_alert():
    try:
        data = request.get_json()
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
    try:
        result = delete_user_alert(session['user']['email'], alert_id)
        return jsonify({"success": True, "message": "알림이 삭제되었습니다."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 실시간 주가 API (시뮬레이션)
@app.route("/api/market/<market_type>")
@login_required
def get_market_stocks(market_type):
    """
    실시간 주가 데이터 조회 (시뮬레이션)
    market_type: domestic, us, japan, china, europe
    """
    try:
        # 시뮬레이션 데이터
        stock_data = {
            'domestic': [
                {'ticker': '005930', 'name': '삼성전자', 'price': 75000, 'change': 500, 'changePercent': 0.67, 'volume': 15000000, 'marketCap': '448조'},
                {'ticker': '000660', 'name': 'SK하이닉스', 'price': 120000, 'change': -2000, 'changePercent': -1.64, 'volume': 8500000, 'marketCap': '87조'},
                {'ticker': '035420', 'name': 'NAVER', 'price': 205000, 'change': 3500, 'changePercent': 1.74, 'volume': 1200000, 'marketCap': '34조'},
                {'ticker': '005380', 'name': '현대차', 'price': 180000, 'change': -1500, 'changePercent': -0.83, 'volume': 2100000, 'marketCap': '38조'}
            ],
            'us': [
                {'ticker': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'change': 2.30, 'changePercent': 1.33, 'volume': 55000000, 'marketCap': '$2.7T'},
                {'ticker': 'MSFT', 'name': 'Microsoft Corp.', 'price': 345.20, 'change': -1.80, 'changePercent': -0.52, 'volume': 28000000, 'marketCap': '$2.6T'},
                {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 135.80, 'change': 0.95, 'changePercent': 0.70, 'volume': 32000000, 'marketCap': '$1.7T'},
                {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'price': 142.60, 'change': -2.10, 'changePercent': -1.45, 'volume': 45000000, 'marketCap': '$1.5T'}
            ],
            'japan': [
                {'ticker': '7203', 'name': 'Toyota Motor', 'price': 2850, 'change': 45, 'changePercent': 1.60, 'volume': 8500000, 'marketCap': '¥42조'},
                {'ticker': '6758', 'name': 'Sony Group', 'price': 12500, 'change': -180, 'changePercent': -1.42, 'volume': 2100000, 'marketCap': '¥15조'}
            ],
            'china': [
                {'ticker': '00700', 'name': 'Tencent', 'price': 365.50, 'change': -8.20, 'changePercent': -2.19, 'volume': 15000000, 'marketCap': 'HK$3.5T'},
                {'ticker': '09988', 'name': 'Alibaba', 'price': 98.50, 'change': 2.80, 'changePercent': 2.93, 'volume': 22000000, 'marketCap': 'HK$2.1T'}
            ],
            'europe': [
                {'ticker': 'ASML', 'name': 'ASML Holding', 'price': 685.50, 'change': 12.30, 'changePercent': 1.83, 'volume': 2100000, 'marketCap': '€280B'},
                {'ticker': 'SAP', 'name': 'SAP SE', 'price': 125.80, 'change': -2.40, 'changePercent': -1.87, 'volume': 1850000, 'marketCap': '€145B'}
            ]
        }
        
        stocks = stock_data.get(market_type, [])
        return jsonify({"success": True, "stocks": stocks})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/market/indices")
@login_required
def get_market_indices():
    """
    주요 지수 정보 조회
    """
    try:
        indices = {
            "kospi": {"value": 2500.00, "change": 10.50, "changePercent": 0.42},
            "kosdaq": {"value": 850.00, "change": -5.20, "changePercent": -0.61},
            "sp500": {"value": 4200.00, "change": -15.30, "changePercent": -0.36},
            "nasdaq": {"value": 13500.00, "change": -45.80, "changePercent": -0.34},
            "nikkei": {"value": 33500.00, "change": 120.50, "changePercent": 0.36},
            "hangseng": {"value": 17800.00, "change": -85.20, "changePercent": -0.48},
            "stoxx600": {"value": 456.80, "change": 2.40, "changePercent": 0.53}
        }
        return jsonify({"success": True, "indices": indices})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)