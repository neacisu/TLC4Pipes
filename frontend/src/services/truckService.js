import api from './api';

export const truckService = {
    // List available truck configs
    listTrucks: async () => {
        const response = await api.get('/calculations/trucks/');
        return response.data;
    }
};
