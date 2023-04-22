import {configureStore} from "@reduxjs/toolkit";
import studentsReducer, {StudentsState} from './studentsState'

export interface RootState {
    students: StudentsState,
}

const logger = (store: { getState: () => any; }) => (next: (arg0: any) => any) => (action: { type: any; }) => {
    console.group(action.type)
    console.info('dispatching', action)
    let result = next(action)
    console.log('next state', store.getState())
    console.groupEnd()
    return result
}

const store = configureStore({
    reducer: {
        students: studentsReducer,
    },
    // middleware: [logger],
});

export default store;