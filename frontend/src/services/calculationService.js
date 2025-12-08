import api from './api';

export const calculationService = {
    // Optimize loading
    optimize: async (data) => {
        const response = await api.post('/calculations/optimize', data);
        return response.data;
    },

    // Validate specific nesting pair
    validateNesting: async (outerPipeId, innerPipeId) => {
        const response = await api.post('/calculations/validate-nesting', null, {
            params: {
                outer_pipe_id: outerPipeId,
                inner_pipe_id: innerPipeId
            }
        });
        return response.data;
    }
};
