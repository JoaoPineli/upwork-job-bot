from discord.ext import tasks
import discord
import get_contracts
import datetime

def filter_new_entries(current_entries, new_entries):
    current_ids = [entry.id for entry in current_entries]
    return [entry for entry in new_entries if entry.id not in current_ids]


class Client(discord.Client):
    async def on_ready(self):
        self.curr_contracts = []
        print(f'Logged on as {self.user}!')

    async def setup_hook(self):
        self.get_new_contracts.start()

    @tasks.loop(seconds=60)
    async def get_new_contracts(self):
        print('Checking for new contracts...', datetime.datetime.now().strftime("%H:%M"))
        contracts = get_contracts.main()
        new_contracts = filter_new_entries(self.curr_contracts, contracts)
        if len(new_contracts) > 0:
            await self.get_channel(1121466160454574141).send(new_contracts[0])
        else:
            print ('No new contracts found')
        self.curr_contracts = contracts

    @get_new_contracts.before_loop
    async def wait_login(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run('MTEyMTQ1NjI4MjI3NzI2OTUzNA.G87McX.vmA4ZMCjEwOos7xFTzIY5eqat9KvZfr-P0Wlbo')
