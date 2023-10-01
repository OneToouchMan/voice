import disnake
from disnake.ext import commands
import sqlite3
import asyncio

class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('private_channels.db')
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS private_channels 
                                  (server_id INT, channel_id INT, owner_id INT)''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    @commands.command()
    async def setvoice(self, ctx):
        category = await ctx.guild.create_category('Приватные каналы')
        channel = await category.create_voice_channel('+ создать')
        await ctx.send('Голосовой канал создан!')

    async def check_empty_voice_channels(self):
        for row in self.cursor.execute('SELECT channel_id FROM private_channels'):
            channel_id = row[0]
            channel = self.bot.get_channel(channel_id)
            if channel and len(channel.members) == 0:
                self.cursor.execute('DELETE FROM private_channels WHERE channel_id = ?', (channel_id,))
                self.conn.commit()
                await channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if after.channel and after.channel.name == '+ создать':
                category = after.channel.category
                new_channel = await category.create_voice_channel(f'Приватный канал {member.display_name}')
                await member.move_to(new_channel)
                self.cursor.execute('INSERT INTO private_channels (server_id, channel_id, owner_id) VALUES (?, ?, ?)',
                                    (member.guild.id, new_channel.id, member.id))
                self.conn.commit()

        await self.check_empty_voice_channels()


def setup(bot):
    bot.add_cog(voice(bot))
