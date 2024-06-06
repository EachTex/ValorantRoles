import os, traceback, discord
from discord.ext import commands

with open(f"./token.txt", "r") as f:
    token = f.read()
    f.close()

class MyBot(commands.Bot):

    def __init__(self, command_prefix, **kwargs):
        super().__init__(command_prefix, **kwargs)

        try:
            self.load_extension(f"cogs.valorantroles")
        except Exception:
            traceback.print_exc()

    async def on_ready(self):
        os.system('clear')
        print(f">>> {self.user}にログインしました！")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance ( error , commands.CommandNotFound ):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            return

if __name__ == '__main__':
    bot = MyBot(command_prefix=None, intents = discord.Intents.all())
    bot.run(token)