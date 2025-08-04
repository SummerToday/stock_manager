import requests
import json
import time
from datetime import datetime
import random

# 실시간 주가 데이터 시뮬레이션
STOCK_DATA = {
    'domestic': [
        {'ticker': '005930', 'name': '삼성전자', 'price': 75000, 'change': 500, 'changePercent': 0.67, 'volume': 15000000, 'marketCap': '448조'},
        {'ticker': '000660', 'name': 'SK하이닉스', 'price': 120000, 'change': -2000, 'changePercent': -1.64, 'volume': 8500000, 'marketCap': '87조'},
        {'ticker': '035420', 'name': 'NAVER', 'price': 205000, 'change': 3500, 'changePercent': 1.74, 'volume': 1200000, 'marketCap': '34조'},
        {'ticker': '005380', 'name': '현대차', 'price': 180000, 'change': -1500, 'changePercent': -0.83, 'volume': 2100000, 'marketCap': '38조'},
        {'ticker': '006400', 'name': '삼성SDI', 'price': 680000, 'change': 15000, 'changePercent': 2.26, 'volume': 450000, 'marketCap': '31조'},
        {'ticker': '051910', 'name': 'LG화학', 'price': 850000, 'change': -8000, 'changePercent': -0.93, 'volume': 320000, 'marketCap': '60조'},
        {'ticker': '068270', 'name': '셀트리온', 'price': 195000, 'change': 2800, 'changePercent': 1.46, 'volume': 1800000, 'marketCap': '26조'},
        {'ticker': '035720', 'name': '카카오', 'price': 68500, 'change': -1200, 'changePercent': -1.72, 'volume': 3200000, 'marketCap': '25조'},
        {'ticker': '207940', 'name': '삼성바이오로직스', 'price': 780000, 'change': 12000, 'changePercent': 1.56, 'volume': 85000, 'marketCap': '112조'},
        {'ticker': '373220', 'name': 'LG에너지솔루션', 'price': 450000, 'change': -5500, 'changePercent': -1.21, 'volume': 650000, 'marketCap': '107조'}
    ],
    'us': [
        {'ticker': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'change': 2.30, 'changePercent': 1.33, 'volume': 55000000, 'marketCap': '$2.7T'},
        {'ticker': 'MSFT', 'name': 'Microsoft Corp.', 'price': 345.20, 'change': -1.80, 'changePercent': -0.52, 'volume': 28000000, 'marketCap': '$2.6T'},
        {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 135.80, 'change': 0.95, 'changePercent': 0.70, 'volume': 32000000, 'marketCap': '$1.7T'},
        {'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'price': 142.60, 'change': -2.10, 'changePercent': -1.45, 'volume': 45000000, 'marketCap': '$1.5T'},
        {'ticker': 'TSLA', 'name': 'Tesla Inc.', 'price': 245.80, 'change': 8.70, 'changePercent': 3.67, 'volume': 85000000, 'marketCap': '$780B'},
        {'ticker': 'NVDA', 'name': 'NVIDIA Corp.', 'price': 520.30, 'change': 15.20, 'changePercent': 3.01, 'volume': 42000000, 'marketCap': '$1.3T'},
        {'ticker': 'META', 'name': 'Meta Platforms', 'price': 385.90, 'change': -5.40, 'changePercent': -1.38, 'volume': 18000000, 'marketCap': '$980B'},
        {'ticker': 'NFLX', 'name': 'Netflix Inc.', 'price': 465.20, 'change': 12.80, 'changePercent': 2.83, 'volume': 15000000, 'marketCap': '$205B'},
        {'ticker': 'AMD', 'name': 'Advanced Micro Devices', 'price': 115.40, 'change': -3.20, 'changePercent': -2.70, 'volume': 38000000, 'marketCap': '$186B'},
        {'ticker': 'CRM', 'name': 'Salesforce Inc.', 'price': 215.60, 'change': 4.50, 'changePercent': 2.13, 'volume': 8500000, 'marketCap': '$214B'}
    ],
    'japan': [
        {'ticker': '7203', 'name': 'Toyota Motor', 'price': 2850, 'change': 45, 'changePercent': 1.60, 'volume': 8500000, 'marketCap': '¥42조'},
        {'ticker': '6758', 'name': 'Sony Group', 'price': 12500, 'change': -180, 'changePercent': -1.42, 'volume': 2100000, 'marketCap': '¥15조'},
        {'ticker': '9984', 'name': 'SoftBank Group', 'price': 6200, 'change': 120, 'changePercent': 1.97, 'volume': 3200000, 'marketCap': '¥13조'},
        {'ticker': '6861', 'name': 'Keyence', 'price': 65000, 'change': -800, 'changePercent': -1.22, 'volume': 450000, 'marketCap': '¥12조'},
        {'ticker': '4063', 'name': 'Shin-Etsu Chemical', 'price': 18500, 'change': 250, 'changePercent': 1.37, 'volume': 1200000, 'marketCap': '¥8조'},
        {'ticker': '8035', 'name': 'Tokyo Electron', 'price': 22000, 'change': -350, 'changePercent': -1.57, 'volume': 890000, 'marketCap': '¥7조'},
        {'ticker': '6098', 'name': 'Recruit Holdings', 'price': 4800, 'change': 85, 'changePercent': 1.80, 'volume': 1800000, 'marketCap': '¥8조'},
        {'ticker': '8306', 'name': 'Mitsubishi UFJ Financial', 'price': 950, 'change': -15, 'changePercent': -1.55, 'volume': 45000000, 'marketCap': '¥12조'}
    ],
    'china': [
        {'ticker': '00700', 'name': 'Tencent', 'price': 365.50, 'change': -8.20, 'changePercent': -2.19, 'volume': 15000000, 'marketCap': 'HK$3.5T'},
        {'ticker': '09988', 'name': 'Alibaba', 'price': 98.50, 'change': 2.80, 'changePercent': 2.93, 'volume': 22000000, 'marketCap': 'HK$2.1T'},
        {'ticker': '01024', 'name': 'Kuaishou', 'price': 68.20, 'change': -1.50, 'changePercent': -2.15, 'volume': 8500000, 'marketCap': 'HK$295B'},
        {'ticker': '03690', 'name': 'Meituan', 'price': 125.30, 'change': 3.70, 'changePercent': 3.04, 'volume': 12000000, 'marketCap': 'HK$775B'},
        {'ticker': '02318', 'name': 'Ping An Insurance', 'price': 45.80, 'change': -0.90, 'changePercent': -1.93, 'volume': 18000000, 'marketCap': 'HK$837B'},
        {'ticker': '00175', 'name': 'Geely Automobile', 'price': 12.50, 'change': 0.35, 'changePercent': 2.88, 'volume': 25000000, 'marketCap': 'HK$136B'},
        {'ticker': '01211', 'name': 'BYD Company', 'price': 245.60, 'change': 8.40, 'changePercent': 3.54, 'volume': 12000000, 'marketCap': 'HK$715B'},
        {'ticker': '00981', 'name': 'SMIC', 'price': 22.50, 'change': -0.85, 'changePercent': -3.64, 'volume': 35000000, 'marketCap': 'HK$179B'}
    ],
    'europe': [
        {'ticker': 'ASML', 'name': 'ASML Holding', 'price': 685.50, 'change': 12.30, 'changePercent': 1.83, 'volume': 2100000, 'marketCap': '€280B'},
        {'ticker': 'SAP', 'name': 'SAP SE', 'price': 125.80, 'change': -2.40, 'changePercent': -1.87, 'volume': 1850000, 'marketCap': '€145B'},
        {'ticker': 'LVMH', 'name': 'LVMH', 'price': 780.20, 'change': 15.60, 'changePercent': 2.04, 'volume': 850000, 'marketCap': '€390B'},
        {'ticker': 'TTE', 'name': 'TotalEnergies', 'price': 58.90, 'change': -1.10, 'changePercent': -1.83, 'volume': 3200000, 'marketCap': '€155B'},
        {'ticker': 'NVO', 'name': 'Novo Nordisk', 'price': 105.30, 'change': 2.80, 'changePercent': 2.73, 'volume': 1200000, 'marketCap': '€485B'},
        {'ticker': 'UNA', 'name': 'Unilever', 'price': 48.50, 'change': -0.75, 'changePercent': -1.52, 'volume': 2800000, 'marketCap': '€120B'},
        {'ticker': 'NESN', 'name': 'Nestle SA', 'price': 108.50, 'change': 1.20, 'changePercent': 1.12, 'volume': 2100000, 'marketCap': '€315B'},
        {'ticker': 'RMS', 'name': 'Hermes International', 'price': 1950.00, 'change': 25.50, 'changePercent': 1.32, 'volume': 125000, 'marketCap': '€205B'}
    ]
}

def get_market_data(market_type):
    """
    특정 시장의 주식 데이터를 반환
    
    Args:
        market_type (str): 'domestic', 'us', 'japan', 'china', 'europe'
    
    Returns:
        list: 주식 데이터 리스트
    """
    try:
        if market_type not in STOCK_DATA:
            raise ValueError(f"지원하지 않는 시장 타입: {market_type}")
        
        # 실시간 가격 변동 시뮬레이션
        stocks = []
        for stock in STOCK_DATA[market_type]:
            # 복사본 생성
            stock_copy = stock.copy()
            
            # 랜덤 가격 변동 적용 (±2%)
            price_variation = random.uniform(-0.02, 0.02)
            new_price = stock_copy['price'] * (1 + price_variation)
            
            # 변동량 계산
            change = new_price - stock_copy['price']
            change_percent = (change / stock_copy['price']) * 100
            
            stock_copy.update({
                'price': round(new_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'timestamp': datetime.now().isoformat(),
                'market': market_type
            })
            
            stocks.append(stock_copy)
        
        return stocks
        
    except Exception as e:
        print(f"시장 데이터 조회 중 오류: {e}")
        return []

def get_stock_price(ticker, market_type='domestic'):
    """
    특정 종목의 현재가 정보를 반환
    
    Args:
        ticker (str): 종목 코드
        market_type (str): 시장 타입
    
    Returns:
        dict: 주식 가격 정보
    """
    try:
        market_stocks = get_market_data(market_type)
        
        for stock in market_stocks:
            if stock['ticker'] == ticker:
                return {
                    'ticker': stock['ticker'],
                    'name': stock['name'],
                    'price': stock['price'],
                    'change': stock['change'],
                    'changePercent': stock['changePercent'],
                    'volume': stock['volume'],
                    'marketCap': stock['marketCap'],
                    'timestamp': stock['timestamp'],
                    'market': market_type
                }
        
        raise ValueError(f"종목을 찾을 수 없습니다: {ticker}")
        
    except Exception as e:
        print(f"주식 가격 조회 중 오류: {e}")
        return None

def get_real_time_data(tickers, market_type='domestic'):
    """
    여러 종목의 실시간 데이터를 한번에 조회
    
    Args:
        tickers (list): 종목 코드 리스트
        market_type (str): 시장 타입
    
    Returns:
        dict: 종목별 실시간 데이터
    """
    try:
        result = {}
        market_stocks = get_market_data(market_type)
        
        for ticker in tickers:
            for stock in market_stocks:
                if stock['ticker'] == ticker:
                    result[ticker] = stock
                    break
        
        return result
        
    except Exception as e:
        print(f"실시간 데이터 조회 중 오류: {e}")
        return {}

def search_stocks(query, market_type='all'):
    """
    종목 검색
    
    Args:
        query (str): 검색어
        market_type (str): 검색할 시장 ('all', 'domestic', 'us', etc.)
    
    Returns:
        list: 검색 결과
    """
    try:
        results = []
        query = query.upper().strip()
        
        markets_to_search = [market_type] if market_type != 'all' else STOCK_DATA.keys()
        
        for market in markets_to_search:
            if market in STOCK_DATA:
                for stock in STOCK_DATA[market]:
                    if (query in stock['ticker'].upper() or 
                        query in stock['name'].upper()):
                        
                        result_stock = stock.copy()
                        result_stock['market'] = market
                        results.append(result_stock)
        
        return results[:20]  # 최대 20개 결과만 반환
        
    except Exception as e:
        print(f"종목 검색 중 오류: {e}")
        return []

def get_market_status():
    """
    각 시장의 현재 상태를 반환
    
    Returns:
        dict: 시장별 상태 정보
    """
    try:
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # 간단한 시장 시간 시뮬레이션
        status = {
            'domestic': {
                'isOpen': 9 <= current_hour < 15,  # 한국 시장 9-15시
                'status': '장중' if 9 <= current_hour < 15 else '장마감',
                'nextOpen': '09:00' if current_hour >= 15 else None,
                'timezone': 'KST'
            },
            'us': {
                'isOpen': 22 <= current_hour or current_hour < 5,  # 미국 시장 (한국시간 22-05시)
                'status': '장중' if 22 <= current_hour or current_hour < 5 else '장마감',
                'nextOpen': '22:30' if 5 <= current_hour < 22 else None,
                'timezone': 'EST'
            },
            'japan': {
                'isOpen': 9 <= current_hour < 15,  # 일본 시장
                'status': '장중' if 9 <= current_hour < 15 else '장마감',
                'nextOpen': '09:00' if current_hour >= 15 else None,
                'timezone': 'JST'
            },
            'china': {
                'isOpen': 10 <= current_hour < 16,  # 중국 시장 (한국시간 기준)
                'status': '장중' if 10 <= current_hour < 16 else '장마감',
                'nextOpen': '10:30' if current_hour >= 16 else None,
                'timezone': 'CST'
            },
            'europe': {
                'isOpen': 17 <= current_hour < 1,  # 유럽 시장 (한국시간 기준)
                'status': '장중' if 17 <= current_hour or current_hour < 1 else '장마감',
                'nextOpen': '17:00' if 1 <= current_hour < 17 else None,
                'timezone': 'CET'
            }
        }
        
        return status
        
    except Exception as e:
        print(f"시장 상태 조회 중 오류: {e}")
        return {}

# 실제 운영환경에서는 아래와 같은 외부 API 연동 함수들을 사용할 수 있습니다.

def fetch_real_stock_data_korea(ticker):
    """
    한국투자증권 API 또는 다른 실시간 데이터 제공업체 연동
    실제 구현시 API 키와 인증이 필요합니다.
    """
    # 예시 - 실제로는 외부 API 호출
    # url = f"https://api.koreainvestment.com/stock/{ticker}"
    # headers = {"Authorization": "Bearer YOUR_API_KEY"}
    # response = requests.get(url, headers=headers)
    # return response.json()
    pass

def fetch_real_stock_data_us(ticker):
    """
    Alpha Vantage, Yahoo Finance API 등을 통한 미국 주식 데이터 연동
    """
    # 예시 - 실제로는 외부 API 호출
    # api_key = "YOUR_ALPHA_VANTAGE_API_KEY"
    # url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    # response = requests.get(url)
    # return response.json()
    pass