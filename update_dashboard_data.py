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
    """미국 주식 데이터 수집 - Alpha Vantage"""
    try:
        if not api_key:
            logger.warning("⚠️ ALPHA_VANTAGE_KEY 없음 - 폴백 데이터 사용")
            return get_fallback_us_stocks()
            
        # S&P 500 주요 종목들
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ']
        stocks = {}
        
        for symbol in symbols:
            try:
                # Alpha Vantage Global Quote API
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    stocks[symbol] = {
                        'symbol': symbol,
                        'name': get_company_name(symbol),
                        'price': float(quote.get('05. price', 0)),
                        'change': float(quote.get('09. change', 0)),
                        'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                        'volume': int(quote.get('06. volume', 0)),
                        'market_cap': get_market_cap(symbol)
                    }
                    logger.info(f"✅ {symbol}: ${stocks[symbol]['price']:.2f}")
                else:
                    logger.warning(f"⚠️ {symbol}: API 응답 이상, 폴백 사용")
                
                time.sleep(12)  # API 제한 고려
                
            except Exception as e:
                logger.error(f"❌ Error fetching {symbol}: {e}")
                continue
                
        # 데이터가 부족하면 폴백으로 보완
        if len(stocks) < 5:
            fallback_stocks = get_fallback_us_stocks()
            stocks.update(fallback_stocks)
            
        return stocks
        
    except Exception as e:
        logger.error(f"❌ Error in fetch_us_stock_data: {e}")
        return get_fallback_us_stocks()

def get_fallback_us_stocks():
    """미국 주식 폴백 데이터 (시장 시간 기준 합리적 가격)"""
    return {
        'AAPL': {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.43, 'change': 2.15, 'change_percent': '1.24', 'volume': 45678900, 'market_cap': 3.5},
        'MSFT': {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 378.85, 'change': -1.32, 'change_percent': '-0.35', 'volume': 23456789, 'market_cap': 3.1},
        'GOOGL': {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 138.21, 'change': 0.87, 'change_percent': '0.63', 'volume': 34567890, 'market_cap': 2.1},
        'AMZN': {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'price': 134.56, 'change': -2.34, 'change_percent': '-1.71', 'volume': 56789012, 'market_cap': 1.8},
        'NVDA': {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'price': 724.31, 'change': 15.67, 'change_percent': '2.21', 'volume': 78901234, 'market_cap': 1.7},
        'TSLA': {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 248.42, 'change': -4.23, 'change_percent': '-1.67', 'volume': 89012345, 'market_cap': 0.8},
        'META': {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'price': 295.89, 'change': 3.45, 'change_percent': '1.18', 'volume': 12345678, 'market_cap': 1.3},
        'BRK-B': {'symbol': 'BRK-B', 'name': 'Berkshire Hathaway', 'price': 412.67, 'change': 1.23, 'change_percent': '0.30', 'volume': 9876543, 'market_cap': 0.9},
        'UNH': {'symbol': 'UNH', 'name': 'UnitedHealth Group', 'price': 487.92, 'change': -2.56, 'change_percent': '-0.52', 'volume': 8765432, 'market_cap': 0.5},
        'JNJ': {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'price': 163.45, 'change': 0.78, 'change_percent': '0.48', 'volume': 7654321, 'market_cap': 0.4}
    }

def fetch_crypto_data():
    """암호화폐 데이터 수집 - CoinGecko"""
    try:
        # CoinGecko API (무료)
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,solana,ripple&vs_currencies=usd&include_24hr_change=true&include_market_cap=true'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        crypto = {}
        crypto_names = {
            'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin'},
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum'},
            'binancecoin': {'symbol': 'BNB', 'name': 'BNB'},
            'cardano': {'symbol': 'ADA', 'name': 'Cardano'},
            'solana': {'symbol': 'SOL', 'name': 'Solana'},
            'ripple': {'symbol': 'XRP', 'name': 'XRP'}
        }
        
        for coin_id, coin_info in crypto_names.items():
            if coin_id in data:
                coin_data = data[coin_id]
                crypto[coin_info['symbol']] = {
                    'symbol': coin_info['symbol'],
                    'name': coin_info['name'],
                    'price': coin_data.get('usd', 0),
                    'change_24h': round(coin_data.get('usd_24h_change', 0), 2),
                    'market_cap': coin_data.get('usd_market_cap', 0)
                }
                logger.info(f"✅ {coin_info['symbol']}: ${crypto[coin_info['symbol']]['price']:,.2f}")
        
        # 폴백 데이터로 보완
        if len(crypto) < 3:
            fallback_crypto = get_fallback_crypto()
            crypto.update(fallback_crypto)
            
        return crypto
        
    except Exception as e:
        logger.error(f"❌ Error in fetch_crypto_data: {e}")
        return get_fallback_crypto()

def get_fallback_crypto():
    """암호화폐 폴백 데이터"""
    return {
        'BTC': {'symbol': 'BTC', 'name': 'Bitcoin', 'price': 67234.56, 'change_24h': 2.34, 'market_cap': 1325000000000},
        'ETH': {'symbol': 'ETH', 'name': 'Ethereum', 'price': 2543.21, 'change_24h': -1.23, 'market_cap': 305000000000},
        'BNB': {'symbol': 'BNB', 'name': 'BNB', 'price': 542.87, 'change_24h': 0.78, 'market_cap': 81000000000},
        'ADA': {'symbol': 'ADA', 'name': 'Cardano', 'price': 0.387, 'change_24h': -2.15, 'market_cap': 13500000000},
        'SOL': {'symbol': 'SOL', 'name': 'Solana', 'price': 145.32, 'change_24h': 4.56, 'market_cap': 67000000000},
        'XRP': {'symbol': 'XRP', 'name': 'XRP', 'price': 0.524, 'change_24h': 1.89, 'market_cap': 29800000000}
    }

def fetch_korean_market_data(finnhub_key=None):
    """한국 시장 데이터 - 폴백 데이터 사용 (Finnhub 무료 계정 제한으로)"""
    logger.info("ℹ️ 한국 주식: Finnhub 무료 제한으로 폴백 데이터 사용")
    return get_fallback_korean_stocks()

def get_fallback_korean_stocks():
    """한국 주식 폴백 데이터 (실제 시세 반영한 합리적 가격)"""
    return {
        '005930': {'symbol': '005930', 'name': '삼성전자', 'sector': '반도체', 'price': 58100, 'change': -400, 'change_percent': '-0.68', 'high': 58800, 'low': 57900, 'volume': 12450000},
        '000660': {'symbol': '000660', 'name': 'SK하이닉스', 'sector': '반도체', 'price': 89500, 'change': 1200, 'change_percent': '1.36', 'high': 90200, 'low': 88700, 'volume': 2340000},
        '035420': {'symbol': '035420', 'name': 'NAVER', 'sector': '인터넷', 'price': 145200, 'change': -800, 'change_percent': '-0.55', 'high': 147000, 'low': 144500, 'volume': 567000},
        '051910': {'symbol': '051910', 'name': 'LG화학', 'sector': '화학', 'price': 284000, 'change': 3500, 'change_percent': '1.25', 'high': 285000, 'low': 281000, 'volume': 890000},
        '006400': {'symbol': '006400', 'name': '삼성SDI', 'sector': '배터리', 'price': 318000, 'change': -5000, 'change_percent': '-1.55', 'high': 324000, 'low': 317000, 'volume': 432000},
        '207940': {'symbol': '207940', 'name': '삼성바이오로직스', 'sector': '바이오', 'price': 672000, 'change': 8000, 'change_percent': '1.20', 'high': 678000, 'low': 668000, 'volume': 123000},
        '035720': {'symbol': '035720', 'name': '카카오', 'sector': '인터넷', 'price': 47800, 'change': -600, 'change_percent': '-1.24', 'high': 48900, 'low': 47500, 'volume': 1890000}
    }

def fetch_global_indices(alpha_vantage_key=None, finnhub_key=None):
    """글로벌 지수 데이터 - 폴백 데이터 사용 (Finnhub 제한으로)"""
    logger.info("ℹ️ 글로벌 지수: Finnhub 무료 제한으로 폴백 데이터 사용")
    return get_fallback_indices()

def get_fallback_indices():
    """글로벌 지수 폴백 데이터"""
    return {
        'SPX': {'symbol': 'SPX', 'name': 'S&P 500', 'value': 5847.21, 'change': 23.45, 'change_percent': '0.40', 'high': 5856.78, 'low': 5831.23},
        'IXIC': {'symbol': 'IXIC', 'name': 'NASDAQ', 'value': 18567.89, 'change': 97.34, 'change_percent': '0.53', 'high': 18598.45, 'low': 18523.12},
        'DJI': {'symbol': 'DJI', 'name': 'Dow Jones', 'value': 43047.32, 'change': -87.65, 'change_percent': '-0.20', 'high': 43156.78, 'low': 43021.45},
        'KS11': {'symbol': 'KS11', 'name': 'KOSPI', 'value': 2434.67, 'change': -12.34, 'change_percent': '-0.50', 'high': 2451.23, 'low': 2428.90},
        'KQ11': {'symbol': 'KQ11', 'name': 'KOSDAQ', 'value': 687.45, 'change': -5.67, 'change_percent': '-0.82', 'high': 695.12, 'low': 684.23},
        'N225': {'symbol': 'N225', 'name': 'Nikkei 225', 'value': 38456.78, 'change': 156.34, 'change_percent': '0.41', 'high': 38523.45, 'low': 38367.89}
    }

def get_company_name(symbol):
    """회사명 매핑"""
    names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corp.',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'NVDA': 'NVIDIA Corp.',
        'TSLA': 'Tesla Inc.',
        'META': 'Meta Platforms Inc.',
        'BRK-B': 'Berkshire Hathaway',
        'UNH': 'UnitedHealth Group',
        'JNJ': 'Johnson & Johnson'
    }
    return names.get(symbol, symbol)

def get_market_cap(symbol):
    """시가총액 추정 (단위: 조 달러)"""
    market_caps = {
        'AAPL': 3.5, 'MSFT': 3.1, 'GOOGL': 2.1, 'AMZN': 1.8, 'NVDA': 1.7,
        'TSLA': 0.8, 'META': 1.3, 'BRK-B': 0.9, 'UNH': 0.5, 'JNJ': 0.4
    }
    return market_caps.get(symbol, 0.1)

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
            'description': 'AI 기술 혁신과 소비 회복세',
            'outlook': 'positive'
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
            'description': '부동산 조정과 수출 회복',
            'outlook': 'neutral'
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
            'description': '반도체 회복과 내수 부진',
            'outlook': 'cautious'
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
            'description': '엔화 약세와 수출 증가',
            'outlook': 'neutral'
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
            'description': '제조업 둔화와 에너지 전환',
            'outlook': 'cautious'
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
            'description': 'AI 혁명과 반도체 슈퍼사이클',
            'trend': 'hot'
        },
        {
            'name': '클린에너지',
            'performance': 15.2,
            'stocks': ['TSLA', 'ENPH', 'FSLR', 'NIO', '003670'],
            'description': '탄소중립과 재생에너지 확산',
            'trend': 'rising'
        },
        {
            'name': '헬스케어',
            'performance': 12.8,
            'stocks': ['JNJ', 'PFE', 'ABBV', 'UNH', '207940'],
            'description': '고령화와 바이오 기술 발전',
            'trend': 'stable'
        },
        {
            'name': '금융',
            'performance': 8.3,
            'stocks': ['JPM', 'BAC', 'WFC', 'GS', '055550'],
            'description': '금리 상승과 대출 수요 증가',
            'trend': 'stable'
        },
        {
            'name': '전기차',
            'performance': 22.1,
            'stocks': ['TSLA', 'BYD', 'NIO', 'XPEV', '066570'],
            'description': '전기차 시장 확산과 배터리 기술',
            'trend': 'hot'
        }
    ]
    
    return themes

def update_dashboard_data():
    """전체 대시보드 데이터 업데이트"""
    logger.info("🔄 대시보드 데이터 업데이트 시작")
    
    # API 키 가져오기
    alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_KEY')
    finnhub_key = os.environ.get('FINNHUB_KEY')
    
    # 현재 시간 (한국 시간)
    now_utc = datetime.datetime.utcnow()
    now_kst = now_utc + datetime.timedelta(hours=9)
    
    # 데이터 수집
    logger.info("📊 데이터 수집 중...")
    us_stocks = fetch_us_stock_data(alpha_vantage_key)
    crypto_data = fetch_crypto_data()
    korean_stocks = fetch_korean_market_data(finnhub_key)
    indices_data = fetch_global_indices(alpha_vantage_key, finnhub_key)
    countries_data = generate_country_data()
    themes_data = generate_stock_themes()
    
    # 마켓 상태 계산
    market_status = calculate_market_status(indices_data, korean_stocks, us_stocks)
    
    # 대시보드 데이터 구성
    dashboard_data = {
        "version": "2.2",
        "last_updated": now_kst.isoformat(),
        "last_updated_display": now_kst.strftime("%Y년 %m월 %d일 %H:%M KST"),
        "year": 2025,
        "data_source": "GitHub 실시간 연동 (폴백 데이터 포함)",
        "market_status": market_status,
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
            "global_investment_climate": calculate_gici_score(indices_data, market_status),
            "risk_factors": {
                "geopolitical": 50,
                "corporate_earnings": 58,
                "asia_slowdown": 63,
                "inflation": 45,
                "interest_rates": 52
            },
            "description": "신중한 낙관론에서 약간 하향 조정된 환경"
        },
        "stats": {
            "total_assets_tracked": len(us_stocks) + len(korean_stocks) + len(crypto_data) + len(indices_data),
            "api_calls_made": count_api_calls(),
            "data_freshness": "혼합 (실시간 + 폴백)"
        }
    }
    
    # JSON 파일로 저장
    try:
        with open('dashboard_data.json', 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ dashboard_data.json 업데이트 완료")
        
        # 통계 출력
        logger.info(f"📈 수집 완료:")
        logger.info(f"   - 미국 주식: {len(us_stocks)}개")
        logger.info(f"   - 한국 주식: {len(korean_stocks)}개 (폴백)")
        logger.info(f"   - 암호화폐: {len(crypto_data)}개")
        logger.info(f"   - 글로벌 지수: {len(indices_data)}개 (폴백)")
        logger.info(f"   - 국가 데이터: {len(countries_data)}개")
        logger.info(f"   - 주식 테마: {len(themes_data)}개")
        logger.info(f"   - GICI 점수: {dashboard_data['gici']['global_investment_climate']}")
        
    except Exception as e:
        logger.error(f"❌ 파일 저장 실패: {e}")
        raise e

def calculate_market_status(indices, korean_stocks, us_stocks):
    """시장 상태 종합 계산"""
    try:
        # 지수 변화율 평균
        index_changes = []
        for idx in indices.values():
            if 'change_percent' in idx:
                try:
                    change_pct = float(idx['change_percent'])
                    index_changes.append(change_pct)
                except:
                    pass
        
        avg_index_change = sum(index_changes) / len(index_changes) if index_changes else 0
        
        # 상태 결정
        if avg_index_change > 1.0:
            status = "상승세"
            sentiment = "bullish"
        elif avg_index_change < -1.0:
            status = "하락세"  
            sentiment = "bearish"
        else:
            status = "보합세"
            sentiment = "neutral"
            
        return {
            "overall": status,
            "sentiment": sentiment,
            "avg_change": round(avg_index_change, 2),
            "volume_trend": "높음" if abs(avg_index_change) > 0.5 else "보통"
        }
    except:
        return {"overall": "보합세", "sentiment": "neutral", "avg_change": 0, "volume_trend": "보통"}

def calculate_gici_score(indices, market_status):
    """GICI(Global Investment Climate Index) 점수 계산"""
    try:
        base_score = 65
        
        # 지수 성과 반영
        if market_status["sentiment"] == "bullish":
            score_adj = +5
        elif market_status["sentiment"] == "bearish":
            score_adj = -8
        else:
            score_adj = 0
            
        # 변동성 고려
        if abs(market_status["avg_change"]) > 2.0:
            score_adj -= 3  # 높은 변동성은 불안 요소
            
        final_score = max(0, min(100, base_score + score_adj))
        return final_score
    except:
        return 65

def count_api_calls():
    """API 호출 횟수 추정"""
    return {"alpha_vantage": 10, "finnhub": 0, "coingecko": 1, "fallback_used": True}

if __name__ == "__main__":
    update_dashboard_data()