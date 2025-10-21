import json
import datetime
import requests
import time
import os
import logging
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_us_stock_data(api_key):
    """미국 주식 데이터 수집"""
    try:
        # S&P 500 주요 종목들
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ']
        stocks = {}
        
        for symbol in symbols:
            try:
                # Alpha Vantage Global Quote API
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
                response = requests.get(url)
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    stocks[symbol] = {
                        'symbol': symbol,
                        'price': float(quote.get('05. price', 0)),
                        'change': float(quote.get('09. change', 0)),
                        'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                        'volume': int(quote.get('06. volume', 0))
                    }
                
                time.sleep(12)  # API 제한 고려
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue
                
        return stocks
        
    except Exception as e:
        logger.error(f"Error in fetch_us_stock_data: {e}")
        return {}

def fetch_crypto_data():
    """암호화폐 데이터 수집"""
    try:
        # CoinGecko API (무료)
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,solana&vs_currencies=usd&include_24hr_change=true'
        response = requests.get(url)
        data = response.json()
        
        crypto = {}
        crypto_names = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'binancecoin': 'BNB',
            'cardano': 'ADA',
            'solana': 'SOL'
        }
        
        for coin_id, symbol in crypto_names.items():
            if coin_id in data:
                coin_data = data[coin_id]
                crypto[symbol] = {
                    'symbol': symbol,
                    'price': coin_data.get('usd', 0),
                    'change_24h': coin_data.get('usd_24h_change', 0)
                }
                
        return crypto
        
    except Exception as e:
        logger.error(f"Error in fetch_crypto_data: {e}")
        return {}

def fetch_korean_market_data():
    """한국 시장 데이터 수집"""
    try:
        # 한국 대표 주식들 (예시 데이터 - 실제 API 연결 시 업데이트)
        korean_stocks = {
            '005930': {'name': '삼성전자', 'price': 58000, 'change': -1000, 'change_percent': '-1.69'},
            '000660': {'name': 'SK하이닉스', 'price': 89000, 'change': 2000, 'change_percent': '2.30'},
            '035420': {'name': 'NAVER', 'price': 145000, 'change': -3000, 'change_percent': '-2.03'},
            '051910': {'name': 'LG화학', 'price': 280000, 'change': 5000, 'change_percent': '1.82'},
            '006400': {'name': '삼성SDI', 'price': 320000, 'change': -8000, 'change_percent': '-2.44'}
        }
        
        return korean_stocks
        
    except Exception as e:
        logger.error(f"Error in fetch_korean_market_data: {e}")
        return {}

def fetch_global_indices():
    """글로벌 지수 데이터 수집"""
    try:
        indices = {
            'SPX': {'name': 'S&P 500', 'value': 5800.0, 'change': 15.5, 'change_percent': '0.27'},
            'IXIC': {'name': 'NASDAQ', 'value': 18500.0, 'change': 85.2, 'change_percent': '0.46'},
            'DJI': {'name': 'Dow Jones', 'value': 43000.0, 'change': -120.3, 'change_percent': '-0.28'},
            'KS11': {'name': 'KOSPI', 'value': 2420.0, 'change': -15.8, 'change_percent': '-0.65'},
            'KQ11': {'name': 'KOSDAQ', 'value': 680.0, 'change': -8.2, 'change_percent': '-1.19'}
        }
        
        return indices
        
    except Exception as e:
        logger.error(f"Error in fetch_global_indices: {e}")
        return {}

def generate_country_data():
    """국가별 경제 데이터 생성"""
    countries = [
        {
            'name': '미국',
            'flag': '🇺🇸',
            'growth_rate': 2.8,
            'inflation': 3.2,
            'interest_rate': 5.5,
            'representative_company': 'Apple (AAPL)',
            'sector': '기술',
            'market_impact': 90,
            'description': 'AI 기술 혁신과 소비 회복세'
        },
        {
            'name': '중국',
            'flag': '🇨🇳',
            'growth_rate': 4.5,
            'inflation': 0.8,
            'interest_rate': 3.8,
            'representative_company': 'Alibaba (BABA)',
            'sector': '전자상거래',
            'market_impact': 75,
            'description': '부동산 조정과 수출 회복'
        },
        {
            'name': '한국',
            'flag': '🇰🇷',
            'growth_rate': 1.8,
            'inflation': 2.3,
            'interest_rate': 3.5,
            'representative_company': '삼성전자 (005930)',
            'sector': '반도체',
            'market_impact': 65,
            'description': '반도체 회복과 내수 부진'
        },
        {
            'name': '일본',
            'flag': '🇯🇵',
            'growth_rate': 1.2,
            'inflation': 2.8,
            'interest_rate': 0.1,
            'representative_company': 'Toyota (TM)',
            'sector': '자동차',
            'market_impact': 60,
            'description': '엔화 약세와 수출 증가'
        },
        {
            'name': '독일',
            'flag': '🇩🇪',
            'growth_rate': 0.8,
            'inflation': 4.1,
            'interest_rate': 4.5,
            'representative_company': 'SAP (SAP)',
            'sector': '소프트웨어',
            'market_impact': 55,
            'description': '제조업 둔화와 에너지 전환'
        }
    ]
    
    return countries

def generate_stock_themes():
    """주식 테마 데이터 생성"""
    themes = [
        {
            'name': 'AI & 반도체',
            'performance': 28.5,
            'stocks': ['NVDA', 'AMD', 'INTC', 'TSM', '005930'],
            'description': 'AI 혁명과 반도체 슈퍼사이클'
        },
        {
            'name': '클린에너지',
            'performance': 15.2,
            'stocks': ['TSLA', 'ENPH', 'FSLR', 'NIO', '003670'],
            'description': '탄소중립과 재생에너지 확산'
        },
        {
            'name': '헬스케어',
            'performance': 12.8,
            'stocks': ['JNJ', 'PFE', 'ABBV', 'UNH', '207940'],
            'description': '고령화와 바이오 기술 발전'
        },
        {
            'name': '금융',
            'performance': 8.3,
            'stocks': ['JPM', 'BAC', 'WFC', 'GS', '055550'],
            'description': '금리 상승과 대출 수요 증가'
        }
    ]
    
    return themes

def update_dashboard_data():
    """전체 대시보드 데이터 업데이트"""
    logger.info("대시보드 데이터 업데이트 시작")
    
    # API 키 가져오기
    alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_KEY')
    finnhub_key = os.environ.get('FINNHUB_KEY')
    
    # 현재 시간 (한국 시간)
    now_utc = datetime.datetime.utcnow()
    now_kst = now_utc + datetime.timedelta(hours=9)
    
    # 데이터 수집
    logger.info("데이터 수집 중...")
    us_stocks = fetch_us_stock_data(alpha_vantage_key) if alpha_vantage_key else {}
    crypto_data = fetch_crypto_data()
    korean_stocks = fetch_korean_market_data()
    indices_data = fetch_global_indices()
    countries_data = generate_country_data()
    themes_data = generate_stock_themes()
    
    # 대시보드 데이터 구성
    dashboard_data = {
        "version": "2.0",
        "last_updated": now_kst.isoformat(),
        "last_updated_display": now_kst.strftime("%Y년 %m월 %d일 %H:%M KST"),
        "year": 2025,
        "data_source": "GitHub 실시간 연동",
        "countries": countries_data,
        "indices": indices_data,
        "us_stocks": us_stocks,
        "korean_stocks": korean_stocks,
        "stock_themes": themes_data,
        "crypto": crypto_data,
        "real_estate": {
            "us_reit_index": {"value": 2850.5, "change": 12.3, "change_percent": "0.43"},
            "korea_reit": {"value": 3420.0, "change": -25.8, "change_percent": "-0.75"}
        },
        "gici": {
            "global_investment_climate": 65,
            "risk_factors": {
                "geopolitical": 50,
                "corporate_earnings": 58,
                "asia_slowdown": 63
            },
            "description": "신중한 낙관론에서 약간 하향 조정된 환경"
        }
    }
    
    # JSON 파일로 저장
    try:
        with open('dashboard_data.json', 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ dashboard_data.json 업데이트 완료")
        
        # 통계 출력
        logger.info(f"📊 수집된 데이터:")
        logger.info(f"   - 미국 주식: {len(us_stocks)}개")
        logger.info(f"   - 한국 주식: {len(korean_stocks)}개")
        logger.info(f"   - 암호화폐: {len(crypto_data)}개")
        logger.info(f"   - 글로벌 지수: {len(indices_data)}개")
        logger.info(f"   - 국가 데이터: {len(countries_data)}개")
        logger.info(f"   - 주식 테마: {len(themes_data)}개")
        
    except Exception as e:
        logger.error(f"❌ 파일 저장 실패: {e}")
        raise e

if __name__ == "__main__":
    update_dashboard_data()