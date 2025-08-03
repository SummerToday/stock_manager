/**
 * Stock Manager 로그인 페이지 JavaScript
 */

// 로딩 상태 표시 함수
function showLoading() {
    const loading = document.getElementById('loading');
    const loginBtn = document.querySelector('.google-login-btn');

    if (loading && loginBtn) {
        loading.classList.add('show');
        loginBtn.style.opacity = '0.6';
        loginBtn.style.pointerEvents = 'none';
    }
}

// 로딩 상태 숨김 함수
function hideLoading() {
    const loading = document.getElementById('loading');
    const loginBtn = document.querySelector('.google-login-btn');

    if (loading && loginBtn) {
        loading.classList.remove('show');
        loginBtn.style.opacity = '1';
        loginBtn.style.pointerEvents = 'auto';
    }
}

// 페이지 로드 애니메이션
function initPageAnimation() {
    const container = document.querySelector('.login-container');

    if (container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';

        setTimeout(() => {
            container.style.transition = 'all 0.6s ease';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
    }
}

// 기능 카드 호버 효과
function initFeatureCardEffects() {
    const features = document.querySelectorAll('.feature');

    features.forEach(feature => {
        feature.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.3s ease';
            this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
        });

        feature.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
}

// 로그인 버튼 클릭 시 로딩 표시만 하고 리디렉션은 기본 링크 동작으로
function initLoginButton() {
    const loginBtn = document.querySelector('.google-login-btn');

    if (loginBtn) {
        loginBtn.addEventListener('click', function () {
            // 이미 로딩 중이면 무시
            if (this.style.pointerEvents === 'none') {
                return;
            }

            showLoading();

            console.log('Google 로그인으로 리디렉트 중...');

            setTimeout(() => {
                if (document.querySelector('.loading.show')) {
                    console.log('로그인 타임아웃 - 로딩 상태 리셋');
                    hideLoading();
                }
            }, 10000);
        });
    }
}

// 키보드 접근성 개선
function initAccessibility() {
    const loginBtn = document.querySelector('.google-login-btn');

    if (loginBtn) {
        loginBtn.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    }
}

// 페이지 가시성 감지
function initVisibilityHandler() {
    document.addEventListener('visibilitychange', function () {
        if (!document.hidden) {
            const loading = document.querySelector('.loading.show');
            if (loading) {
                setTimeout(() => {
                    if (document.querySelector('.loading.show')) {
                        hideLoading();
                    }
                }, 1000);
            }
        }
    });
}

// 초기화
document.addEventListener('DOMContentLoaded', function () {
    console.log('Stock Manager 로그인 페이지 로드됨');
    initPageAnimation();
    initFeatureCardEffects();
    initLoginButton();
    initAccessibility();
    initVisibilityHandler();
});

window.addEventListener('beforeunload', function () {
    hideLoading();
});
