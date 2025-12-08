import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { orderService } from '../../services/orderService'

export const createOrder = createAsyncThunk(
    'order/create',
    async (orderData, { rejectWithValue }) => {
        try {
            const response = await orderService.create(orderData)
            return response.data
        } catch (error) {
            return rejectWithValue(error.response?.data || 'Failed to create order')
        }
    }
)

const initialState = {
    currentOrder: null,
    orders: [],
    items: [],
    pipeLength: 12.0,
    loading: false,
    error: null,
}

const orderSlice = createSlice({
    name: 'order',
    initialState,
    reducers: {
        setPipeLength: (state, action) => {
            state.pipeLength = action.payload
        },
        addItem: (state, action) => {
            state.items.push(action.payload)
        },
        removeItem: (state, action) => {
            state.items = state.items.filter((_, index) => index !== action.payload)
        },
        updateItemQuantity: (state, action) => {
            const { index, quantity } = action.payload
            if (state.items[index]) {
                state.items[index].quantity = quantity
            }
        },
        clearOrder: (state) => {
            state.items = []
            state.currentOrder = null
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(createOrder.pending, (state) => {
                state.loading = true
                state.error = null
            })
            .addCase(createOrder.fulfilled, (state, action) => {
                state.loading = false
                state.currentOrder = action.payload
            })
            .addCase(createOrder.rejected, (state, action) => {
                state.loading = false
                state.error = action.payload
            })
    },
})

export const { setPipeLength, addItem, removeItem, updateItemQuantity, clearOrder } = orderSlice.actions
export default orderSlice.reducer
