import sqlite3
import time
con = sqlite3.connect('database.db', check_same_thread=False)
cursor = con.cursor()

async def UpdatePlayerScore(message, time):
    tt = cursor.execute(f"SELECT last_time FROM members WHERE guild = {message.guild.name} ")
    last_poster = cursor.execute(f"SELECT last_poster FROM members WHERE guild = {message.guild.name} ")
    last_poster_pp = cursor.execute(f"SELECT point_a FROM members WHERE guild = {message.guild.name} ")
    point = time.time() - tt
    point = point+ last_poster

    cursor.execute(f"UPDATE members SET point_a = {point} WHERE guild = {message.guild.name} AND last_poster = {last_poster} ")
    cursor.execute(f"UPDATE members SET last_poster = {message.author} ")