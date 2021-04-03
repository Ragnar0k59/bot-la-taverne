import re
from datetime import datetime

from Business.Models.models import Event, User_event
from Business.Utils.utils import *


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f'Boire l\'apéro avec {BOT_PREFIX}help'))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def addRole(ctx, *, role: discord.Role):
    session = Session()
    if is_admin(ctx.author):
        role = AuthorizedRole(id=role.id, name=role.name)
        if session.query(AuthorizedRole).get(role.id) is None:
            role = AuthorizedRole(id=role.id, name=role.name)
            session.add(role)
            session.commit()
            session.flush()
            await ctx.channel.send('Role <@&' + str(session.query(AuthorizedRole.id)[0].id) + '> registered!')
        else:
            await ctx.channel.send('Role <@&'
                                   + str(session.query(AuthorizedRole).get(role.id).id) +
                                   '> has already been registered!')
    else:
        await ctx.channel.send('You don\'t have permission to use this command')
    session.close()


@bot.command()
async def createEvent(ctx, game, count, hour, date):
    session = Session()
    if is_animator(ctx.author, session):
        date = date.split('/')
        hour = hour.split('h')
        date_end = datetime(int(date[2]), int(date[1]), int(date[0]), int(hour[0]), int(hour[1]))
        event = Event(date_closure=date_end, max_user=count, type=game)
        event.users.append(await user_exist(ctx.author.id, session))
        session.add(event)
        session.commit()
        session.flush()
        await ctx.message.delete()
        id_message = await ctx.channel.send(embed=await create_embed_inscr(event, 0x16b826))
        event.id_message = id_message.id
        session.add(event)
        session.commit()
        session.flush()
    else:
        await ctx.channel.send('You don\'t have permission to use this command')
    session.close()


@bot.command()
async def closeEventRegister(ctx, event_id):
    session = Session()
    if is_animator(ctx.author, session):
        event = session.query(Event).get(event_id)
        event.open = False
        msg = await ctx.channel.fetch_message(event.id_message)
        await msg.edit(embed=await create_embed_inscr(event, 0xec2013))
        await ctx.message.delete()
        session.add(event)
        session.commit()
        session.flush()
    else:
        await ctx.channel.send('You don\'t have permission to use this command')
    session.close()


@bot.command()
async def register(ctx, event_id):
    session = Session()
    event = session.query(Event).get(event_id)
    if event.open and len(event.users) - 1 < event.max_user:
        if len([x for x in event.users if x.id == str(ctx.author.id)]) > 0:
            await (await ctx.channel.send('Tu es déjà inscrit.e à cet événement')).delete(delay=30)
            await ctx.message.delete(delay=30)
            session.close()
            return
        event.users.append(await user_exist(ctx.author.id, session))
        session.add(event)
        session.commit()
        session.flush()
        msg = await ctx.channel.fetch_message(event.id_message)
        if len(event.users) - 1 < event.max_user:
            color = 0x16b826
        else:
            color = 0xf57c17
        await msg.edit(embed=await create_embed_inscr(event, color))
        await ctx.message.delete()
    else:
        await ctx.channel.send('Pour cet événement soit la liste est pleine, soit les inscriptions sont terminées')
    session.close()


@bot.command()
async def unregister(ctx, event_id):
    session = Session()
    event = session.query(Event).get(event_id)
    event.users.remove([x for x in event.users if x.id == str(ctx.author.id)][0])
    session.add(event)
    session.commit()
    session.flush()
    if len(event.users) - 1 < event.max_user:
        color = 0x16b826
    else:
        color = 0xf57c17
    msg = await ctx.channel.fetch_message(event.id_message)
    await msg.edit(embed=await create_embed_inscr(event, color))
    await ctx.message.delete()
    session.close()


@bot.command()
async def createAmongUs(ctx):
    session = Session()
    print(await user_exist("176336919431479296", session))


@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Voici la liste des commandes disponibles',
                          description=open('conf/help', 'r', encoding='utf8').read() + '\r\u200b',
                          color=0xAD33E9
                          )

    embed.add_field(name='**__Préfixe du bot__**', value=f'• `{BOT_PREFIX}`', inline=False)
    embed.set_author(name='Le Tavernier', url='https://mrdoob.com/projects/chromeexperiments/google-gravity/',
                     icon_url='https://cdn.discordapp.com/avatars/780489320582610994/1b1613457d8bde8de158baf95ad42ecd'
                              '.png?size=4096')

    embed.set_footer(text=f'À la prochaine {ctx.author.display_name} pour boire un verre avec moi 🍻')
    await ctx.channel.send(embed=embed)
    await ctx.message.delete()


def hasWord(string, word):
    return len(re.findall(word, string, re.IGNORECASE)) != 0


bot.run(DISCORD_TOKEN)
