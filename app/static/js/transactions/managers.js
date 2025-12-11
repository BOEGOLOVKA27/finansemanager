/**
 * Класс для управления элементами интерфейса транзакций
 * Предоставляет методы для форматирования сумм, работы с модальными окнами и уведомлениями
 */
export class Managers {
    /**
     * Создает экземпляр менеджера
     * @param {Object} elements - Объект с DOM элементами
     */
    constructor(elements) {
        this.elm = elements;
    }

    /**
     * Форматирование суммы с разделителями тысяч
     * @param {HTMLInputElement} input - Поле ввода суммы
     * @example
     * manager.formatAmount(document.getElementById('amount'));
     */
    formatAmount(input) {
        let value = input.value.replace(/[^\d.]/g, '');
        
        // Разделяем на целую и дробную части
        let parts = value.split('.');
        let integerPart = parts[0];
        let decimalPart = parts.length > 1 ? '.' + parts[1].substring(0, 2) : '';
        
        // Форматируем целую часть с разделителями тысяч
        integerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        
        input.value = integerPart + decimalPart;
    }

    /**
     * Установка быстрой суммы в поле ввода
     * @param {number} amount - Сумма для установки
     * @example
     * manager.setQuickAmount(1000);
     */
    setQuickAmount(amount) {
        const amountInput = document.getElementById('amount');
        amountInput.value = amount.toLocaleString('ru-RU');
        amountInput.focus();
    }

    /**
     * Заполнение модального окна для создания категории
     * @param {string} name - Название категории
     * @param {string} type - Тип категории (income/expense)
     * @example
     * manager.fillCategoryModal('Продукты', 'expense');
     */
    fillCategoryModal(name, type) {
        document.getElementById('new_category_name').value = name;
        document.getElementById(`new_type_${type.toLowerCase()}`).checked = true;
        openCategoryModal();
    }

    /**
     * Открытие модального окна создания категории
     * @example
     * manager.openCategoryModal();
     */
    openCategoryModal() {
        document.getElementById('categoryModal').style.display = 'flex';
        document.getElementById('new_category_name').focus();
    }

    /**
     * Закрытие модального окна создания категории
     * @example
     * manager.closeCategoryModal();
     */
    closeCategoryModal() {
        document.getElementById('categoryModal').style.display = 'none';
        document.getElementById('categoryForm').reset();
    }

    /**
     * Показ уведомления пользователю
     * @param {string} message - Текст уведомления
     * @param {string} type - Тип уведомления (success, error, warning, info)
     * @example
     * manager.showNotification('Операция выполнена успешно', 'success');
     */
    showNotification(message, type) {
        // Простая реализация уведомления
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    /**
     * Обработка успешного создания категории
     * @param {Object} data - Данные категории из ответа сервера
     * @param {HTMLSelectElement} categoryIdSelect - Элемент select для категорий
     * @example
     * manager.handleCategoryCreated(data, document.getElementById('category_id'));
     */
    handleCategoryCreated(data, categoryIdSelect) {
        const newOption = new Option(
            data.category.name + ' (' + (data.category.operation_type === 'INCOME' ? 'Доход' : 'Расход') + ')', 
            data.category.id
        );
        newOption.setAttribute('data-type', data.category.operation_type);
        categoryIdSelect.appendChild(newOption);
        categoryIdSelect.value = data.category.id;

        this.closeCategoryModal();
        this.showNotification('Категория успешно создана!', 'success');
    }

    /**
     * Переключение отображения категорий по типу операции
     * @param {HTMLInputElement} radio - Радио-кнопка типа операции
     * @example
     * manager.switchTypeCategories(document.querySelector('input[name="type"]:checked'));
     */
    switchTypeCategories(radio) {
        const selectedType = radio.value;
                
        for (let option of this.elm.categoryId.options) {
            if (option.value === '') continue;
            
            const categoryType = option.dataset.type;
            if (categoryType === selectedType) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
                if (option.selected && categoryType !== selectedType) {
                    this.elm.categoryId.value = '';
                }
            }
        }
    }

    /**
     * Переключение типа операции в зависимости от выбранной категории
     * @param {HTMLSelectElement} categoryId - Элемент select с категориями
     * @example
     * manager.switchTypeOperations(document.getElementById('category_id'));
     */
    switchTypeOperations(categoryId) {
        const selectedOption = categoryId.options[categoryId.selectedIndex];
        const operationType = selectedOption.dataset.type;
        
        if (operationType) {
            document.getElementById(`type_${operationType.toLowerCase()}`).checked = true;
        }
    }

    /**
     * Синхронизация категорий при загрузке страницы
     * Вызывает событие изменения для выбранной операции
     * @example
     * manager.syncCategoriesUploading();
     */
    syncCategoriesUploading() {
        const selectedOperation = this.elm.selectedOperation;
        if (selectedOperation) {
            selectedOperation.dispatchEvent(new Event('change'));
        }
    }

    /**
     * Валидация формы транзакции перед отправкой
     * Проверяет заполнение обязательных полей и корректность суммы
     * @returns {boolean} - Результат валидации
     * @example
     * if (manager.validateTransactionForm()) { submitForm(); }
     */
    validateTransactionForm() {
        let amountValue = this.elm.amountInput.value.replace(/\s/g, '').replace(',', '.');
        amountValue = parseFloat(amountValue);
        
        let isValid = true;
        
        if (!this.elm.selectedOperation) {
            alert('Выберите тип операции');
            isValid = false;
        } else if (!this.elm.categoryId.value) {
            alert('Выберите категорию');
            isValid = false;
        } else if (!amountValue || amountValue <= 0 || isNaN(amountValue)) {
            alert('Введите корректную сумму');
            isValid = false;
        }
        
        if (isValid) {
            this.elm.amountInput.value = amountValue.toFixed(2);
            return true;
        } else {
            return false;
        }
    }
}