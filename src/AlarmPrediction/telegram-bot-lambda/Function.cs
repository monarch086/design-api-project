using AlarmPrediction.WeatherLambda;
using Amazon.Lambda.Core;
using System.Text.Json;
using System.Text.Json.Nodes;
using telegram_bot_lambda.Model;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace telegram_bot_lambda;

public class Function
{
    private HttpClient client = new HttpClient();
    private const int MESSAGE_MAX_LENGTH = 4096;

    /// <summary>
    /// Telegram bot for alarm predicting system
    /// </summary>
    public async Task FunctionHandler(JsonObject input, ILambdaContext context)
    {
        try
        {
            var requestBody = input["body"];
            if (requestBody == null) { return; }

            context.Logger.LogLine(requestBody.ToString());

            var commandEvent = JsonSerializer.Deserialize<CommandEvent>(requestBody.ToString());
            var region = commandEvent?.message?.text;
            var chatId = commandEvent?.message?.chat?.id ?? 0;

            context.Logger.LogLine($"Region: {region}");

            var predictionHost = await ParamStore.GetAlarmPredictionHost();
            var predictionUrl = $"{predictionHost}/?region={region}";

            HttpResponseMessage response = await client.GetAsync(predictionUrl);

            var token = await ParamStore.GetTelegramToken();
            var bot = new ChatBot(token);

            var prediction = (await response.Content.ReadAsStringAsync()).Truncate(MESSAGE_MAX_LENGTH);

            if (!response.IsSuccessStatusCode || string.IsNullOrEmpty(prediction))
            {
                var message = "Введений регіон/локація не знайдені";
                await bot.Post(message, chatId);

                return;
            }

            context.Logger.LogInformation($"Requesting prediction for {region}: {prediction}.");

            await bot.Post(prediction, chatId);
        }
        catch (Exception ex)
        {
            context.Logger.LogError(ex.ToString());
        }
    }
}
