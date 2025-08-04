from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
import yfinance as yf
from functools import wraps

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
    try:
        market_tickers = {
            "us": ["AAPL", "MSFT", "GOOGL", "AMZN"],
            "domestic": ["005930.KS", "000660.KS", "035420.KQ", "005380.KS"]
        }

        domestic_names = {
            "005930": "삼성전자",
            "000660": "SK하이닉스",
            "035420": "NAVER",
            "005380": "현대차"
        }

        tickers = market_tickers.get(market_type, [])
        if not tickers:
            return jsonify({"success": True, "stocks": []})

        print(f"[DEBUG] 요청된 마켓 타입: {market_type}")
        print(f"[DEBUG] 사용 티커 목록: {tickers}")

        # 15분봉 사용
        data = yf.download(tickers=tickers, period="1d", interval="15m", threads=True, group_by='ticker')
        print("[DEBUG] 데이터 수신 완료")

        stocks = []
        for ticker in tickers:
            try:
                df = data[ticker]
                close = df['Close'].dropna()
                if len(close) < 2:
                    print(f"[WARN] {ticker} 데이터 부족")
                    continue

                price = round(close.iloc[-1], 2)
                change = round(price - close.iloc[-2], 2)
                change_percent = round((change / close.iloc[-2]) * 100, 2)
                volume = int(df["Volume"].dropna().iloc[-1])

                symbol = ticker.replace(".KS", "").replace(".KQ", "")
                name = domestic_names.get(symbol, symbol) if market_type == "domestic" else symbol

                stocks.append({
                    "ticker": symbol,
                    "name": name,
                    "price": price,
                    "change": change,
                    "changePercent": change_percent,
                    "volume": volume,
                    "marketCap": "-"
                })
            except Exception as e:
                print(f"[ERROR] {ticker} 처리 중 오류: {e}")
                continue

        return jsonify({"success": True, "stocks": stocks})
    except Exception as e:
        print(f"[ERROR] 전체 처리 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/market/indices")
@login_required
def get_market_indices():
    try:
        print("[DEBUG] === 지수 데이터 수신 시작 ===")
        
        index_tickers = {
            "kospi": "^KS11",
            "kosdaq": "^KQ11",
            "sp500": "^GSPC",
            "nasdaq": "^IXIC"
        }

        result = {}
        for name, ticker in index_tickers.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d", interval="1m")  # 최근 2일치 1분봉

                if hist.empty:
                    print(f"[WARN] {ticker} 데이터 없음")
                    continue

                last_valid = hist["Close"].dropna().iloc[-1]
                prev_close = hist["Close"].dropna().iloc[-2]

                change = last_valid - prev_close
                change_percent = (change / prev_close * 100) if prev_close else 0

                # 시간 차 계산
                last_timestamp = hist.index[-1]
                from datetime import datetime, timezone
                now_utc = datetime.now(timezone.utc)
                minutes_ago = int((now_utc - last_timestamp).total_seconds() // 60)

                print(f"[DEBUG] {name.upper()} ({ticker})")
                print(f"         현재가: {last_valid}, 전일종가: {prev_close}")
                print(f"         변화량: {change}, 변동률: {change_percent}%")

                result[name] = {
                    "value": float(round(last_valid, 2)),
                    "change": float(round(change, 2)),
                    "changePercent": float(round(change_percent, 2)),
                    "timeDiffMinutes": minutes_ago
                }

            except Exception as e:
                print(f"[WARN] {ticker} 지수 오류:", e)
                continue

        print("[DEBUG] 지수 응답 결과:", result)
        print("[DEBUG] === 지수 데이터 수신 완료 ===")
        return jsonify({"success": True, "indices": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)
