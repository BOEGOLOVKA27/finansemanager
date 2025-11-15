document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    if (!form) return;

    const inputs = {
        login: document.getElementById('login'),
        email: document.getElementById('email'),
        password: document.getElementById('password'),
        replaypassword: document.getElementById('replaypassword')
    };

    const errors = {
        login: document.getElementById('login-error'),
        email: document.getElementById('email-error'),
        password: document.getElementById('password-error'),
        passwordMatch: document.getElementById('password-match-error')
    };

    // Валидация логина
    function validateLogin() {
        const value = inputs.login.value.trim();
        if (value.length < 3) {
            showError(inputs.login, errors.login, 'Минимум 3 символа');
            return false;
        }
        hideError(inputs.login, errors.login);
        return true;
    }

    // Валидация email
    function validateEmail() {
        const value = inputs.email.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showError(inputs.email, errors.email, 'Введите корректный email');
            return false;
        }
        hideError(inputs.email, errors.email);
        return true;
    }

    // Валидация пароля
    function validatePassword() {
        const value = inputs.password.value;
        if (value.length < 6) {
            showError(inputs.password, errors.password, 'Минимум 6 символов');
            return false;
        }
        hideError(inputs.password, errors.password);
        return true;
    }

    // Проверка совпадения паролей
    function validatePasswordMatch() {
        if (inputs.password.value !== inputs.replaypassword.value) {
            showError(inputs.replaypassword, errors.passwordMatch, 'Пароли не совпадают');
            return false;
        }
        hideError(inputs.replaypassword, errors.passwordMatch);
        return true;
    }

    // События
    inputs.login.addEventListener('blur', validateLogin);
    inputs.email.addEventListener('blur', validateEmail);
    inputs.password.addEventListener('blur', validatePassword);
    inputs.replaypassword.addEventListener('input', validatePasswordMatch);

    // Валидация при отправке
    form.addEventListener('submit', function(e) {
        const isValid = validateLogin() && validateEmail() && validatePassword() && validatePasswordMatch();
        if (!isValid) {
            e.preventDefault();
        }
    });
});