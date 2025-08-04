from flask import jsonify
from models import db, Interest

def add_interest(email, ticker, name=None):
    """
    관심 종목 추가
    
    Args:
        email (str): 사용자 이메일
        ticker (str): 종목 코드
        name (str, optional): 종목명
    
    Returns:
        dict: 응답 결과
    """
    try:
        # 이미 존재하는지 확인
        existing = Interest.query.filter_by(email=email, ticker=ticker).first()
        if existing:
            return jsonify({"success": False, "message": "이미 등록된 종목입니다."})
        
        # 새 관심 종목 추가
        interest = Interest(email=email, ticker=ticker, name=name)
        db.session.add(interest)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"{ticker} 종목이 관심 목록에 추가되었습니다.",
            "data": {
                "ticker": ticker,
                "name": name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"관심 종목 추가 중 오류: {e}")
        return jsonify({"success": False, "message": "관심 종목 추가 중 오류가 발생했습니다."})

def get_interests(email):
    """
    사용자의 관심 종목 목록 조회
    
    Args:
        email (str): 사용자 이메일
    
    Returns:
        dict: 관심 종목 목록
    """
    try:
        rows = Interest.query.filter_by(email=email).all()
        
        interests = []
        for interest in rows:
            interests.append({
                "ticker": interest.ticker,
                "name": interest.name or interest.ticker,
                "id": interest.id
            })
        
        return jsonify({
            "success": True,
            "interests": interests,
            "count": len(interests)
        })
        
    except Exception as e:
        print(f"관심 종목 조회 중 오류: {e}")
        return jsonify({"success": False, "message": "관심 종목 조회 중 오류가 발생했습니다."})

def remove_interest_by_ticker(email, ticker):
    """
    관심 종목 삭제 (종목 코드로)
    
    Args:
        email (str): 사용자 이메일
        ticker (str): 종목 코드
    
    Returns:
        dict: 삭제 결과
    """
    try:
        interest = Interest.query.filter_by(email=email, ticker=ticker).first()
        
        if not interest:
            return jsonify({"success": False, "message": "해당 종목을 찾을 수 없습니다."})
        
        db.session.delete(interest)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{ticker} 종목이 관심 목록에서 삭제되었습니다."
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"관심 종목 삭제 중 오류: {e}")
        return jsonify({"success": False, "message": "관심 종목 삭제 중 오류가 발생했습니다."})

def remove_interest_by_id(email, interest_id):
    """
    관심 종목 삭제 (ID로)
    
    Args:
        email (str): 사용자 이메일
        interest_id (int): 관심 종목 ID
    
    Returns:
        dict: 삭제 결과
    """
    try:
        interest = Interest.query.filter_by(email=email, id=interest_id).first()
        
        if not interest:
            return jsonify({"success": False, "message": "해당 종목을 찾을 수 없습니다."})
        
        ticker = interest.ticker
        db.session.delete(interest)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{ticker} 종목이 관심 목록에서 삭제되었습니다."
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"관심 종목 삭제 중 오류: {e}")
        return jsonify({"success": False, "message": "관심 종목 삭제 중 오류가 발생했습니다."})

def update_interest(email, ticker, name=None):
    """
    관심 종목 정보 업데이트
    
    Args:
        email (str): 사용자 이메일
        ticker (str): 종목 코드
        name (str, optional): 새로운 종목명
    
    Returns:
        dict: 업데이트 결과
    """
    try:
        interest = Interest.query.filter_by(email=email, ticker=ticker).first()
        
        if not interest:
            return jsonify({"success": False, "message": "해당 종목을 찾을 수 없습니다."})
        
        if name:
            interest.name = name
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"{ticker} 종목 정보가 업데이트되었습니다.",
            "data": {
                "ticker": interest.ticker,
                "name": interest.name
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"관심 종목 업데이트 중 오류: {e}")
        return jsonify({"success": False, "message": "관심 종목 업데이트 중 오류가 발생했습니다."})

def get_interest_count(email):
    """
    사용자의 관심 종목 개수 조회
    
    Args:
        email (str): 사용자 이메일
    
    Returns:
        int: 관심 종목 개수
    """
    try:
        count = Interest.query.filter_by(email=email).count()
        return count
        
    except Exception as e:
        print(f"관심 종목 개수 조회 중 오류: {e}")
        return 0

def is_interest_exists(email, ticker):
    """
    특정 종목이 관심 목록에 있는지 확인
    
    Args:
        email (str): 사용자 이메일
        ticker (str): 종목 코드
    
    Returns:
        bool: 존재 여부
    """
    try:
        interest = Interest.query.filter_by(email=email, ticker=ticker).first()
        return interest is not None
        
    except Exception as e:
        print(f"관심 종목 존재 확인 중 오류: {e}")
        return False