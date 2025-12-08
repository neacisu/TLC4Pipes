import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { pipeService } from '../../services/pipeService'

export const fetchPipes = createAsyncThunk(
    'pipe/fetchAll',
    async (filters = {}, { rejectWithValue }) => {
        try {
            const response = await pipeService.getAll(filters)
            return response.data
        } catch (error) {
            return rejectWithValue(error.response?.data || 'Failed to fetch pipes')
        }
    }
)

const initialState = {
    pipes: [],
    loading: false,
    error: null,
}

const pipeSlice = createSlice({
    name: 'pipe',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchPipes.pending, (state) => {
                state.loading = true
            })
            .addCase(fetchPipes.fulfilled, (state, action) => {
                state.loading = false
                state.pipes = action.payload
            })
            .addCase(fetchPipes.rejected, (state, action) => {
                state.loading = false
                state.error = action.payload
            })
    },
})

export default pipeSlice.reducer
