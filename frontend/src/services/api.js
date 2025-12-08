import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 60000, // 60 seconds
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle common errors here (e.g., 401 Unauthorized, Network Error)
        console.error('API Error:', error.response || error.message);
        return Promise.reject(error);
    }
);

export default api;
