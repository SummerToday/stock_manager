import smtplib
import requests
from email.message import EmailMessage
from datetime import datetime
from flask import jsonify

# 임시 메모리 저장소 (실제로는 데이터베이스 사용)
alerts_storage = {}
alert_id_counter = 1

def send_email_alert(to, subject, body):
    """
    이메일 알림 발송
    
    Args:
        to (str): 수신자 이메일
        subject (str): 제목
        body (str): 본문
    
    Returns:
        bool: 발송 성공 여부
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "noreply@stockalert.com"
        msg["To"] = to
        msg.set_content(body)
        
        # 실제 운영환경에서는 SMTP 서버 설정 필요
        # with smtplib.SMTP("localhost") as smtp:
        #     smtp.send_message(msg)
        
        print(f"이메일 발송 시뮬레이션: {to} - {subject}")
        return True
        
    except Exception as e:
        print(f"이메일 발송 중 오류: {e}")
        return False

def send_slack_alert(webhook_url, message):
    """
    슬랙 알림 발송
    
    Args:
        webhook_url (str): 슬랙 웹훅 URL
        message (str): 메시지
    
    Returns:
        bool: 발송 성공 여부
    """
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"슬랙 메시지 발송 성공: {message}")
            return True
        else:
            print(f"슬랙 메시지 발송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"슬랙 메시지 발송 중 오류: {e}")
        return False

def get_user_alerts(email):
    """
    사용자의 알림 목록 조회
    
    Args:
        email (str): 사용자 이메일
    
    Returns:
        list: 알림 목록
    """
    try:
        user_alerts = alerts_storage.get(email, [])
        return user_alerts
        
    except Exception as e:
        print(f"알림 목록 조회 중 오류: {e}")
        return []

def create_user_alert(email, ticker, alert_type, condition, value, method):
    """
    새로운 알림 생성
    
    Args:
        email (str): 사용자 이메일
        ticker (str): 종목 코드
        alert_type (str): 알림 유형 (price, psychology, rsi, volume)
        condition (str): 조건 (above, below, equal)
        value (float): 기준값
        method (str): 알림 방법 (email, slack, both)
    
    Returns:
        dict: 생성 결과
    """
    try:
        global alert_id_counter
        
        # 사용자 알림 목록 가져오기
        if email not in alerts_storage:
            alerts_storage[email] = []
        
        # 새 알림 생성
        new_alert = {
            "id": alert_id_counter,
            "ticker": ticker,
            "stockName": ticker,  # 실제로는 종목명 조회
            "type": alert_type,
            "condition": condition,
            "value": float(value),
            "method": method,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "triggered_count": 0,
            "last_triggered": None
        }
        
        alerts_storage[email].append(new_alert)
        alert_id_counter += 1
        
        return {
            "success": True,
            "message": "알림이 성공적으로 생성되었습니다.",
            "alert_id": new_alert["id"]
        }
        
    except Exception as e:
        print(f"알림 생성 중 오류: {e}")
        return {
            "success": False,
            "message": "알림 생성 중 오류가 발생했습니다."
        }

def delete_user_alert(email, alert_id):
    """
    알림 삭제
    
    Args:
        email (str): 사용자 이메일
        alert_id (str): 알림 ID
    
    Returns:
        dict: 삭제 결과
    """
    try:
        alert_id = int(alert_id)
        
        if email not in alerts_storage:
            return {
                "success": False,
                "message": "알림을 찾을 수 없습니다."
            }
        
        user_alerts = alerts_storage[email]
        original_length = len(user_alerts)
        
        # 해당 ID의 알림 제거
        alerts_storage[email] = [alert for alert in user_alerts if alert["id"] != alert_id]
        
        if len(alerts_storage[email]) < original_length:
            return {
                "success": True,
                "message": "알림이 삭제되었습니다."
            }
        else:
            return {
                "success": False,
                "message": "해당 알림을 찾을 수 없습니다."
            }
            
    except Exception as e:
        print(f"알림 삭제 중 오류: {e}")
        return {
            "success": False,
            "message": "알림 삭제 중 오류가 발생했습니다."
        }

def update_alert_status(email, alert_id, active):
    """
    알림 활성화/비활성화 상태 변경
    
    Args:
        email (str): 사용자 이메일
        alert_id (int): 알림 ID
        active (bool): 활성화 상태
    
    Returns:
        dict: 업데이트 결과
    """
    try:
        if email not in alerts_storage:
            return {
                "success": False,
                "message": "알림을 찾을 수 없습니다."
            }
        
        for alert in alerts_storage[email]:
            if alert["id"] == alert_id:
                alert["active"] = active
                return {
                    "success": True,
                    "message": f"알림이 {'활성화' if active else '비활성화'}되었습니다."
                }
        
        return {
            "success": False,
            "message": "해당 알림을 찾을 수 없습니다."
        }
        
    except Exception as e:
        print(f"알림 상태 업데이트 중 오류: {e}")
        return {
            "success": False,
            "message": "알림 상태 업데이트 중 오류가 발생했습니다."
        }

def check_and_trigger_alerts():
    """
    모든 활성 알림을 확인하고 조건에 맞으면 발송
    실제 운영환경에서는 백그라운드 작업으로 실행
    
    Returns:
        dict: 처리 결과
    """
    try:
        triggered_count = 0
        
        for email, user_alerts in alerts_storage.items():
            for alert in user_alerts:
                if not alert["active"]:
                    continue
                
                # 실제로는 여기서 현재 주가를 조회하여 조건 확인
                # 현재는 시뮬레이션으로 랜덤하게 트리거
                import random
                if random.random() < 0.1:  # 10% 확률로 트리거
                    trigger_alert(email, alert)
                    triggered_count += 1
        
        return {
            "success": True,
            "message": f"{triggered_count}개의 알림이 발송되었습니다.",
            "triggered_count": triggered_count
        }
        
    except Exception as e:
        print(f"알림 확인 및 트리거 중 오류: {e}")
        return {
            "success": False,
            "message": "알림 확인 중 오류가 발생했습니다."
        }

def trigger_alert(email, alert):
    """
    특정 알림 발송
    
    Args:
        email (str): 사용자 이메일
        alert (dict): 알림 정보
    """
    try:
        # 알림 메시지 생성
        condition_text = {
            "above": "이상",
            "below": "이하", 
            "equal": "달성"
        }.get(alert["condition"], alert["condition"])
        
        type_text = {
            "price": "주가",
            "psychology": "심리도",
            "rsi": "RSI",
            "volume": "거래량"
        }.get(alert["type"], alert["type"])
        
        subject = f"[주식 알림] {alert['stockName']} {type_text} 알림"
        message = f"{alert['stockName']}({alert['ticker']})의 {type_text}가 {alert['value']} {condition_text}을 달성했습니다."
        
        # 알림 방법에 따라 발송
        if alert["method"] in ["email", "both"]:
            send_email_alert(email, subject, message)
        
        if alert["method"] in ["slack", "both"]:
            # 실제로는 사용자별 슬랙 웹훅 URL 저장 필요
            webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            send_slack_alert(webhook_url, message)
        
        # 알림 트리거 기록 업데이트
        alert["triggered_count"] += 1
        alert["last_triggered"] = datetime.now().isoformat()
        
        print(f"알림 발송 완료: {email} - {message}")
        
    except Exception as e:
        print(f"알림 발송 중 오류: {e}")

def get_alert_statistics(email):
    """
    사용자의 알림 통계 조회
    
    Args:
        email (str): 사용자 이메일
    
    Returns:
        dict: 알림 통계
    """
    try:
        user_alerts = alerts_storage.get(email, [])
        
        total_alerts = len(user_alerts)
        active_alerts = len([alert for alert in user_alerts if alert["active"]])
        total_triggered = sum(alert["triggered_count"] for alert in user_alerts)
        
        # 오늘 발송된 알림 수 (시뮬레이션)
        today_triggered = total_triggered  # 실제로는 오늘 날짜 필터링 필요
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "total_triggered": total_triggered,
            "today_triggered": today_triggered
        }
        
    except Exception as e:
        print(f"알림 통계 조회 중 오류: {e}")
        return {
            "total_alerts": 0,
            "active_alerts": 0,
            "total_triggered": 0,
            "today_triggered": 0
        }