import api from './api';

export const pipeService = {
    // List pipes with optional filters
    listPipes: async (params = {}) => {
        const response = await api.get('/pipes/', { params });
        return response.data;
    },

    // Get a specific pipe by ID
    getPipe: async (id) => {
        const response = await api.get(`/pipes/${id}`);
        return response.data;
    },

    // Get compatible inner pipes for nesting
    getCompatiblePipes: async (hostPipeId) => {
        const response = await api.get(`/pipes/compatible/${hostPipeId}`);
        return response.data;
    }
};
