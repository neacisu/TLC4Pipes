import axios from 'axios';

// Determine API base URL for both container (nginx proxy) and local dev
const runtimeBaseUrl =
    (typeof window !== 'undefined' && `${window.location.origin}/api/v1`) ||
    'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: runtimeBaseUrl,
    timeout: 60000,
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
