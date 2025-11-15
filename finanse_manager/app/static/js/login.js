document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    const inputs = {
        login: document.getElementById('login'),
        password: document.getElementById('password')
    };

    const errors = {
        login: document.getElementById('login-error'),
        password: document.getElementById('password-error')
    };

    // Валидация логина/email
    function validateLogin() {
        const value = inputs.login.value.trim();
        if (value.length === 0) {
            showError(inputs.login, errors.login, 'Поле не может быть пустым');
            return false;
        }
        if (value.length < 3) {
            showError(inputs.login, errors.login, 'Минимум 3 символа');
            return false;
        }
        hideError(inputs.login, errors.login);
        return true;
    }

    // Валидация пароля
    function validatePassword() {
        const value = inputs.password.value;
        if (value.length === 0) {
            showError(inputs.password, errors.password, 'Поле не может быть пустым');
            return false;
        }
        if (value.length < 6) {
            showError(inputs.password, errors.password, 'Минимум 6 символов');
            return false;
        }
        hideError(inputs.password, errors.password);
        return true;
    }

    // События валидации
    inputs.login.addEventListener('blur', validateLogin);
    inputs.login.addEventListener('input', function() {
        if (this.value.trim().length >= 3) {
            hideError(inputs.login, errors.login);
        }
    });

    inputs.password.addEventListener('blur', validatePassword);
    inputs.password.addEventListener('input', function() {
        if (this.value.length >= 6) {
            hideError(inputs.password, errors.password);
        }
    });

    // Real-time validation
    inputs.login.addEventListener('input', function() {
        const value = this.value.trim();
        if (value.length > 0 && value.length < 3) {
            showError(inputs.login, errors.login, 'Минимум 3 символа');
        } else if (value.length >= 3) {
            hideError(inputs.login, errors.login);
        }
    });

    inputs.password.addEventListener('input', function() {
        const value = this.value;
        if (value.length > 0 && value.length < 6) {
            showError(inputs.password, errors.password, 'Минимум 6 символов');
        } else if (value.length >= 6) {
            hideError(inputs.password, errors.password);
        }
    });

    // Валидация при отправке
    form.addEventListener('submit', function(e) {
        const isValid = validateLogin() && validatePassword();
        if (!isValid) {
            e.preventDefault();
            if (!validateLogin()) validateLogin();
            if (!validatePassword()) validatePassword();
        }
    });
});