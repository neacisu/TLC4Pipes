import { configureStore } from '@reduxjs/toolkit';

// Placeholder reducers
const placeholderReducer = (state = {}, action) => state;

export const store = configureStore({
    reducer: {
        app: placeholderReducer,
        // Add slices here later
    },
});
