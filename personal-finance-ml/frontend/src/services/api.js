const API_URL = 'http://127.0.0.1:8000/api';

export const apiCall = async (endpoint, method = 'GET', body = null, token = null) => {
    const headers = {
        'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        const data = await response.json();

        if (!response.ok) {
            // DRF usually returns errors in an object or array
            const errorMsg = data.detail || (typeof data === 'object' ? Object.values(data)[0][0] : 'Something went wrong');
            throw new Error(errorMsg);
        }

        return data;
    } catch (err) {
        throw err;
    }
};
