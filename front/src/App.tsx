import React, {useEffect, useState} from 'react';
import Table, {Column} from './components/table';
import styled from "styled-components";
import axios from "axios";
import {Prediction, PredictionColumn} from "./models/prediction.model";

const retrievePredictions = 'https://qweko3hollebocqljvjtryy46a0iczgb.lambda-url.us-east-1.on.aws/';

const Cell = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const strToLocalDate = (str: string): Date => {
    const utcDate = new Date(str);
    return new Date(utcDate.getTime() + (utcDate.getTimezoneOffset()));
}

const Container = styled.div`
    height: 70%;
    width: 70%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
`;

const transformPredictions = (predictions: Prediction): [Date, Date, PredictionColumn[]] => {
    const predictionsData = Object.keys(predictions.regions_forecast).map((key, id) => {
        return {
            id,
            region: key,
            data: JSON.parse(predictions.regions_forecast[key]),
        }
    });
    console.log(predictionsData);
    const lastModelTrainTime = strToLocalDate(predictions.last_model_train_time);
    const lastPredictionTime = strToLocalDate(`${predictions.last_prediction_time.replace(' ', 'T')}Z`);
    return [lastModelTrainTime, lastPredictionTime, predictionsData];
}

const getColumnsConfig = (predictions: PredictionColumn[]): Column<PredictionColumn>[] => {
    if (!predictions?.length) {
        return [{
            header: 'Region',
            styleClass: 'region-cell',
            key: 'region',
        }];
    }
    console.log(predictions[0].data);
    const timesColumns = Object.keys(predictions[0].data).map(key => {
        console.log(key);
        const date = strToLocalDate(`${key.replace(' ', 'T')}Z`);
        return {
            header: `${date.getHours()}:00`,
            styleClass: 'predictions-cell',
            body: (row: PredictionColumn) => {
                return <Cell className={row.data[key] ? 'red' : 'green'}>{row.data[key] ? '+' : '-'}</Cell>
            }
        }
    });
    return [{
        header: 'Region',
        styleClass: 'region-cell',
        key: 'region',
    },
        ...timesColumns];
}

function App() {
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(false);
    const [modelTrainTime, setModelTrainTime] = useState<Date>();
    const [predictionTime, setPredictionTime] = useState<Date>();
    const [predictions, setPredictions] = useState<PredictionColumn[]>([]);
    const [columns, setColumns] = useState<Column<PredictionColumn>[]>(getColumnsConfig([]));

    useEffect(() => {
        setLoading(true);
        axios.get(retrievePredictions)
            .then(res => {
                const [modelTrainTime, predictionTime, data] = transformPredictions(res.data);
                setModelTrainTime(modelTrainTime);
                setPredictionTime(predictionTime);
                setPredictions(data);
                setColumns(getColumnsConfig(data));
            })
            .catch(res => setError(true))
            .finally(() => setLoading(false));

    }, []);

    return <Container>
        <div>
            <span>Model train time: </span>
            <span>{loading ? '-' : modelTrainTime?.toLocaleDateString()}</span>
        </div>
        <div>
            <span>Prediction time: </span>
            <span>{loading ? '-' : predictionTime?.toLocaleString()}</span>
        </div>
        <Table columns={columns}
               data={predictions}
               loading={loading}
               error={error}></Table>
    </Container>
}

export default App;
