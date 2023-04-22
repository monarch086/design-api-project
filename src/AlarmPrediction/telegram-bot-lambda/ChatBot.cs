using Telegram.Bot;

namespace telegram_bot_lambda;

internal class ChatBot
{
    private TelegramBotClient client;

    public ChatBot(string token)
    {
        client = new TelegramBotClient(token);
    }

    public async Task Post(string message, int chatId)
    {
        var t = await client.SendTextMessageAsync(chatId, message, Telegram.Bot.Types.Enums.ParseMode.Html);
    }
}
