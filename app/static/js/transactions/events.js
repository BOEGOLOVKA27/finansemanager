/**
 * Класс для управления событиями транзакций
 * Предоставляет методы для инициализации обработчиков событий формы транзакций
 */
export class Events {
    /**
     * Создает экземпляр обработчика событий
     * @param {Object} elements - Объект с DOM элементами
     * @param {Object} managers - Объект с менеджерами и API
     */
    constructor(elements, managers) {
        this.elm = elements;
        this.mng = managers.managers;
        this.api = managers.api;
    }

    /**
     * Инициализация всех обработчиков событий
     * @example
     * events.initialize();
     */
    initialize() {
        this.setupModalHandlers();
        this.setupCloseCategoryModal();
        this.setupCreateCategory();
        this.setupOperationTypeChange();
        this.setupCategoryChange();
        this.setupAmountInputFormatting();
        this.setupTriggerInitialOperationTypeSync();
        this.setupValidateTransactionForm();
        this.setupShortcutsAmount();
        this.setupFillCategoryModal();
    }

    /**
     * Установка обработчика открытия модального окна создания категории
     * @example
     * events.setupModalHandlers();
     */
    setupModalHandlers() {
        if (this.elm.createCategoryBtn) {
            this.elm.createCategoryBtn.addEventListener('click', () => {
                this.mng.openCategoryModal();
            });
        }
    }

    /**
     * Установка обработчиков закрытия модального окна создания категории
     * Обрабатывает клик вне модального окна и клик по кнопкам закрытия
     * @example
     * events.setupCloseCategoryModal();
     */
    setupCloseCategoryModal() {
        window.addEventListener('click', (event) => {
            if (event.target === this.elm.modal) {
                this.mng.closeCategoryModal();
            }
        });
        this.elm.modalCloseBtns.forEach((btn) => {
            btn.addEventListener('click', () => {
                this.mng.closeCategoryModal();
            });
        });
    }

    /**
     * Установка обработчика создания новой категории
     * Отправляет данные формы на сервер и обрабатывает ответ
     * @example
     * events.setupCreateCategory();
     */
    setupCreateCategory() {
        this.elm.categoryForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const formData = new FormData(this.elm.categoryForm);
            const url = this.elm.categoryForm.dataset.actionUrl;

            try {
                const data = await this.api.postFormData(url, formData);

                if (data.success) {
                    this.mng.handleCategoryCreated(data, this.elm.categoryId);
                } else {
                    alert('Ошибка: ' + data.errors.join(', '));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Произошла ошибка при создании категории');
            }
        });
    }

    /**
     * Установка обработчика изменения выбранной категории
     * При выборе категории автоматически устанавливает соответствующий тип операции
     * @example
     * events.setupOperationTypeChange();
     */
    setupOperationTypeChange() {
        this.elm.categoryId.addEventListener('change', () => {
            this.mng.switchTypeOperations(this.elm.categoryId);
        });
    }

    /**
     * Установка обработчиков изменения типа операции
     * При изменении типа операции фильтрует список доступных категорий
     * @example
     * events.setupCategoryChange();
     */
    setupCategoryChange() {
        this.elm.operationTypes.forEach(radio => {
            radio.addEventListener('change', () => {
                this.mng.switchTypeCategories(radio);
            });
        });
    }

    /**
     * Установка обработчика форматирования ввода суммы
     * Автоматически форматирует вводимую сумму с разделителями тысяч
     * @example
     * events.setupAmountInputFormatting();
     */
    setupAmountInputFormatting() {
        this.elm.amountInput.addEventListener('input', (event) => {
            this.mng.formatAmount(event.target);
        });
    }
    
    /**
     * Инициация синхронизации категорий при загрузке страницы
     * Вызывает событие изменения для выбранной операции
     * @example
     * events.setupTriggerInitialOperationTypeSync();
     */
    setupTriggerInitialOperationTypeSync() {
        this.mng.syncCategoriesUploading();
    }

    /**
     * Установка обработчика валидации формы транзакции
     * Проверяет корректность заполнения формы перед отправкой
     * @example
     * events.setupValidateTransactionForm();
     */
    setupValidateTransactionForm() {
        this.elm.transactionForm.addEventListener('submit', (event) => {
            if (!this.mng.validateTransactionForm()) {
                event.preventDefault();
            }
        });
    }

    setupShortcutsAmount() {
        this.elm.shortcutsAmount.forEach(btn => {
            btn.addEventListener('click', () => {
                this.mng.setQuickAmount(btn.dataset.amount);
            });
        });
    }

    setupFillCategoryModal() {
        this.elm.popularCategoriesList.forEach(category => {
            category.addEventListener('click', () => {
                const categoryName = category.dataset.categoryName;
                const categoryType = category.dataset.categoryType;
                this.mng.fillCategoryModal(categoryName, categoryType);
            })
        })
    }
}