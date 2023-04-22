namespace telegram_bot_lambda.Model;

internal class CommandEvent
{
    public int update_id { get; set; }

    public Message? message { get; set; }
}
