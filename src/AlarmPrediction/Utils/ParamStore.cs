using Amazon.SimpleSystemsManagement.Model;
using Amazon.SimpleSystemsManagement;

namespace AlarmPrediction.WeatherLambda
{
    public static class ParamStore
    {
        private static string WEATHER_TOKEN_PARAM_NAME = "AlarmPrediction.WeatherLambda.Token";
        private static string TELEGRAM_TOKEN_PARAM_NAME = "TelegramBot.Token";

        public static async Task<string> GetWeatherApiToken() =>
            await GetParamValue(WEATHER_TOKEN_PARAM_NAME);

        public static async Task<string> GetTelegramToken() =>
            await GetParamValue(TELEGRAM_TOKEN_PARAM_NAME);

        private static async Task<string> GetParamValue(string paramName)
        {
            var client = new AmazonSimpleSystemsManagementClient();

            var request = new GetParameterRequest()
            {
                Name = paramName
            };
            var result = await client.GetParameterAsync(request);

            return result.Parameter.Value;
        }
    }
}
