// 전역 변수
let interests = [];
let alerts = [];
let currentMarket = 'domestic';
let currentOverseasMarket = 'us';
let marketData = {};

// 실시간 주가 데이터 (시뮬레이션용)
const stockData = {
    domestic: [
        { ticker: '005930', name: '삼성전자', price: 75000, change: 500, changePercent: 0.67, volume: 15000000, marketCap: '448조' },
        { ticker: '000660', name: 'SK하이닉스', price: 120000, change: -2000, changePercent: -1.64, volume: 8500000, marketCap: '87조' },
        { ticker: '035420', name: 'NAVER', price: 205000, change: 3500, changePercent: 1.74, volume: 1200000, marketCap: '34조' },
        { ticker: '005380', name: '현대차', price: 180000, change: -1500, changePercent: -0.83, volume: 2100000, marketCap: '38조' },
        { ticker: '006400', name: '삼성SDI', price: 680000, change: 15000, changePercent: 2.26, volume: 450000, marketCap: '31조' },
        { ticker: '051910', name: 'LG화학', price: 850000, change: -8000, changePercent: -0.93, volume: 320000, marketCap: '60조' },
        { ticker: '068270', name: '셀트리온', price: 195000, change: 2800, changePercent: 1.46, volume: 1800000, marketCap: '26조' },
        { ticker: '035720', name: '카카오', price: 68500, change: -1200, changePercent: -1.72, volume: 3200000, marketCap: '25조' }
    ],
    overseas: {
        us: [
            { ticker: 'AAPL', name: 'Apple Inc.', price: 175.50, change: 2.30, changePercent: 1.33, volume: 55000000, marketCap: '$2.7T' },
            { ticker: 'MSFT', name: 'Microsoft Corp.', price: 345.20, change: -1.80, changePercent: -0.52, volume: 28000000, marketCap: '$2.6T' },
            { ticker: 'GOOGL', name: 'Alphabet Inc.', price: 135.80, change: 0.95, changePercent: 0.70, volume: 32000000, marketCap: '$1.7T' },
            { ticker: 'AMZN', name: 'Amazon.com Inc.', price: 142.60, change: -2.10, changePercent: -1.45, volume: 45000000, marketCap: '$1.5T' },
            { ticker: 'TSLA', name: 'Tesla Inc.', price: 245.80, change: 8.70, changePercent: 3.67, volume: 85000000, marketCap: '$780B' },
            { ticker: 'NVDA', name: 'NVIDIA Corp.', price: 520.30, change: 15.20, changePercent: 3.01, volume: 42000000, marketCap: '$1.3T' },
            { ticker: 'META', name: 'Meta Platforms', price: 385.90, change: -5.40, changePercent: -1.38, volume: 18000000, marketCap: '$980B' },
            { ticker: 'NFLX', name: 'Netflix Inc.', price: 465.20, change: 12.80, changePercent: 2.83, volume: 15000000, marketCap: '$205B' }
        ],
        japan: [
            { ticker: '7203', name: 'Toyota Motor', price: 2850, change: 45, changePercent: 1.60, volume: 8500000, marketCap: '¥42조' },
            { ticker: '6758', name: 'Sony Group', price: 12500, change: -180, changePercent: -1.42, volume: 2100000, marketCap: '¥15조' },
            { ticker: '9984', name: 'SoftBank Group', price: 6200, change: 120, changePercent: 1.97, volume: 3200000, marketCap: '¥13조' },
            { ticker: '6861', name: 'Keyence', price: 65000, change: -800, changePercent: -1.22, volume: 450000, marketCap: '¥12조' },
            { ticker: '4063', name: 'Shin-Etsu Chemical', price: 18500, change: 250, changePercent: 1.37, volume: 1200000, marketCap: '¥8조' },
            { ticker: '8035', name: 'Tokyo Electron', price: 22000, change: -350, changePercent: -1.57, volume: 890000, marketCap: '¥7조' }
        ],
        china: [
            { ticker: '00700', name: 'Tencent', price: 365.50, change: -8.20, changePercent: -2.19, volume: 15000000, marketCap: 'HK$3.5T' },
            { ticker: '09988', name: 'Alibaba', price: 98.50, change: 2.80, changePercent: 2.93, volume: 22000000, marketCap: 'HK$2.1T' },
            { ticker: '01024', name: 'Kuaishou', price: 68.20, change: -1.50, changePercent: -2.15, volume: 8500000, marketCap: 'HK$295B' },
            { ticker: '03690', name: 'Meituan', price: 125.30, change: 3.70, changePercent: 3.04, volume: 12000000, marketCap: 'HK$775B' },
            { ticker: '02318', name: 'Ping An Insurance', price: 45.80, change: -0.90, changePercent: -1.93, volume: 18000000, marketCap: 'HK$837B' },
            { ticker: '00175', name: 'Geely Automobile', price: 12.50, change: 0.35, changePercent: 2.88, volume: 25000000, marketCap: 'HK$136B' }
        ],
        europe: [
            { ticker: 'ASML', name: 'ASML Holding', price: 685.50, change: 12.30, changePercent: 1.83, volume: 2100000, marketCap: '€280B' },
            { ticker: 'SAP', name: 'SAP SE', price: 125.80, change: -2.40, changePercent: -1.87, volume: 1850000, marketCap: '€145B' },
            { ticker: 'LVMH', name: 'LVMH', price: 780.20, change: 15.60, changePercent: 2.04, volume: 850000, marketCap: '€390B' },
            { ticker: 'TTE', name: 'TotalEnergies', price: 58.90, change: -1.10, changePercent: -1.83, volume: 3200000, marketCap: '€155B' },
            { ticker: 'NVO', name: 'Novo Nordisk', price: 105.30, change: 2.80, changePercent: 2.73, volume: 1200000, marketCap: '€485B' },
            { ticker: 'UNA', name: 'Unilever', price: 48.50, change: -0.75, changePercent: -1.52, volume: 2800000, marketCap: '€120B' }
        ]
    }
};

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    loadInterests();
    loadAlerts();
    loadMarketData();
    
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

// 마켓 데이터 로드
function loadMarketData() {
    setTimeout(() => {
        renderMarketStocks();
        document.getElementById('domesticLoading').style.display = 'none';
        document.getElementById('overseasLoading').style.display = 'none';
    }, 800);
}

// 마켓 전환
function switchMarket(market) {
    currentMarket = market;
    
    // 탭 상태 업데이트
    document.querySelectorAll('.btn-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-market="${market}"]`).classList.add('active');
    
    // 패널 전환
    document.querySelectorAll('.market-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(market + 'Market').classList.add('active');
    
    // 데이터 렌더링
    renderMarketStocks();
}

// 해외 마켓 변경
function changeOverseasMarket() {
    const selectElement = document.getElementById('overseasMarketSelect');
    currentOverseasMarket = selectElement.value;
    
    // 마켓 정보 업데이트
    updateOverseasMarketInfo();
    renderMarketStocks();
}

// 해외 마켓 정보 업데이트
function updateOverseasMarketInfo() {
    const marketInfo = {
        us: { name: 'S&P 500', index: '4,200.00', change: '-15.30 (-0.36%)' },
        japan: { name: 'Nikkei 225', index: '33,500.00', change: '+120.50 (+0.36%)' },
        china: { name: 'Hang Seng', index: '17,800.00', change: '-85.20 (-0.48%)' },
        europe: { name: 'STOXX 600', index: '456.80', change: '+2.40 (+0.53%)' }
    };
    
    const info = marketInfo[currentOverseasMarket];
    if (info) {
        document.querySelector('#overseasMarket .market-name').textContent = info.name;
        document.getElementById('sp500Index').textContent = info.index;
        const changeElement = document.getElementById('sp500Change');
        changeElement.textContent = info.change;
        changeElement.className = `market-change ${info.change.startsWith('+') ? 'positive' : 'negative'}`;
    }
}

// 마켓 주식 렌더링
function renderMarketStocks() {
    const gridId = currentMarket === 'domestic' ? 'domesticStockGrid' : 'overseasStockGrid';
    const grid = document.getElementById(gridId);
    
    let stocks = [];
    if (currentMarket === 'domestic') {
        stocks = stockData.domestic;
    } else {
        stocks = stockData.overseas[currentOverseasMarket] || [];
    }
    
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
}

// 관심종목에 추가
function addToInterest(ticker, name) {
    if (isInInterest(ticker)) {
        showNotification('이미 관심종목에 추가된 종목입니다.', 'error');
        return;
    }
    
    // 실제 API 호출 대신 시뮬레이션
    setTimeout(() => {
        interests.push({ ticker, name, price: 0, change: 0, changePercent: 0 });
        showNotification(`${name}(${ticker})이 관심종목에 추가되었습니다.`, 'success');
        updateInterestStats();
        renderStocks();
        renderMarketStocks(); // 버튼 상태 업데이트
    }, 500);
}

// 관심종목에 있는지 확인
function isInInterest(ticker) {
    return interests.some(stock => stock.ticker === ticker);
}

// 관심 종목 로드
async function loadInterests() {
    try {
        // 실제 API 호출 대신 시뮬레이션 데이터 사용
        setTimeout(() => {
            interests = [
                { ticker: '005930', name: '삼성전자', price: 75000, change: 500, changePercent: 0.67 },
                { ticker: '000660', name: 'SK하이닉스', price: 120000, change: -2000, changePercent: -1.64 }
            ];
            updateInterestStats();
            renderStocks();
            document.getElementById('stockLoading').style.display = 'none';
        }, 1000);
    } catch (error) {
        console.error('관심 종목 로드 중 오류:', error);
    }
}

// 알림 목록 로드
async function loadAlerts() {
    try {
        // 실제 API 호출 대신 시뮬레이션 데이터 사용
        setTimeout(() => {
            alerts = [
                { id: 1, ticker: '005930', stockName: '삼성전자', type: 'price', condition: 'above', value: 80000, method: 'email', active: true },
                { id: 2, ticker: '000660', stockName: 'SK하이닉스', type: 'rsi', condition: 'below', value: 30, method: 'slack', active: true }
            ];
            updateAlertStats();
            renderAlerts();
            document.getElementById('alertLoading').style.display = 'none';
        }, 1200);
    } catch (error) {
        console.error('알림 목록 로드 중 오류:', error);
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
        // 실제 API 호출 대신 시뮬레이션
        setTimeout(() => {
            interests.push({ 
                ticker, 
                name: name || ticker, 
                price: Math.floor(Math.random() * 100000) + 10000,
                change: Math.floor(Math.random() * 2000) - 1000,
                changePercent: (Math.random() * 4) - 2
            });
            showNotification(`${ticker} 종목이 추가되었습니다.`, 'success');
            closeAddStockModal();
            updateInterestStats();
            renderStocks();
            renderMarketStocks(); // 마켓 목록에서 버튼 상태 업데이트
        }, 500);
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
        // 실제 API 호출 대신 시뮬레이션
        setTimeout(() => {
            interests = interests.filter(stock => stock.ticker !== ticker);
            showNotification(`${ticker} 종목이 삭제되었습니다.`, 'success');
            updateInterestStats();
            renderStocks();
            renderMarketStocks(); // 마켓 목록에서 버튼 상태 업데이트
        }, 300);
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
        // 실제 API 호출 대신 시뮬레이션
        setTimeout(() => {
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
        }, 500);
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

function formatStockPrice(price, isDomestic) {
    if (isDomestic) {
        return new Intl.NumberFormat('ko-KR').format(price) + '원';
    } else {
        return '$' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2 }).format(price);
    }
}

function formatChange(change) {
    return new Intl.NumberFormat('ko-KR').format(Math.abs(change));
}

function formatPercent(percent) {
    return percent.toFixed(2);
}

function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toLocaleString();
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

// 실시간 데이터 업데이트 시뮬레이션 (10초마다)
setInterval(() => {
    updateMarketPrices();
    updateStockPrices();
}, 10000);

function updateMarketPrices() {
    // 마켓 주식 가격 업데이트
    const currentStocks = currentMarket === 'domestic' 
        ? stockData.domestic 
        : stockData.overseas[currentOverseasMarket];
    
    if (currentStocks) {
        currentStocks.forEach(stock => {
            const randomChange = (Math.random() - 0.5) * (stock.price * 0.02);
            const randomPercent = (randomChange / stock.price) * 100;
            
            stock.change = randomChange;
            stock.changePercent = randomPercent;
            stock.price = Math.max(stock.price + randomChange, stock.price * 0.5);
        });
        
        renderMarketStocks();
    }
}

function updateStockPrices() {
    // 관심 종목 가격 업데이트
    interests.forEach(stock => {
        const randomChange = (Math.random() - 0.5) * 2000;
        const randomPercent = (Math.random() - 0.5) * 3;
        
        stock.change = randomChange;
        stock.changePercent = randomPercent;
    });
    
    renderStocks();
}

// 초기화 완료 후 첫 마켓 데이터 로드
setTimeout(() => {
    switchMarket('domestic');
}, 1500);