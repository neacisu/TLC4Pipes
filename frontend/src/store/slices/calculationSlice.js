import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { calculationService } from '../../services/calculationService'

export const calculateLoading = createAsyncThunk(
    'calculation/optimize',
    async (request, { rejectWithValue }) => {
        try {
            const response = await calculationService.optimize(request)
            return response.data
        } catch (error) {
            return rejectWithValue(error.response?.data || 'Calculation failed')
        }
    }
)

const initialState = {
    result: null,
    loading: false,
    error: null,
}

const calculationSlice = createSlice({
    name: 'calculation',
    initialState,
    reducers: {
        clearResult: (state) => {
            state.result = null
            state.error = null
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(calculateLoading.pending, (state) => {
                state.loading = true
                state.error = null
            })
            .addCase(calculateLoading.fulfilled, (state, action) => {
                state.loading = false
                state.result = action.payload
            })
            .addCase(calculateLoading.rejected, (state, action) => {
                state.loading = false
                state.error = action.payload
            })
    },
})

export const { clearResult } = calculationSlice.actions
export default calculationSlice.reducer
