using Newtonsoft.Json;

namespace telegram_bot_lambda.Model;

internal class Prediction
{
    [JsonProperty("last_model_train_time")]
    public DateTime LastModelTrainTime { get; set; }

    [JsonProperty("regions_forecast")]
    public Dictionary<string, string> RegionsForecastJson { get; set; }

    [JsonIgnore]
    public Dictionary<string, Dictionary<DateTime, bool>> RegionsForecast { get; set; }

    [JsonProperty("last_prediction_time")]
    public DateTime LastPredictionTime { get; set; }
}
