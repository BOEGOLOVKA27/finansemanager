// Функция для переключения видимости пароля
function initPasswordToggle() {
    document.addEventListener('click', (e) => {
        if (e.target.closest('.toggle-password')) {
            const button = e.target.closest('.toggle-password');
            const input = button.previousElementSibling;
            const icon = button.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
            }
        }
    });
}

// Вспомогательные функции для валидации
function showError(input, errorElement, message) {
    input.classList.add('invalid');
    input.classList.remove('valid');
    errorElement.textContent = message;
    errorElement.classList.add('show');
}

function hideError(input, errorElement) {
    input.classList.remove('invalid');
    input.classList.add('valid');
    errorElement.classList.remove('show');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggle();
});

// Обработка показа/скрытия пароля
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
});

// Восстановление JWT токена из sessionStorage при перезагрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли токен в sessionStorage (сохранен после входа)
    const storedToken = sessionStorage.getItem('access_token');
    if (storedToken) {
        localStorage.setItem('access_token', storedToken);
        console.log('JWT токен восстановлен из sessionStorage');
    }
    
    // Также проверяем, есть ли токен в localStorage (для случаев когда сессия активна)
    const localToken = localStorage.getItem('access_token');
    if (localToken) {
        console.log('JWT токен найден в localStorage');
    }
});

// Очистка токенов при выходе пользователя
function clearAuthTokens() {
    localStorage.removeItem('access_token');
    sessionStorage.removeItem('access_token');
    console.log('JWT токены очищены');
}