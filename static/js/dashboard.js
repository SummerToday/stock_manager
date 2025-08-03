// 전역 변수
let interests = [];
let alerts = [];

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    loadInterests();
    loadAlerts();
    
    // 사용자 정보 설정
    const userEmail = document.getElementById('userEmail').textContent;
    if (userEmail && userEmail !== 'user@example.com') {
        const userName = userEmail.split('@')[0];
        document.getElementById('userName').textContent = userName + '님';
        document.getElementById('userAvatar').textContent = userName.charAt(0).toUpperCase();
    }
});

// 페이지 초기화
function initializePage() {
    // 페이지 로드 애니메이션
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.8s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // 환영 메시지
    setTimeout(() => {
        showNotification('환영합니다! 대시보드가 준비되었습니다.', 'success');
    }, 1000);
}

// 관심 종목 로드
async function loadInterests() {
    try {
        const response = await fetch('/api/interests');
        const data = await response.json();
        
        if (data.success) {
            interests = data.interests || [];
            updateInterestStats();
            renderStocks();
        } else {
            console.error('관심 종목 로드 실패:', data.message);
        }
    } catch (error) {
        console.error('관심 종목 로드 중 오류:', error);
    } finally {
        document.getElementById('stockLoading').style.display = 'none';
    }
}

// 알림 목록 로드
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        
        if (data.success) {
            alerts = data.alerts || [];
            updateAlertStats();
            renderAlerts();
        } else {
            console.error('알림 목록 로드 실패:', data.message);
        }
    } catch (error) {
        console.error('알림 목록 로드 중 오류:', error);
    } finally {
        document.getElementById('alertLoading').style.display = 'none';
    }
}

// 통계 업데이트
function updateInterestStats() {
    document.getElementById('interestCount').textContent = interests.length;
}

function updateAlertStats() {
    const activeAlerts = alerts.filter(alert => alert.active).length;
    document.getElementById('alertCount').textContent = activeAlerts;
}

// 주식 목록 렌더링
function renderStocks() {
    const stockList = document.getElementById('stockList');
    const emptyState = document.getElementById('stockEmptyState');
    
    if (interests.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    const stocksHtml = interests.map(stock => `
        <div class="stock-item" data-ticker="${stock.ticker}">
            <div class="stock-info">
                <div class="stock-name">${stock.name || stock.ticker}</div>
                <div class="stock-code">${stock.ticker}</div>
            </div>
            <div class="stock-price">
                <div class="price">${formatPrice(stock.price || 0)}원</div>
                <div class="change ${stock.change >= 0 ? 'positive' : 'negative'}">
                    ${stock.change >= 0 ? '+' : ''}${formatChange(stock.change || 0)} (${formatPercent(stock.changePercent || 0)}%)
                </div>
            </div>
            <div class="stock-actions">
                <button class="btn btn-primary btn-small" onclick="openAlertModal('${stock.ticker}')">알림 설정</button>
                <button class="btn btn-danger btn-small" onclick="removeStock('${stock.ticker}')">삭제</button>
            </div>
        </div>
    `).join('');
    
    stockList.innerHTML = stocksHtml;
}

// 알림 목록 렌더링
function renderAlerts() {
    const alertList = document.getElementById('alertList');
    const emptyState = document.getElementById('alertEmptyState');
    
    if (alerts.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    
    emptyState.style.display = 'none';
    
    const alertsHtml = alerts.map(alert => `
        <div class="alert-item">
            <div class="alert-info">
                <h4>${alert.stockName || alert.ticker} ${getAlertTypeText(alert.type)} 알림</h4>
                <p>${getAlertConditionText(alert)} | ${getNotificationMethodText(alert.method)}</p>
            </div>
            <div class="alert-status ${alert.active ? '' : 'inactive'}">
                ${alert.active ? '활성' : '비활성'}
            </div>
        </div>
    `).join('');
    
    alertList.innerHTML = alertsHtml;
}

// 종목 추가 모달 열기
function openAddStockModal() {
    document.getElementById('addStockModal').style.display = 'block';
    document.getElementById('stockTicker').focus();
}

// 종목 추가 모달 닫기
function closeAddStockModal() {
    document.getElementById('addStockModal').style.display = 'none';
    document.getElementById('addStockForm').reset();
}

// 알림 설정 모달 열기
function openAlertModal(ticker) {
    document.getElementById('alertStockTicker').value = ticker;
    document.getElementById('alertModal').style.display = 'block';
}

// 알림 설정 모달 닫기
function closeAlertModal() {
    document.getElementById('alertModal').style.display = 'none';
    document.getElementById('alertForm').reset();
}

// 종목 추가
async function addStock(event) {
    event.preventDefault();
    
    const ticker = document.getElementById('stockTicker').value.trim().toUpperCase();
    const name = document.getElementById('stockName').value.trim();
    
    if (!ticker) {
        showNotification('종목 코드를 입력해주세요.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/interests', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ticker, name })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${ticker} 종목이 추가되었습니다.`, 'success');
            closeAddStockModal();
            loadInterests(); // 목록 새로고침
        } else {
            showNotification(data.message || '종목 추가에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('종목 추가 중 오류:', error);
        showNotification('종목 추가 중 오류가 발생했습니다.', 'error');
    }
}

// 종목 삭제
async function removeStock(ticker) {
    if (!confirm(`${ticker} 종목을 삭제하시겠습니까?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/interests/${ticker}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${ticker} 종목이 삭제되었습니다.`, 'success');
            loadInterests(); // 목록 새로고침
        } else {
            showNotification(data.message || '종목 삭제에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('종목 삭제 중 오류:', error);
        showNotification('종목 삭제 중 오류가 발생했습니다.', 'error');
    }
}

// 알림 설정
async function setAlert(event) {
    event.preventDefault();
    
    const ticker = document.getElementById('alertStockTicker').value;
    const type = document.getElementById('alertType').value;
    const condition = document.getElementById('alertCondition').value;
    const value = document.getElementById('alertValue').value;
    const method = document.getElementById('notificationMethod').value;
    
    if (!ticker || !type || !condition || !value || !method) {
        showNotification('모든 필드를 입력해주세요.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/alerts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ticker,
                type,
                condition,
                value: parseFloat(value),
                method
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`${ticker} 알림이 설정되었습니다.`, 'success');
            closeAlertModal();
            loadAlerts(); // 알림 목록 새로고침
        } else {
            showNotification(data.message || '알림 설정에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('알림 설정 중 오류:', error);
        showNotification('알림 설정 중 오류가 발생했습니다.', 'error');
    }
}

// 로그아웃
function logout() {
    if (confirm('로그아웃 하시겠습니까?')) {
        showNotification('로그아웃 처리 중...', 'success');
        setTimeout(() => {
            window.location.href = '/logout';
        }, 1000);
    }
}

// 알림 표시
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');
    const notificationTitle = document.getElementById('notificationTitle');
    
    notificationText.textContent = message;
    notificationTitle.textContent = type === 'error' ? '오류' : '알림';
    
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

// 유틸리티 함수들
function formatPrice(price) {
    return new Intl.NumberFormat('ko-KR').format(price);
}

function formatChange(change) {
    return new Intl.NumberFormat('ko-KR').format(Math.abs(change));
}

function formatPercent(percent) {
    return percent.toFixed(2);
}

function getAlertTypeText(type) {
    const types = {
        'price': '가격',
        'psychology': '심리도',
        'rsi': 'RSI',
        'volume': '거래량'
    };
    return types[type] || type;
}

function getAlertConditionText(alert) {
    const conditions = {
        'above': '이상',
        'below': '이하',
        'equal': '같음'
    };
    return `${getAlertTypeText(alert.type)} ${alert.value} ${conditions[alert.condition] || alert.condition}시`;
}

function getNotificationMethodText(method) {
    const methods = {
        'email': '이메일',
        'slack': '슬랙',
        'both': '이메일+슬랙'
    };
    return methods[method] || method;
}

// 모달 외부 클릭시 닫기
window.onclick = function(event) {
    const addStockModal = document.getElementById('addStockModal');
    const alertModal = document.getElementById('alertModal');
    
    if (event.target === addStockModal) {
        closeAddStockModal();
    }
    if (event.target === alertModal) {
        closeAlertModal();
    }
}

// 실시간 데이터 업데이트 시뮬레이션 (5초마다)
setInterval(() => {
    updateStockPrices();
}, 5000);

function updateStockPrices() {
    const stockItems = document.querySelectorAll('.stock-item');
    stockItems.forEach(item => {
        const priceElement = item.querySelector('.price');
        const changeElement = item.querySelector('.change');
        
        if (!priceElement || !changeElement) return;
        
        // 랜덤 가격 변동 시뮬레이션
        const randomChange = (Math.random() - 0.5) * 2000;
        const randomPercent = (Math.random() - 0.5) * 3;
        const isPositive = randomChange > 0;
        
        changeElement.className = `change ${isPositive ? 'positive' : 'negative'}`;
        changeElement.innerHTML = `${isPositive ? '+' : ''}${formatChange(randomChange)} (${formatPercent(randomPercent)}%)`;
    });
}