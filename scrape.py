import requests
from bs4 import BeautifulSoup
import pandas as pd

import discord
from discord.ext import commands
from secret import DISCORD_TOKEN
from secret import MESSAGE_CHANNEL_ID
from secret import LEADERBOARD_CHANNEL_ID
bot = commands.Bot(command_prefix='/')

@bot.command()
async def qual(ctx):
    data = pd.read_csv('data.csv',index_col=0,encoding='utf-8',dtype=object)
    songs = data.columns[1:]

    scraping_range = 10

    def local(data,name,song):
        num_data = data.iloc[1:,1:].astype('float64')
        data_s = num_data.sort_values(song,ascending=False)
        return data_s.index.get_loc(name)+1

    for name,url in zip(data.index.values[1:],data.ScoreSaberID[1:]):
        print("scraping {} #debug".format(name))
        for p in range(1,scraping_range+1):
            target = '{}&page={}&sort=2'.format(url,p)
            r = requests.get(target)
            t = r.text
            s = BeautifulSoup(t,'html.parser')
            names = s.select('.songTop.pp')
            accs = s.select('.scoreBottom')
            for n,a in zip(names,accs):
                if n.text in songs:
                    notes = data.at['notes',n.text]
                    score = int(a.text[7:-3].replace(',',''))
                    acc = score/(115*8*int(notes)-7245)*100
                    acc = int(acc*100)
                    acc = float(acc)/100
                    if acc > float(data.at[name, n.text]):
                        data.at[name,n.text] = acc
                        local_rank = local(data,name,n.text)
                        channel = bot.get_channel(MESSAGE_CHANNEL_ID)
                        text = "{}さんが {} を更新！ acc ... {} (譜面内順位 **#{}**)".format(name,n.text,acc,local_rank)
                        await channel.send(text) #honban
                        # await ctx.send(text) #debug

    num_data = data.iloc[1:,1:].astype('float64')
    total = num_data.sum(axis=1)
    total_s = total.sort_values(ascending=False)
    text = ':crown:現在の総合ランキング:lizard:\n'
    count = 0
    for t in total_s.index.values:
        count += 1
        score = total_s[t]
        score = int(score*100)
        score = float(score)/100
        if "棄権" in t:
            count -= 1
            text += '-- {} ... {}pt\n'.format(t,score)
        else:
            text += '#{} **{}** ... {}pt\n'.format(count,t,score)
            if count==8:
                text += '🧱🧱🧱🧱🧱🧱 本選進出の壁 🧱🧱🧱🧱🧱🧱\n'

    for song in songs:
        text += '\n**{}**  の譜面内ランキング\n'.format(song)
        data_s = num_data.sort_values(song,ascending=False)
        print(data_s)
        for i,v in enumerate(data_s.index.values):
            if i >= 5:
                break
            score = data_s.at[v,song]
            score = int(score*100)
            score = float(score)/100
            text += '#{} {} ... {}%\n'.format(i+1,v,score)

    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    lid = channel.last_message_id
    last_message = await channel.fetch_message(lid)
    await last_message.edit(content=text) #honban
    # await ctx.send(text) #debug

    data.to_csv('data.csv')
    print("done")
    
print("bot running...")
bot.run(DISCORD_TOKEN)
