
import pytest
from app.agents.query_router import route_query

def test_intent_detection():
    # Price
    assert route_query("What is the price of Reliance?").intent == "PRICE_QUOTE"
    assert "RELIANCE" in route_query("What is the price of Reliance?").symbols
    
    # IPO
    assert route_query("Show me upcoming IPOs").intent == "IPO"
    
    # Options
    assert route_query("Explain call options").intent == "OPTIONS"
    
    # Intraday
    assert route_query("Give me an intraday plan for TCS").intent == "INTRADAY"
    assert "TCS" in route_query("Give me an intraday plan for TCS").symbols
    
    # Educational
    assert route_query("What is LTP?").intent == "EDUCATIONAL"

def test_nickname_matching():
    res = route_query("How is HDFC doing?")
    assert "HDFCBANK" in res.symbols
    
    res = route_query("Check price of Mukesh Ambani stock")
    assert "RELIANCE" in res.symbols

def test_complex_query():
    res = route_query("Show me the chart and latest news for INFY")
    assert res.is_complex is True
    assert "INFY" in res.symbols
