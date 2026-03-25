/**
 * Класс для отправки fetch-запросов к серверу
 * Предоставляет методы для взаимодействия с серверным API
 */
export class ServerAPI {
    /**
     * Получение JWT токена из localStorage
     * @returns {string|null} Токен авторизации или null
     */
    getAuthToken() {
        return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    }

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
            headers: { 
                'X-Requested-With': 'XMLHttpRequest'
            }
        })

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Ошибка сервера');
        }

        const data = await response.json();
        return data;
    }

    /**
     * Отправка GET-запроса с авторизацией
     * @param {string} url - URL для отправки запроса
     * @param {Object} params - Параметры запроса
     * @returns {Promise<Object>} Ответ от сервера в формате JSON
     * @throws {Error} Ошибка при неудачном запросе
     */
    async get(url, params = {}) {
        const token = this.getAuthToken();
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;

        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(fullUrl, {
            method: 'GET',
            headers
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Ошибка сервера');
        }

        const data = await response.json();
        return data;
    }

    /**
     * Отправка POST-запроса с JSON данными и авторизацией
     * @param {string} url - URL для отправки запроса
     * @param {Object} data - Данные для отправки в формате JSON
     * @returns {Promise<Object>} Ответ от сервера в формате JSON
     * @throws {Error} Ошибка при неудачном запросе
     */
    async post(url, data) {
        const token = this.getAuthToken();

        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Ошибка сервера');
        }

        const result = await response.json();
        return result;
    }

    /**
     * Отправка PUT-запроса с JSON данными и авторизацией
     * @param {string} url - URL для отправки запроса
     * @param {Object} data - Данные для отправки в формате JSON
     * @returns {Promise<Object>} Ответ от сервера в формате JSON
     * @throws {Error} Ошибка при неудачном запросе
     */
    async put(url, data) {
        const token = this.getAuthToken();

        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            method: 'PUT',
            headers,
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Ошибка сервера');
        }

        const result = await response.json();
        return result;
    }

    /**
     * Отправка DELETE-запроса с авторизацией
     * @param {string} url - URL для отправки запроса
     * @returns {Promise<Object>} Ответ от сервера в формате JSON
     * @throws {Error} Ошибка при неудачном запросе
     */
    async delete(url) {
        const token = this.getAuthToken();

        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            method: 'DELETE',
            headers
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Ошибка сервера');
        }

        const result = await response.json();
        return result;
    }
}