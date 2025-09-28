import requests
import json
import time
from datetime import datetime, timedelta
import os
from flask import jsonify
import pickle

class KISAPIService:
    """한국투자증권 Open API 서비스 - 실제 데이터만"""
    
    def __init__(self, app_key=None, app_secret=None):
        self.app_key = app_key or os.getenv("KIS_APP_KEY")
        self.app_secret = app_secret or os.getenv("KIS_APP_SECRET") 
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = None
        self.token_expired = None
        self.token_cache_file = ".kis_token_cache.pkl"
        self.last_token_request = None
        
        if not self.app_key or not self.app_secret:
            raise ValueError("KIS API 키가 설정되지 않았습니다. 환경변수 KIS_APP_KEY, KIS_APP_SECRET을 설정해주세요.")
        
        # 캐시된 토큰 로드 시도
        self.load_cached_token()
        
        # 토큰이 없거나 만료된 경우에만 새로 발급
        if not self.check_token_valid():
            self.get_access_token()
    
    def save_token_cache(self):
        """토큰을 캐시 파일로 저장"""
        try:
            cache_data = {
                'access_token': self.access_token,
                'token_expired': self.token_expired,
                'last_token_request': self.last_token_request
            }
            with open(self.token_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print("토큰 캐시 저장 완료")
        except Exception as e:
            print(f"토큰 캐시 저장 실패: {e}")
    
    def load_cached_token(self):
        """캐시된 토큰을 로드"""
        try:
            if os.path.exists(self.token_cache_file):
                with open(self.token_cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                self.access_token = cache_data.get('access_token')
                self.token_expired = cache_data.get('token_expired')
                self.last_token_request = cache_data.get('last_token_request')
                
                # 토큰이 여전히 유효한지 확인
                if self.token_expired and datetime.now() < self.token_expired:
                    print("캐시된 토큰 로드 성공")
                    return True
                else:
                    print("캐시된 토큰이 만료됨")
                    
        except Exception as e:
            print(f"토큰 캐시 로드 실패: {e}")
        
        return False
    
    def get_access_token(self):
        """액세스 토큰 발급 - 재시도 로직 포함"""
        # 1분 제한 확인
        if self.last_token_request:
            time_since_last = datetime.now() - self.last_token_request
            if time_since_last.total_seconds() < 60:
                wait_time = 61 - time_since_last.total_seconds()
                print(f"토큰 발급 제한으로 {wait_time:.0f}초 대기 중...")
                time.sleep(wait_time)
        
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            headers = {"Content-Type": "application/json"}
            data = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            print("KIS API 토큰 발급 요청 중...")
            self.last_token_request = datetime.now()
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()
            
            if response.status_code == 200 and result.get("access_token"):
                self.access_token = result["access_token"]
                # 토큰 만료시간 설정 (보통 24시간)
                self.token_expired = datetime.now() + timedelta(hours=23)
                
                # 캐시에 저장
                self.save_token_cache()
                
                print("✅ KIS API 토큰 발급 성공")
                return True
            else:
                error_code = result.get("error_code", "")
                error_desc = result.get("error_description", "")
                
                if error_code == "EGW00133":  # 1분당 1회 제한
                    print("⏳ 토큰 발급 제한 (1분당 1회) - 60초 후 재시도...")
                    time.sleep(61)
                    return self.get_access_token()  # 재귀 호출
                else:
                    print(f"❌ 토큰 발급 실패: {error_desc} ({error_code})")
                    return False
                
        except Exception as e:
            print(f"❌ 토큰 발급 중 오류: {e}")
            return False
    
    def check_token_valid(self):
        """토큰 유효성 확인 및 갱신"""
        if not self.access_token or not self.token_expired:
            return False
        
        if datetime.now() >= self.token_expired:
            print("토큰이 만료되어 새로 발급합니다...")
            return self.get_access_token()
        
        return True
    
    def get_stock_price(self, stock_code):
        """개별 주식 현재가 조회"""
        if not self.check_token_valid():
            return None
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"  # 주식현재가 시세
            }
            params = {
                "fid_cond_mrkt_div_code": "J",  # 시장분류코드 (J:주식)
                "fid_input_iscd": stock_code     # 종목코드
            }
            
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("rt_cd") == "0":
                output = result.get("output", {})
                return {
                    "ticker": stock_code,
                    "name": output.get("hts_kor_isnm", ""),  # 종목명
                    "price": int(output.get("stck_prpr", 0)),  # 현재가
                    "change": int(output.get("prdy_vrss", 0)),  # 전일대비
                    "changePercent": float(output.get("prdy_ctrt", 0)),  # 전일대비율
                    "volume": int(output.get("acml_vol", 0)),  # 누적거래량
                    "high": int(output.get("stck_hgpr", 0)),   # 최고가
                    "low": int(output.get("stck_lwpr", 0)),    # 최저가
                    "open": int(output.get("stck_oprc", 0)),   # 시가
                    "marketCap": self.format_market_cap(output.get("lstn_stcn", 0), int(output.get("stck_prpr", 0)))
                }
            else:
                print(f"주식 현재가 조회 실패: {result}")
                return None
                
        except Exception as e:
            print(f"주식 현재가 조회 중 오류: {e}")
            return None
    
    def get_multiple_stock_prices(self, stock_codes):
        """여러 주식의 현재가를 한번에 조회"""
        results = []
        
        for code in stock_codes:
            stock_data = self.get_stock_price(code)
            if stock_data:
                results.append(stock_data)
            time.sleep(0.1)  # API 호출 제한 방지
        
        return results
    
    def get_overseas_stock_price(self, symbol, market_code="NAS"):
        """해외 주식 현재가 조회"""
        if not self.check_token_valid():
            return None
        
        try:
            url = f"{self.base_url}/uapi/overseas-price/v1/quotations/price"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "HHDFS00000300"  # 해외주식 현재가
            }
            params = {
                "AUTH": "",
                "EXCD": market_code,  # 거래소코드 (NAS:나스닥, NYS:뉴욕, HKS:홍콩, TYO:도쿄 등)
                "SYMB": symbol       # 종목심볼
            }
            
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("rt_cd") == "0":
                output = result.get("output", {})
                current_price = float(output.get("last", 0))
                prev_close = float(output.get("base", 0))
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                
                return {
                    "ticker": symbol,
                    "name": output.get("name", symbol),
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2),
                    "volume": int(float(output.get("tvol", 0))),  # 거래량
                    "high": float(output.get("high", 0)),         # 최고가
                    "low": float(output.get("low", 0)),           # 최저가
                    "open": float(output.get("open", 0)),         # 시가
                    "marketCap": "-"
                }
            else:
                print(f"해외주식 현재가 조회 실패 ({symbol}): {result}")
                return None
                
        except Exception as e:
            print(f"해외주식 현재가 조회 중 오류 ({symbol}): {e}")
            return None
    
    def get_kospi_index(self):
        """코스피 지수 조회"""
        if not self.check_token_valid():
            return None
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-index-price"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHPUP02100000"  # 지수현재가 시세
            }
            params = {
                "fid_cond_mrkt_div_code": "U",  # 시장분류코드
                "fid_input_iscd": "0001"        # 코스피 지수코드
            }
            
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("rt_cd") == "0":
                output = result.get("output", {})
                return {
                    "name": "코스피",
                    "value": float(output.get("bstp_nmix_prpr", 0)),      # 현재지수
                    "change": float(output.get("bstp_nmix_prdy_vrss", 0)), # 전일대비
                    "changePercent": float(output.get("prdy_vrss_sign", 0)) # 전일대비율
                }
            
        except Exception as e:
            print(f"코스피 지수 조회 중 오류: {e}")
        
        return None
    
    def get_kosdaq_index(self):
        """코스닥 지수 조회"""
        if not self.check_token_valid():
            return None
        
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-index-price"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHPUP02100000"
            }
            params = {
                "fid_cond_mrkt_div_code": "U",
                "fid_input_iscd": "1001"        # 코스닥 지수코드
            }
            
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("rt_cd") == "0":
                output = result.get("output", {})
                return {
                    "name": "코스닥",
                    "value": float(output.get("bstp_nmix_prpr", 0)),
                    "change": float(output.get("bstp_nmix_prdy_vrss", 0)),
                    "changePercent": float(output.get("prdy_vrss_sign", 0))
                }
            
        except Exception as e:
            print(f"코스닥 지수 조회 중 오류: {e}")
        
        return None
    
    def get_dow_jones_index(self):
        """다우존스 지수 조회"""
        if not self.check_token_valid():
            return None
        
        try:
            url = f"{self.base_url}/uapi/overseas-price/v1/quotations/price"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHPUP02100000"
            }
            params = {
                "AUTH": "",
                "EXCD": "NYS",
                "SYMB": "DJI"  # 다우존스 심볼
            }
            
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200 and result.get("rt_cd") == "0":
                output = result.get("output", {})
                current_value = float(output.get("last", 0))
                prev_close = float(output.get("base", 0))
                change = current_value - prev_close
                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                
                return {
                    "name": "다우존스",
                    "value": round(current_value, 2),
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2)
                }
                
        except Exception as e:
            print(f"다우존스 지수 조회 중 오류: {e}")
        
        return None
    
    def get_nasdaq_index(self):
        """
        나스닥 지수 조회 (TR: HHDFS00000300)
        - KIS 내부 코드(PCOMP)를 사용하여 공식 심볼(IXIC)의 0 반환 문제를 우회합니다.
        - API가 0을 반환할 경우 경고를 출력합니다.
        """
        if not self.check_token_valid():
            return None
        
        NASDAQ_SYMBOL = "PCOMP" # KIS 해외 마스터 파일 기반 나스닥 종합지수 코드
        
        try:
            print(f"[DEBUG] 나스닥 지수 조회 재시도 (TR: HHDFS00000300, Symbol: {NASDAQ_SYMBOL})...")
            
            url = f"{self.base_url}/uapi/overseas-price/v1/quotations/price"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self.access_token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "HHDFS00000300"
            }
            params = {
                "AUTH": "",
                "EXCD": "NAS",  
                "SYMB": NASDAQ_SYMBOL
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"[ERROR] 나스닥 지수 API HTTP 오류: Status Code {response.status_code}")
                return None
            
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                print(f"[CRITICAL ERROR] JSON 디코딩 실패: {e}")
                return None
            
            print(f"[DEBUG] 나스닥 지수 API 응답: rt_cd={result.get('rt_cd', 'N/A')}")

            if result.get("rt_cd") == "0":
                output = result.get("output", {})
                
                current_value = float(output.get("last", 0) or 0)
                prev_close = float(output.get("base", 0) or 0)
                
                change = current_value - prev_close
                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                
                if current_value > 0:
                    result_data = {
                        "name": "나스닥 종합지수 (PCOMP)",
                        "value": round(current_value, 2),
                        "change": round(change, 2),
                        "changePercent": round(change_percent, 2)
                    }
                    print(f"[SUCCESS] 나스닥 지수 성공")
                    return result_data
                else:
                    print(f"[WARNING] 나스닥 지수 데이터가 유효하지 않음 (value=0). PCOMP도 실패.")
                    # 시장 폐장 시 0이 반환될 수 있으므로, 전일 종가를 반환하는 로직을 추가할 수도 있음
                    if prev_close > 0:
                         print(f"[INFO] 전일 종가({prev_close})는 유효. 시장 폐장으로 추정.")
                    return None
            else:
                error_msg = result.get("msg1", "알 수 없는 오류")
                print(f"[ERROR] 나스닥 지수 API 실패 (rt_cd={result.get('rt_cd')}): {error_msg}")
                return None
                
        except Exception as e:
            print(f"[FATAL ERROR] 나스닥 지수 조회 중 오류: {e}")
            return None
    
    @staticmethod
    def format_market_cap(listed_shares, current_price):
        """시가총액 포맷팅"""
        try:
            if not listed_shares or not current_price:
                return "-"
            
            market_cap = int(listed_shares) * current_price
            if market_cap >= 1000000000000:  # 1조 이상
                return f"{market_cap // 1000000000000}조"
            elif market_cap >= 100000000:   # 1억 이상
                return f"{market_cap // 100000000}억"
            else:
                return "-"
        except:
            return "-"


# Flask 앱에서 사용할 인스턴스 생성
kis_api = None

def init_kis_api():
    """KIS API 초기화"""
    global kis_api
    try:
        kis_api = KISAPIService()
        return True
    except Exception as e:
        print(f"KIS API 초기화 실패: {e}")
        return False

def get_domestic_stocks():
    """국내 주요 종목 현재가 조회"""
    global kis_api
    
    if not kis_api:
        if not init_kis_api():
            return {"success": False, "message": "API 초기화 실패"}
    
    # 주요 종목 코드들
    major_stocks = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스  
        "035420",  # NAVER
        "005380",  # 현대차
        "006400",  # 삼성SDI
        "051910",  # LG화학
        "068270",  # 셀트리온
        "035720",  # 카카오
        "207940",  # 삼성바이오로직스
        "373220"   # LG에너지솔루션
    ]
    
    try:
        stocks_data = kis_api.get_multiple_stock_prices(major_stocks)
        return {"success": True, "stocks": stocks_data}
    except Exception as e:
        print(f"국내 주식 데이터 조회 실패: {e}")
        return {"success": False, "message": str(e)}

def get_overseas_stocks(market_type):
    """해외 주식 데이터 조회 - 미국만 지원"""
    global kis_api
    
    if not kis_api:
        if not init_kis_api():
            return {"success": False, "message": "API 초기화 실패"}
    
    # 미국 주요 종목들만
    if market_type == "us":
        us_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corp."},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corp."},
            {"symbol": "META", "name": "Meta Platforms"},
            {"symbol": "NFLX", "name": "Netflix Inc."},
            {"symbol": "AMD", "name": "Advanced Micro Devices"},
            {"symbol": "CRM", "name": "Salesforce Inc."}
        ]
        
        try:
            stocks_data = []
            for stock_info in us_stocks:
                stock_data = kis_api.get_overseas_stock_price(
                    stock_info["symbol"], 
                    "NAS"  # 나스닥 거래소 코드
                )
                if stock_data:
                    # 한국어 이름으로 덮어쓰기
                    stock_data["name"] = stock_info["name"]
                    stocks_data.append(stock_data)
                time.sleep(0.1)  # API 호출 제한 방지
            
            return {"success": True, "stocks": stocks_data}
            
        except Exception as e:
            print(f"미국 주식 데이터 조회 실패: {e}")
            return {"success": False, "message": str(e)}
    
    else:
        return {"success": False, "message": "미국 시장만 지원됩니다"}

def get_all_market_indices():
    """모든 시장 지수 조회 - 국내 + 미국만"""
    global kis_api
    
    if not kis_api:
        if not init_kis_api():
            return {"success": False, "message": "API 초기화 실패"}
    
    try:
        indices = {}
        
        # 국내 지수 (코스피, 코스닥)
        kospi_data = kis_api.get_kospi_index()
        kosdaq_data = kis_api.get_kosdaq_index()
        
        if kospi_data:
            indices["kospi"] = kospi_data
        if kosdaq_data:
            indices["kosdaq"] = kosdaq_data
        
        # 미국 지수 (다우존스, 나스닥)
        dow_data = kis_api.get_dow_jones_index()
        nasdaq_data = kis_api.get_nasdaq_index()
        
        if dow_data:
            indices["dow"] = dow_data
        if nasdaq_data:
            indices["nasdaq"] = nasdaq_data
            
        return {"success": True, "indices": indices}
        
    except Exception as e:
        print(f"시장 지수 조회 실패: {e}")
        return {"success": False, "message": str(e)}