import discord


async def get_info(ctx, member):
    if member is None:
        user = ctx.message.author
        em = discord.Embed(title="Информация о пользователе", color=user.color)
        em.add_field(name="Имя:", value=user.display_name, inline=False)

        em.add_field(name="Айди пользователя:", value=ctx.message.author.id, inline=False)
        em.add_field(name="Статус:", value=user.activity, inline=False)
        em.add_field(name="Роль на сервере:", value=f"{user.top_role.mention}", inline=False)
        em.add_field(name="Акаунт был создан:",
                     value=user.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        em.set_thumbnail(url=user.avatar_url)
        return em
