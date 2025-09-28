from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
from functools import wraps
from services.kis_api_service import get_domestic_stocks, get_overseas_stocks, get_all_market_indices, init_kis_api

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ✅ login_required 직접 정의 (DB 없이도 동작)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

# ✅ OAuth 설정
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'}
)

# ✅ 기본 페이지 라우팅
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

@app.route("/api/market/<market_type>")
@login_required
def get_market_stocks(market_type):
    """시장별 주식 데이터 조회 - 국내, 미국만 지원"""
    try:
        print(f"[DEBUG] 마켓 타입: {market_type} 데이터 요청")
        
        if market_type == "domestic":
            # 국내 주식 - 한국투자증권 API 사용
            result = get_domestic_stocks()
            print(f"[DEBUG] 국내 주식 응답: {len(result.get('stocks', []))}개 종목")
            return jsonify(result)
        
        elif market_type == "us":
            # 미국 주식 - 한국투자증권 API 사용
            result = get_overseas_stocks(market_type)
            print(f"[DEBUG] 미국 주식 응답: {len(result.get('stocks', []))}개 종목")
            return jsonify(result)
        
        else:
            return jsonify({"success": False, "message": "국내와 미국 시장만 지원됩니다"}), 400

    except Exception as e:
        print(f"[ERROR] 시장 데이터 조회 실패 ({market_type}): {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/market/indices")
@login_required
def get_market_indices_api():
    """시장 지수 데이터 조회 - 모든 지수에 KIS API 사용"""
    try:
        print("[DEBUG] === 지수 데이터 수신 시작 (KIS API) ===")
        
        # 모든 지수를 한국투자증권 API로 조회
        result = get_all_market_indices()
        
        if result.get("success"):
            print(f"[DEBUG] KIS API 지수 데이터: {list(result['indices'].keys())}")
            for name, data in result['indices'].items():
                print(f"[DEBUG] {name.upper()}: {data.get('value', 0)}, 변화: {data.get('change', 0)} ({data.get('changePercent', 0)}%)")
        else:
            print(f"[ERROR] 지수 조회 실패: {result.get('message', '알 수 없는 오류')}")
        
        print("[DEBUG] === 지수 데이터 수신 완료 ===")
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] 지수 데이터 조회 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    # Flask 2.0+에서는 before_first_request가 deprecated되었으므로 직접 호출
    with app.app_context():
        if not init_kis_api():
            print("⚠️  KIS API 초기화 실패 - .env 파일에 KIS_APP_KEY, KIS_APP_SECRET 설정 필요")
            print("📋 필요한 환경변수:")
            print("   KIS_APP_KEY=your_app_key")
            print("   KIS_APP_SECRET=your_app_secret")
    
    # 호스트와 포트 명시적 설정
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)