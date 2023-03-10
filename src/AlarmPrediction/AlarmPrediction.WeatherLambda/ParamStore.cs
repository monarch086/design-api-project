using Amazon.SimpleSystemsManagement.Model;
using Amazon.SimpleSystemsManagement;

namespace AlarmPrediction.WeatherLambda
{
    internal class ParamStore
    {
        private static string TOKEN_PARAM_NAME = "AlarmPrediction.WeatherLambda.Token";

        public static async Task<string> GetWeatherApiToken()
        {
            var client = new AmazonSimpleSystemsManagementClient();

            var request = new GetParameterRequest()
            {
                Name = TOKEN_PARAM_NAME
            };
            var result = await client.GetParameterAsync(request);

            return result.Parameter.Value;
        }
    }
}
