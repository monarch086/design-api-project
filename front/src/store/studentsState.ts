import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import {Student} from "../models/student.model";

export type StudentsState = {
    students: Student[],
    initialLoading: 'loading' | 'error' | 'loaded',
    additionalLoading: 'loading' | 'error' | 'loaded',
};

const initialState: StudentsState = {
    students: [],
    initialLoading: 'loading',
    additionalLoading: 'loaded'
};

// immer.js under the hood
export const studentsSlice = createSlice({
    name: 'students',
    initialState,
    reducers: {
        setLoading: (state, { payload }: PayloadAction<{ additional: boolean }>) => {
          state[payload.additional ? 'additionalLoading' : 'initialLoading'] = 'loading';
        },
        setError: (state, { payload }: PayloadAction<{ additional: boolean }>) => {
            state[payload.additional ? 'additionalLoading' : 'initialLoading'] = 'error';
        },
        dataLoaded: (state, { payload }: PayloadAction<{ additional: boolean, students: Student[] }>) => {
            state[payload.additional ? 'additionalLoading' : 'initialLoading'] = 'loaded';
            if (payload.additional) {
                state.students.push(...payload.students);
            } else {
                state.students = payload.students;
            }
        },
    },
});

export const { setLoading, setError, dataLoaded } = studentsSlice.actions;

export default studentsSlice.reducer;
