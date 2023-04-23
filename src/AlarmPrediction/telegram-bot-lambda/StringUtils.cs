using Newtonsoft.Json;
using System.Text;
using telegram_bot_lambda.Model;

namespace telegram_bot_lambda;
internal static class StringUtils
{
    public static string Truncate(this string value, int maxLength)
    {
        if (string.IsNullOrEmpty(value)) return value;
        return value.Length <= maxLength ? value : value.Substring(0, maxLength);
    }

    public static Prediction Deserialize(this string jsonString)
    {
        var modelData = JsonConvert.DeserializeObject<Prediction>(jsonString);

        modelData.RegionsForecast = new Dictionary<string, Dictionary<DateTime, bool>>();

        foreach (var region in modelData.RegionsForecastJson)
        {
            modelData.RegionsForecast[region.Key] = JsonConvert.DeserializeObject<Dictionary<DateTime, bool>>(region.Value);
        }

        return modelData;
    }

    public static string ToMessage(this string jsonString)
    {
        var sb = new StringBuilder("Прогноз тривог\n");

        var prediction = jsonString.Deserialize();

        sb.AppendLine($"Час тренування моделі: {prediction.LastModelTrainTime.ToKyivTime()}");
        sb.AppendLine($"Час визначення прогнозу: {prediction.LastPredictionTime.ToKyivTime().ToShortTimeString()}");

        foreach (var region in prediction.RegionsForecast.Keys)
        {
            sb.AppendLine($"{region}:");

            foreach (var hour in prediction.RegionsForecast[region].Keys)
            {
                sb.AppendLine($"{hour.ToKyivTime().ToShortTimeString()}: {prediction.RegionsForecast[region][hour]}");
            }
        }

        return sb.ToString();
    }

    public static DateTime ToKyivTime(this DateTime time)
    {
        var kyivTimeShiftHours = 3;

        return time.AddHours(kyivTimeShiftHours);
    }
}

