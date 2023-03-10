using Amazon.Lambda.Core;
using System.Text.Json;
using System.Text.Json.Nodes;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace AlarmPrediction.WeatherLambda;

public class Function
{
    private const string WEATHER_HOST = "https://weather.visualcrossing.com";
    private HttpClient client = new HttpClient();

    /// <summary>
    /// A function that gets weather for a certain date
    /// </summary>
    public async Task<string> FunctionHandler(JsonObject input, ILambdaContext context)
    {
        try
        {
            var queryParams = input["queryStringParameters"];

            var inputData = queryParams == null ?
                new InputModel() :
                JsonSerializer.Deserialize<InputModel>(queryParams.ToString());

            var date = string.IsNullOrEmpty(inputData.Date) ? "next24hours" : inputData.Date;

            var apiKey = await ParamStore.GetWeatherApiToken();

            var weatherUrl = $"{WEATHER_HOST}/VisualCrossingWebServices/rest/services/timeline/{inputData.Location}/{date}?unitGroup=metric&key={apiKey}";

            HttpResponseMessage response = await client.GetAsync(weatherUrl);

            context.Logger.LogInformation($"Requesting weather for {inputData.Location}: {response.StatusCode}.");

            string responseText = await response.Content.ReadAsStringAsync();

            context.Logger.LogInformation(responseText);

            return responseText;
        }
        catch (Exception ex)
        {
            context.Logger.LogError(ex.ToString());

            return ex.Message;
        }

    }
}
