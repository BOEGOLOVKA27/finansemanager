/**
 * Инициализация модуля транзакций
 * 
 * Этот модуль отвечает за инициализацию всех компонентов, необходимых
 * для работы с транзакциями: получение DOM-элементов, создание менеджеров
 * и регистрацию обработчиков событий.
 */

import { Managers } from './managers.js';
import { Events } from './events.js';
import { ServerAPI } from '../server.js';

/**
 * Основная функция инициализации транзакций
 * 
 * Выполняет последовательную инициализацию всех компонентов:
 * 1. Получает ссылки на DOM-элементы
 * 2. Создает менеджеры для управления логикой
 * 3. Регистрирует обработчики событий
 */
export function initializeTransactions() {
    const elements = getEditorElements();
    const managers = initializeManagers(elements);
    registerHandlers(elements, managers);
}

/**
 * Получает ссылки на все необходимые DOM-элементы
 * 
 * @returns {Object} Объект с ссылками на DOM-элементы
 */
function getEditorElements() {
    return {
        amountInput: document.getElementById('amount'),
        createCategoryBtn: document.getElementById('create-category-btn'),
        modal: document.getElementById('categoryModal'),
        modalCloseBtns: document.querySelectorAll('.modal-close-btn'),
        categoryId: document.getElementById('category_id'),
        transactionForm: document.getElementById('transactionForm'),
        categoryForm: document.getElementById('categoryForm'),
        operationTypes: document.querySelectorAll('input[name="operation_type"]'),
        selectedOperation: document.querySelector('input[name="operation_type"]:checked'),
        shortcutsAmount: document.getElementById('quick-amounts-buttons').childNodes,
        popularCategoriesList: document.getElementById('popular-categories-list').childNodes
    };
}

/**
 * Инициализирует менеджеры для работы с транзакциями
 * 
 * @param {Object} elements - Объект с DOM-элементами
 * @returns {Object} Объект с инициализированными менеджерами
 */
function initializeManagers(elements) {
    return {
        managers: new Managers(elements),
        api: new ServerAPI()
    };
}

/**
 * Регистрирует обработчики событий для транзакций
 * 
 * @param {Object} elements - Объект с DOM-элементами
 * @param {Object} managers - Объект с менеджерами
 */
function registerHandlers(elements, managers) {
    const events = new Events(elements, managers);
    events.initialize();
}