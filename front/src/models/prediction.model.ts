
export interface Prediction {
    last_model_train_time: string;
    last_prediction_time: string;
    regions_forecast: {
        [key: string]: string;
    }
}

export interface PredictionColumn {
    id: number;
    region: string;
    data: {
        [key: string]: boolean
    };
}

