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

// Восстановление JWT токена при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Приоритет 1: Проверяем localStorage (он сохраняется между перезагрузками и перезапусками сервера)
    const localToken = localStorage.getItem('access_token');
    if (localToken) {
        console.log('JWT токен восстановлен из localStorage');
        return;
    }

    // Приоритет 2: Проверяем sessionStorage (работает в рамках текущей сессии браузера)
    const sessionToken = sessionStorage.getItem('access_token');
    if (sessionToken) {
        localStorage.setItem('access_token', sessionToken);
        console.log('JWT токен восстановлен из sessionStorage и сохранен в localStorage');
        return;
    }

    console.log('JWT токен не найден');
});

// Очистка токенов при выходе пользователя
function clearAuthTokens() {
    localStorage.removeItem('access_token');
    sessionStorage.removeItem('access_token');
    console.log('JWT токены очищены');
}