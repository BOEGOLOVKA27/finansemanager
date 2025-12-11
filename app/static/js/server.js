/**
 * Класс для отправки fetch-запросов к серверу
 * Предоставляет методы для взаимодействия с серверным API
 */
export class ServerAPI {
    /**
     * Отправка POST-запроса с данными формы
     * @param {string} url - URL для отправки запроса
     * @param {FormData} formData - Данные формы для отправки
     * @returns {Promise<Object>} Ответ от сервера в формате JSON
     * @throws {Error} Ошибка при неудачном запросе
     */
    async postFormData(url, formData) {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Ошибка сервера');
        }

        const data = await response.json();
        return data;
    }
}