import api from './api';

export const orderService = {
    // List all orders
    listOrders: async (params = {}) => {
        const response = await api.get('/orders/', { params });
        const orders = response.data?.orders ?? [];
        const count = response.data?.count ?? orders.length;
        return { orders, count };
    },

    // Get specific order
    getOrder: async (id) => {
        const response = await api.get(`/orders/${id}`);
        return response.data;
    },

    // Create new order
    createOrder: async (data) => {
        const response = await api.post('/orders/', data);
        return response.data;
    },

    // Add item to order
    addItem: async (orderId, data) => {
        const response = await api.post(`/orders/${orderId}/items`, data);
        return response.data;
    },

    // Delete item from order
    deleteItem: async (orderId, itemId) => {
        const response = await api.delete(`/orders/${orderId}/items/${itemId}`);
        return response.data;
    },

    // Update status
    updateStatus: async (orderId, status) => {
        const response = await api.patch(`/orders/${orderId}/status`, null, {
            params: { status }
        });
        return response.data;
    },

    // Delete order
    deleteOrder: async (id) => {
        const response = await api.delete(`/orders/${id}`);
        return response.data;
    },

    // Import from CSV
    importCsv: async (file, pipeLengthM = 12.0) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/orders/import-csv', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            params: {
                pipe_length_m: pipeLengthM
            }
        });
        return response.data;
    }
};
