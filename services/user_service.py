from flask import jsonify
from models import db, Interest

def add_interest(email, ticker):
    interest = Interest(email=email, ticker=ticker)
    db.session.add(interest)
    db.session.commit()
    return jsonify({"msg": "등록 완료"})

def get_interests(email):
    rows = Interest.query.filter_by(email=email).all()
    return jsonify([i.ticker for i in rows])
