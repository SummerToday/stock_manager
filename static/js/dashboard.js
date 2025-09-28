// 전역 변수
let interests = [];
let alerts = [];
let currentMarket = 'domestic';
let marketData = {};

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function () {
    initializePage();
    loadInterests();
    loadAlerts();
    loadMarketData();
    renderMarketIndices(); 
    const userEmail = document.getElementById('userEmail').textContent;
    if (userEmail && userEmail !== 'user@example.com') {
        const userName = userEmail.split('@')[0];
        document.getElementById('userName').textContent = userName + '님';
        document.getElementById('userAvatar').textContent = userName.charAt(0).toUpperCase();
    }
});

// 초기화
function initializePage() {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.8s ease';
        document.body.style.opacity = '1';
    }, 100);

    setTimeout(() => {
        showNotification('환영합니다! 대시보드가 준비되었습니다.', 'success');
    }, 1000);
}

// 마켓 데이터 로드
function loadMarketData() {
    setTimeout(() => {
        renderMarketStocks();
        document.getElementById('domesticLoading').style.display = 'none';
        document.getElementById('overseasLoading').style.display = 'none';
    }, 800);
}

// 마켓 전환 (국내/미국만)
function switchMarket(market) {
    currentMarket = market;
    document.querySelectorAll('.btn-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelector(`[data-market="${market}"]`).classList.add('active');
    document.querySelectorAll('.market-panel').forEach(panel => panel.classList.remove('active'));
    document.getElementById(market + 'Market').classList.add('active');
    renderMarketStocks();
}

async function renderMarketStocks() {
    const gridId = currentMarket === 'domestic' ? 'domesticStockGrid' : 'overseasStockGrid';
    const grid = document.getElementById(gridId);
    const apiMarket = currentMarket === 'domestic' ? 'domestic' : 'us'; // 해외는 미국만

    try {
        const response = await fetch(`/api/market/${apiMarket}`);
        const result = await response.json();
        if (!result.success) throw new Error(result.message);

        const stocks = result.stocks;

        const stocksHtml = stocks.map(stock => `
            <div class="stock-card" data-ticker="${stock.ticker}">
                <div class="stock-header">
                    <div class="stock-info">
                        <h4>${stock.name}</h4>
                        <div class="stock-code">${stock.ticker}</div>
                    </div>
                    <div class="stock-price">
                        <div class="current-price">${formatStockPrice(stock.price, currentMarket === 'domestic')}</div>
                        <div class="price-change ${stock.change >= 0 ? 'positive' : 'negative'}">
                            ${stock.change >= 0 ? '+' : ''}${formatChange(stock.change)} (${formatPercent(stock.changePercent)}%)
                        </div>
                        ${stock.timeDiffMinutes !== undefined ? `
                            <div class="price-time" style="font-size: 12px; color: #777;">
                                ${stock.timeDiffMinutes}분 전 기준
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="stock-details">
                    <div class="detail-item">
                        <div class="detail-label">거래량</div>
                        <div class="detail-value">${formatVolume(stock.volume)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">시가총액</div>
                        <div class="detail-value">${stock.marketCap}</div>
                    </div>
                </div>
                <div class="stock-actions">
                    <button class="btn-add-interest" onclick="addToInterest('${stock.ticker}', '${stock.name}')" 
                        ${isInInterest(stock.ticker) ? 'disabled' : ''}>
                        ${isInInterest(stock.ticker) ? '이미 추가됨' : '관심종목 추가'}
                    </button>
                </div>
            </div>
        `).join('');

        grid.innerHTML = stocksHtml;

    } catch (error) {
        console.error('마켓 데이터 로딩 실패:', error);
        grid.innerHTML = '<div class="error">데이터를 불러올 수 없습니다.</div>';
    }
}

// 관심종목 추가
function addToInterest(ticker, name) {
    if (isInInterest(ticker)) {
        showNotification('이미 관심종목에 추가된 종목입니다.', 'error');
        return;
    }
    interests.push({ ticker, name, price: 0, change: 0, changePercent: 0 });
    showNotification(`${name}(${ticker})이 관심종목에 추가되었습니다.`, 'success');
    updateInterestStats();
    renderStocks();
    renderMarketStocks();
}

// 관심종목 확인
function isInInterest(ticker) {
    return interests.some(stock => stock.ticker === ticker);
}

// 관심종목 로드
async function loadInterests() {
    interests = [];
    updateInterestStats();
    renderStocks();
    document.getElementById('stockLoading').style.display = 'none';
}

// 알림 로드
async function loadAlerts() {
    alerts = [];
    updateAlertStats();
    renderAlerts();
    document.getElementById('alertLoading').style.display = 'none';
}

// 통계
function updateInterestStats() {
    document.getElementById('interestCount').textContent = interests.length;
}
function updateAlertStats() {
    const activeAlerts = alerts.filter(alert => alert.active).length;
    document.getElementById('alertCount').textContent = activeAlerts;
}

// 관심 종목 렌더링
function renderStocks() {
    const stockList = document.getElementById('stockList');
    const emptyState = document.getElementById('stockEmptyState');

    if (interests.length === 0) {
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    stockList.innerHTML = '';
}

// 알림 렌더링
function renderAlerts() {
    const alertList = document.getElementById('alertList');
    const emptyState = document.getElementById('alertEmptyState');

    if (alerts.length === 0) {
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    alertList.innerHTML = '';
}

// 모달 열고 닫기
function openAddStockModal() {
    document.getElementById('addStockModal').style.display = 'block';
    document.getElementById('stockTicker').focus();
}
function closeAddStockModal() {
    document.getElementById('addStockModal').style.display = 'none';
    document.getElementById('addStockForm').reset();
}
function openAlertModal(ticker) {
    document.getElementById('alertStockTicker').value = ticker;
    document.getElementById('alertModal').style.display = 'block';
}
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
    interests.push({ ticker, name: name || ticker, price: 0, change: 0, changePercent: 0 });
    showNotification(`${ticker} 종목이 추가되었습니다.`, 'success');
    closeAddStockModal();
    updateInterestStats();
    renderStocks();
    renderMarketStocks();
}

// 종목 삭제
async function removeStock(ticker) {
    if (!confirm(`${ticker} 종목을 삭제하시겠습니까?`)) return;
    interests = interests.filter(stock => stock.ticker !== ticker);
    showNotification(`${ticker} 종목이 삭제되었습니다.`, 'success');
    updateInterestStats();
    renderStocks();
    renderMarketStocks();
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

    const newAlert = {
        id: alerts.length + 1,
        ticker,
        stockName: interests.find(s => s.ticker === ticker)?.name || ticker,
        type,
        condition,
        value: parseFloat(value),
        method,
        active: true
    };
    alerts.push(newAlert);
    showNotification(`${ticker} 알림이 설정되었습니다.`, 'success');
    closeAlertModal();
    updateAlertStats();
    renderAlerts();
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

async function renderMarketIndices() {
    try {
        const response = await fetch('/api/market/indices');
        const result = await response.json();
        if (!result.success) throw new Error(result.message);

        const indices = result.indices;

        // Helper function: 숫자 포맷
        const formatNumber = (value) =>
            typeof value === 'number' ? value.toLocaleString('ko-KR', { maximumFractionDigits: 2 }) : '-';

        const renderIndex = (idPrefix, data) => {
            const indexElem = document.getElementById(`${idPrefix}Index`);
            const changeElem = document.getElementById(`${idPrefix}Change`);
            const timeElem = document.getElementById(`${idPrefix}Time`);

            if (!indexElem || !changeElem) return;

            indexElem.textContent = formatNumber(data.value);
            changeElem.textContent = `${data.change >= 0 ? '+' : ''}${formatNumber(data.change)} (${formatNumber(data.changePercent)}%)`;
            changeElem.className = `market-change ${data.change >= 0 ? 'positive' : 'negative'}`;

            if (timeElem && data.timeDiffMinutes !== undefined) {
                timeElem.textContent = `${data.timeDiffMinutes}분 전 기준`;
            }
        };

        // 국내 지수
        if (indices.kospi) renderIndex('kospi', indices.kospi);
        if (indices.kosdaq) renderIndex('kosdaq', indices.kosdaq);
        
        // 미국 지수 - 나스닥 표시
        if (indices.nasdaq) renderIndex('nasdaq', indices.nasdaq);

        console.log('[DEBUG] 지수 업데이트 완료:', Object.keys(indices));

    } catch (error) {
        console.error('지수 데이터 로딩 실패:', error);
    }
}

// 유틸리티
function formatPrice(price) {
    return new Intl.NumberFormat('ko-KR').format(price);
}
function formatStockPrice(price, isDomestic) {
    return isDomestic
        ? formatPrice(price) + '원'
        : '$' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2 }).format(price);
}
function formatChange(change) {
    return formatPrice(Math.abs(change));
}
function formatPercent(percent) {
    return percent.toFixed(2);
}
function formatVolume(volume) {
    if (volume >= 1000000) return (volume / 1000000).toFixed(1) + 'M';
    if (volume >= 1000) return (volume / 1000).toFixed(1) + 'K';
    return volume.toLocaleString();
}
function getAlertTypeText(type) {
    const types = { price: '가격', psychology: '심리도', rsi: 'RSI', volume: '거래량' };
    return types[type] || type;
}
function getAlertConditionText(alert) {
    const conditions = { above: '이상', below: '이하', equal: '같음' };
    return `${getAlertTypeText(alert.type)} ${alert.value} ${conditions[alert.condition] || alert.condition}시`;
}
function getNotificationMethodText(method) {
    const methods = { email: '이메일', slack: '슬랙', both: '이메일+슬랙' };
    return methods[method] || method;
}

// 외부 클릭 시 모달 닫기
window.onclick = function (event) {
    if (event.target === document.getElementById('addStockModal')) closeAddStockModal();
    if (event.target === document.getElementById('alertModal')) closeAlertModal();
};

// 주기적 갱신
setInterval(() => {
    updateMarketPrices();
    updateStockPrices();
}, 10000);

async function updateMarketPrices() {
    await renderMarketIndices(); // 지수 갱신 함수
    renderMarketStocks();       // 종목 갱신
}

function updateStockPrices() {
    renderStocks(); // 관심종목 가격 갱신
}

// 초기 마켓 설정
setTimeout(() => {
    switchMarket('domestic');
}, 1500);