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
                    logger.warning(f"⚠️ {symbol}: API 응답 이상 - {data}")
                
                time.sleep(12)  # API 제한 고려 (5 calls/min)
                
            except Exception as e:
                logger.error(f"❌ Error fetching {symbol}: {e}")
                continue
                
        return stocks
        
    except Exception as e:
        logger.error(f"❌ Error in fetch_us_stock_data: {e}")
        return {}

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
                
        return crypto
        
    except Exception as e:
        logger.error(f"❌ Error in fetch_crypto_data: {e}")
        return {}

def fetch_korean_market_data(finnhub_key):
    """한국 시장 데이터 수집 - Finnhub API 사용"""
    try:
        # 한국 대표 주식들 (KRX 상장)
        korean_symbols = {
            '005930.KS': {'name': '삼성전자', 'sector': '반도체'},
            '000660.KS': {'name': 'SK하이닉스', 'sector': '반도체'},
            '035420.KS': {'name': 'NAVER', 'sector': '인터넷'},
            '051910.KS': {'name': 'LG화학', 'sector': '화학'},
            '006400.KS': {'name': '삼성SDI', 'sector': '배터리'},
            '207940.KS': {'name': '삼성바이오로직스', 'sector': '바이오'},
            '035720.KS': {'name': '카카오', 'sector': '인터넷'},
            '068270.KS': {'name': '셀트리온', 'sector': '바이오'}
        }
        
        korean_stocks = {}
        
        for symbol, info in korean_symbols.items():
            try:
                # Finnhub Quote API
                url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_key}'
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if 'c' in data and data['c'] > 0:  # current price exists
                    current_price = data['c']
                    previous_close = data['pc']
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
                    
                    korean_stocks[symbol.replace('.KS', '')] = {
                        'symbol': symbol.replace('.KS', ''),
                        'name': info['name'],
                        'sector': info['sector'],
                        'price': int(current_price),
                        'change': int(change),
                        'change_percent': f"{change_percent:.2f}",
                        'high': data.get('h', current_price),
                        'low': data.get('l', current_price),
                        'volume': data.get('v', 0)
                    }
                    logger.info(f"✅ {info['name']}: {int(current_price):,}원")
                else:
                    logger.warning(f"⚠️ {info['name']}: 데이터 없음")
                
                time.sleep(0.5)  # API 제한 고려
                
            except Exception as e:
                logger.error(f"❌ Error fetching {info['name']}: {e}")
                continue
                
        return korean_stocks
        
    except Exception as e:
        logger.error(f"❌ Error in fetch_korean_market_data: {e}")
        # 폴백 데이터
        return {
            '005930': {'name': '삼성전자', 'price': 58000, 'change': -1000, 'change_percent': '-1.69'},
            '000660': {'name': 'SK하이닉스', 'price': 89000, 'change': 2000, 'change_percent': '2.30'},
            '035420': {'name': 'NAVER', 'price': 145000, 'change': -3000, 'change_percent': '-2.03'}
        }

def fetch_global_indices(alpha_vantage_key, finnhub_key):
    """글로벌 지수 데이터 수집 - Finnhub 우선, Alpha Vantage 폴백"""
    try:
        indices = {}
        
        # Finnhub 지수 심볼
        finnhub_symbols = {
            '^GSPC': {'name': 'S&P 500', 'code': 'SPX'},
            '^IXIC': {'name': 'NASDAQ', 'code': 'IXIC'},
            '^DJI': {'name': 'Dow Jones', 'code': 'DJI'},
            '^KS11': {'name': 'KOSPI', 'code': 'KS11'},
            '^KQ11': {'name': 'KOSDAQ', 'code': 'KQ11'},
            '^N225': {'name': 'Nikkei 225', 'code': 'N225'},
            '^FTSE': {'name': 'FTSE 100', 'code': 'FTSE'}
        }
        
        for symbol, info in finnhub_symbols.items():
            try:
                # Finnhub Index Quote
                url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={finnhub_key}'
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if 'c' in data and data['c'] > 0:
                    current_value = data['c']
                    previous_close = data['pc']
                    change = current_value - previous_close
                    change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
                    
                    indices[info['code']] = {
                        'symbol': info['code'],
                        'name': info['name'],
                        'value': round(current_value, 2),
                        'change': round(change, 2),
                        'change_percent': f"{change_percent:.2f}",
                        'high': data.get('h', current_value),
                        'low': data.get('l', current_value)
                    }
                    logger.info(f"✅ {info['name']}: {current_value:,.2f}")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"⚠️ Finnhub {info['name']} 실패: {e}")
                # Alpha Vantage 폴백 (주요 지수만)
                if info['code'] in ['SPX', 'IXIC', 'DJI'] and alpha_vantage_key:
                    try:
                        av_symbol = 'SPY' if info['code'] == 'SPX' else symbol.replace('^', '')
                        av_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={av_symbol}&apikey={alpha_vantage_key}'
                        av_response = requests.get(av_url, timeout=10)
                        av_data = av_response.json()
                        
                        if 'Global Quote' in av_data:
                            quote = av_data['Global Quote']
                            indices[info['code']] = {
                                'symbol': info['code'],
                                'name': info['name'],
                                'value': float(quote.get('05. price', 0)),
                                'change': float(quote.get('09. change', 0)),
                                'change_percent': quote.get('10. change percent', '0%').replace('%', '')
                            }
                            logger.info(f"✅ {info['name']} (폴백): {indices[info['code']]['value']:.2f}")
                        
                        time.sleep(12)  # Alpha Vantage rate limit
                    except:
                        pass
        
        return indices
        
    except Exception as e:
        logger.error(f"❌ Error in fetch_global_indices: {e}")
        # 폴백 데이터
        return {
            'SPX': {'name': 'S&P 500', 'value': 5800.0, 'change': 15.5, 'change_percent': '0.27'},
            'IXIC': {'name': 'NASDAQ', 'value': 18500.0, 'change': 85.2, 'change_percent': '0.46'},
            'KS11': {'name': 'KOSPI', 'value': 2420.0, 'change': -15.8, 'change_percent': '-0.65'}
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
    us_stocks = fetch_us_stock_data(alpha_vantage_key) if alpha_vantage_key else {}
    crypto_data = fetch_crypto_data()
    korean_stocks = fetch_korean_market_data(finnhub_key) if finnhub_key else {}
    indices_data = fetch_global_indices(alpha_vantage_key, finnhub_key)
    countries_data = generate_country_data()
    themes_data = generate_stock_themes()
    
    # 마켓 상태 계산
    market_status = calculate_market_status(indices_data, korean_stocks, us_stocks)
    
    # 대시보드 데이터 구성
    dashboard_data = {
        "version": "2.1",
        "last_updated": now_kst.isoformat(),
        "last_updated_display": now_kst.strftime("%Y년 %m월 %d일 %H:%M KST"),
        "year": 2025,
        "data_source": "GitHub 실시간 연동 (Finnhub + Alpha Vantage + CoinGecko)",
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
            "data_freshness": "실시간"
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
        logger.info(f"   - 한국 주식: {len(korean_stocks)}개")
        logger.info(f"   - 암호화폐: {len(crypto_data)}개")
        logger.info(f"   - 글로벌 지수: {len(indices_data)}개")
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
    # 실제로는 글로벌 카운터나 메트릭을 사용
    return {"alpha_vantage": 10, "finnhub": 15, "coingecko": 1}

if __name__ == "__main__":
    update_dashboard_data()