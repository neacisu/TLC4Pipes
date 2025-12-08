import { createSlice } from '@reduxjs/toolkit'

const initialState = {
    configs: [
        {
            id: 1,
            name: 'Standard 24t Romania',
            maxPayloadKg: 24000,
            internalLengthMm: 13600,
            internalWidthMm: 2480,
            internalHeightMm: 2700,
        },
        {
            id: 2,
            name: 'Mega Trailer Romania',
            maxPayloadKg: 24000,
            internalLengthMm: 13600,
            internalWidthMm: 2480,
            internalHeightMm: 3000,
        },
    ],
    selectedConfig: 1,
}

const truckSlice = createSlice({
    name: 'truck',
    initialState,
    reducers: {
        selectTruckConfig: (state, action) => {
            state.selectedConfig = action.payload
        },
    },
})

export const { selectTruckConfig } = truckSlice.actions
export default truckSlice.reducer
