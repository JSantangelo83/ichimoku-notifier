#!/usr/bin/python3
import discord
from discord.ext import commands
from discord import ActionRow, Button, ButtonStyle
from helperdb import HelperDB
import time


client = commands.Bot(command_prefix=commands.when_mentioned_or('$'), intents=discord.Intents.all(), case_insensitive=True)


async def botimoku():
    await client.wait_until_ready()

    interval = HelperDB.instance.fromIntervalToSeconds(HelperDB.instance.getInterval())    
    print(f"INTERVAL = {interval}")
    time_cero = time.time()
    time_end = time_cero + interval
    while True:
        time_cero = time.time()
        if(time_cero >= time_end):
            print("pasaron 10 seg")
            time_end = time_cero + interval
    ctx = client.get_channel(HelperDB.instance.getChannel()) # replace with channel ID that you want to send to
    await send_trade(ctx, "BTCUSDT", ".\\tmp\\a.png", "52.0000", "56.000", "SHORT", 0, "512")
    

@client.event
async def on_guild_join(guild):
    ch = discord.utils.get(guild.channels, name="botimoku_time")
    if(not ch):
        ch = await guild.create_text_channel('botimoku_time')
    HelperDB.instance.setChannel(ch)

async def send_trade(ctx, symbol, image_path, takeprofit, stoploss, direccionalidad, status, trade_id, max_duaration=(5*60)):
    users = []
    c = discord.Color.from_rgb(229, 26, 76) if not status else discord.Color.from_rgb(127, 255, 0)   
    file = discord.File(fp=image_path, filename="image.png") 

    embed = discord.Embed(title=f"Ichimoku se cumplio en: {symbol}", description=f"🌈🌈 **Deseas realizar un TRADE!!!!** 🌈🌈 :  {direccionalidad}\n**Stoploss**: {stoploss}\n**Takeprofit**: {takeprofit}", color=c)
    embed.set_image(url="attachment://image.png")



    ok_button = Button(label='Entrar al Trade!', custom_id=f'ok:{trade_id}', style=ButtonStyle.Primary); 
    not_ok_button = Button(label='Salir del Trade', custom_id=f'not_ok:{trade_id}', style=ButtonStyle.Danger);
    msg = await ctx.send(embed=embed, components=[ActionRow(ok_button, not_ok_button)], file=file)

    def _check(i: discord.Interaction, b):
        return i.message == msg 
    end_time = time.time() + max_duaration 
    exitw = True
    while(exitw):
        inter, but = await client.wait_for('button_click', check=_check)
        button = but.custom_id.split(":")
        trade_id = button[1]
        which_button = button[0]
        await inter.defer()
        if(time.time() > end_time):
           exitw = False 
        if(inter.user_id in users and which_button == "ok"):
            continue
        if(which_button == "ok"):
            if(not len(users)):
                embed.description += "\nUsuarios: "
            users.append(inter.user_id)
            embed.description += f"<@{inter.user_id}>, "
            await inter.edit(embed=embed)
        elif(which_button == "not_ok"):
            await ctx.send(embed=discord.Embed(title=f":c"))

"""
entra al sv


discord
fijarse si existe botimoku_time
    si no lo crea, el canal
consigue el canal

logica trade
loop magico








"""

client.loop.create_task(botimoku())
client.run('OTEwNzUwODQ3NjE5NzA2OTEw.YZXY0w.IVbPVIhzs13habcOTFMjmsWfyG4')
