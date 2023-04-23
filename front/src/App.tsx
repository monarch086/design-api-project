import React, {useEffect, useState} from 'react';
import Table, {Column} from './components/table';
import styled from "styled-components";
import axios from "axios";
import {Prediction, PredictionColumn} from "./models/prediction.model";

const updatePredictionsUrl = 'https://whyh2nljtb2reh5zunflfomxfi0rysdn.lambda-url.us-east-1.on.aws/';
const retrievePredictionsUrl = 'https://qweko3hollebocqljvjtryy46a0iczgb.lambda-url.us-east-1.on.aws/';

const Cell = styled.div`
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
`;


const strToLocalDate = (str: string): Date => {
    const utcDate = new Date(str);
    return new Date(utcDate.getTime() + (utcDate.getTimezoneOffset()));
}

const Info = styled.div`
    align-self: flex-start;
`;

const Container = styled.div`
    height: 70%;
    width: 70%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
`;

const Button = styled.div`
  cursor: pointer;
  outline: 0;
  color: white;
  background-color: #9147ff;
  display: inline-block;
  font-weight: 400;
  line-height: 1.5;
  text-align: center;
  padding: 6px 12px;
  font-size: 16px;
  border-radius: .25rem;
  
  :hover {
    background-color: #772ce8;
  }
`;

const DisabledButton = styled.div`
  outline: 0;
  color: white;
  background-color: #9147ff77;
  pointer-events: none;
  display: inline-block;
  font-weight: 400;
  line-height: 1.5;
  text-align: center;
  padding: 6px 12px;
  font-size: 16px;
  border-radius: .25rem;
`;

const transformPredictions = (predictions: Prediction): [Date, Date, PredictionColumn[]] => {
    const predictionsData = Object.keys(predictions.regions_forecast).map((key, id) => {
        const rawData = JSON.parse(predictions.regions_forecast[key]);
        const data = Object.keys(rawData).reduce((obj: PredictionColumn['data'], key) => {
            const date = strToLocalDate(`${key.replace(' ', 'T')}Z`);
            const newKey = `${date.getHours()}:00`;
            obj[newKey] = rawData[key];
            return obj;
        }, {});

        return {
            id,
            data,
            region: key,
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
    const timesColumns = Object.keys(predictions[0].data).map(key => {
        return {
            header: key,
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
        axios.get(retrievePredictionsUrl)
            .then(res => {
                console.log(res);
                const [modelTrainTime, predictionTime, data] = transformPredictions(res.data);
                setModelTrainTime(modelTrainTime);
                setPredictionTime(predictionTime);
                setPredictions(data);
                setColumns(getColumnsConfig(data));
            })
            .catch(() => setError(true))
            .finally(() => setLoading(false));

    }, []);

    const updatePredictions = () => {
        setLoading(true);
        axios.get(updatePredictionsUrl)
            .then(res => {
                if (res.status === 200) {
                    console.log("retrieving url");
                    return axios.get(retrievePredictionsUrl)
                } else {
                    throw new Error('Error');
                }
            })
            .then(res => {
                const [modelTrainTime, predictionTime, data] = transformPredictions(res.data);
                setModelTrainTime(modelTrainTime);
                setPredictionTime(predictionTime);
                setPredictions(data);
                setColumns(getColumnsConfig(data));
                setError(false);
                setLoading(false);
            })
            .catch(() => {
                setError(true);
                setLoading(false);
            });
    }

    return <Container>
        <Info>
            { loading
                ? <DisabledButton onClick={updatePredictions}>Refresh predictions</DisabledButton>
                : <Button onClick={updatePredictions}>Refresh predictions</Button> }
        </Info>
        <Info>
            <span>Model train time: </span>
            <span>{loading ? '-' : modelTrainTime?.toLocaleDateString()}</span>
        </Info>
        <Info>
            <span>Prediction time: </span>
            <span>{loading ? '-' : predictionTime?.toLocaleString()}</span>
        </Info>
        <Table columns={columns}
               data={predictions}
               loading={loading}
               error={error}></Table>
    </Container>
}

export default App;