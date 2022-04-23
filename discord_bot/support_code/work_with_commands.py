import discord
from discord import Embed


async def command_user(ctx, msg):
    em = discord.Embed(colour=ctx.message.author.color, title=f"Command by "
                                                              f"{ctx.message.author.display_name}  |  "
                                                              f"<{msg}>")
    await ctx.send(embed=em)


async def get_list_commands():
    em = Embed(title="Команды", colour=discord.Colour(0xFF69B4))
    em.add_field(name="!play", value="Добавляет песню в очередь")
    em.add_field(name="!stop", value="Отключает бота")
    em.add_field(name="!menu", value="Открывает меню управления песнями")
    em.add_field(name="!pl", value="Добавляет плейлист с нашего сайта")
    em.add_field(name="!yandex", value="Добавляет плейлист с YandexMusic")
    em.add_field(name="!now", value="Выводит играющий трек")
    em.add_field(name="!pause", value="Ставит музыку на паузу")
    em.add_field(name="!pl", value="Добавляет плейлист c cайта по названию в очередь")
    em.add_field(name="!queue", value="Выводит текущую очередь песен")
    em.add_field(name="!pop", value="Удаляет песню из очереди по номеру")
    em.add_field(name="!repeat", value="Зацикливает воспроизведение очереди")
    em.add_field(name="!skip", value="Пропускает текущую песню")
    em.add_field(name="!seek", value="Перематывает на ")
    em.add_field(name="!text", value="Выводит текст текущей песни")
    em.add_field(name="!shuffle", value="Перемешивает воспроизведение треков")
    em.add_field(name="!info", value="Информация о пользователе")
    em.add_field(name="!help", value="Выводит список всех команд бота")
    return em
