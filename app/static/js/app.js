import { initializeTransactions } from './transactions/init.js';

/**
 * Определяет текущую страницу на основе URL.
 *
 * @returns {string} Идентификатор текущей страницы ('transactions' или 'home')
 */
function getCurrentPage() {
    const path = window.location.pathname;

    if (/\/transactions\//.test(path)) return 'transactions';
    return 'home';
}

/**
 * Инициализация приложения.
 */
document.addEventListener('DOMContentLoaded', function() {
    const page = getCurrentPage();

    switch (page) {
        case 'transactions':
            initializeTransactions();
            break;
        default:
            console.log('Home page loaded');
    }

    console.log(`App initialized (page: ${page})`);
});