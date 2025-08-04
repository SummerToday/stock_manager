from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/stocks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Interest(db.Model):
    """관심 종목 모델"""
    __tablename__ = 'interests'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    ticker = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=True)  # 종목명 추가
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 복합 인덱스 (사용자별 종목 중복 방지)
    __table_args__ = (
        db.UniqueConstraint('email', 'ticker', name='unique_user_ticker'),
        db.Index('idx_email_ticker', 'email', 'ticker'),
    )
    
    def __repr__(self):
        return f'<Interest {self.email}:{self.ticker}>'
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'email': self.email,
            'ticker': self.ticker,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Alert(db.Model):
    """알림 모델"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    ticker = db.Column(db.String(10), nullable=False)
    stock_name = db.Column(db.String(100), nullable=True)
    alert_type = db.Column(db.String(20), nullable=False)  # price, psychology, rsi, volume
    condition = db.Column(db.String(10), nullable=False)   # above, below, equal
    value = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), nullable=False)      # email, slack, both
    active = db.Column(db.Boolean, default=True)
    triggered_count = db.Column(db.Integer, default=0)
    last_triggered = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스
    __table_args__ = (
        db.Index('idx_email_active', 'email', 'active'),
        db.Index('idx_ticker_active', 'ticker', 'active'),
    )
    
    def __repr__(self):
        return f'<Alert {self.email}:{self.ticker}:{self.alert_type}>'
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'email': self.email,
            'ticker': self.ticker,
            'stockName': self.stock_name,
            'type': self.alert_type,
            'condition': self.condition,
            'value': self.value,
            'method': self.method,
            'active': self.active,
            'triggered_count': self.triggered_count,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class User(db.Model):
    """사용자 모델 (OAuth 정보 저장용)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    picture = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(50), unique=True, nullable=True)
    slack_webhook_url = db.Column(db.String(255), nullable=True)  # 개인 슬랙 웹훅
    notification_email = db.Column(db.String(100), nullable=True)  # 알림 받을 이메일 (다를 수 있음)
    timezone = db.Column(db.String(50), default='Asia/Seoul')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 데이터베이스 초기화 함수
def init_db():
    """데이터베이스 테이블 생성"""
    try:
        db.create_all()
        print("데이터베이스 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"데이터베이스 초기화 중 오류: {e}")

# 샘플 데이터 생성 함수
def create_sample_data():
    """개발용 샘플 데이터 생성"""
    try:
        # 샘플 사용자
        sample_user = User(
            email='test@example.com',
            name='테스트 사용자',
            google_id='sample_google_id',
            timezone='Asia/Seoul'
        )
        
        # 샘플 관심 종목
        sample_interests = [
            Interest(email='test@example.com', ticker='005930', name='삼성전자'),
            Interest(email='test@example.com', ticker='000660', name='SK하이닉스'),
        ]
        
        # 샘플 알림
        sample_alert = Alert(
            email='test@example.com',
            ticker='005930',
            stock_name='삼성전자',
            alert_type='price',
            condition='above',
            value=80000,
            method='email'
        )
        
        # 데이터베이스에 추가
        db.session.add(sample_user)
        db.session.add_all(sample_interests)
        db.session.add(sample_alert)
        db.session.commit()
        
        print("샘플 데이터가 성공적으로 생성되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        print(f"샘플 데이터 생성 중 오류: {e}")

if __name__ == '__main__':
    with app.app_context():
        init_db()
        create_sample_data()