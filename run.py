import asyncio
from icecream import install
# Set up icecream
install()
from traceback import format_exc

import discord
from discord import app_commands
from discord.ext import commands

import core


# Create the bot client
class LineBot(commands.Bot):
	async def setup_hook(self):
		# Load the extensions which contain commands and utilities
		for extension in (
			'listeners',
			'bot',
			'modtxt',
			# 'util',
			'fun',
			'owner',
			# 'image'
		):
			await bot.load_extension('extensions.' + extension)

		# Add descriptions to the commands from the core.descs dict and syncs the commands
		core.config_commands(self)
		for guild in core.bot_guilds:
			await self.tree.sync(guild=guild)

# Set the intents
intents = discord.Intents.all()
intents.bans = False
intents.integrations = False
intents.webhooks = False
intents.invites = False
intents.voice_states = False
intents.message_content = False

bot = LineBot(command_prefix='l!', help_command=None, owner_id=core.owner_id, case_insensitive=True, intents=intents)

@bot.tree.context_menu(name='Tic Tac Toe', guilds=core.bot_guilds)
@app_commands.checks.cooldown(1, 15)
async def tictactoe_context(interaction: discord.Interaction, user: discord.Member):
	if not user.bot:
		ask_view = core.Confirm(interaction, user)
		ask_string = f'{user.mention} ¿Quieres unirte a la partida de Tic Tac Toe de **{interaction.user.name}**?' if user.id != interaction.user.id else f'¿Estás tratando de jugar contra ti mismo?'
		await interaction.response.send_message(ask_string, view=ask_view)
		await ask_view.wait()
		
		if ask_view.value == None:
				await interaction.edit_original_response(view=ask_view)
				return
			
		elif not ask_view.value:
			await ask_view.last_interaction.response.edit_message(content=core.Warning.cancel('La partida fue rechazada'), view=ask_view)
			return

		else:
			await ask_view.last_interaction.response.defer()

	game = core.TicTacToe(interaction, interaction.user, user)
	if interaction.response.is_done():
		await interaction.edit_original_response(content=game.get_content(), view=game)
	else:
		await interaction.response.send_message(content=game.get_content(), view=game)

async def main():
	# Create the event that catches any unknown errors and logs them
	@bot.event
	async def on_error(event, *args, **kwargs):
		ctx = args[0]
		log = f'Ha ocurrido un error: "{ctx.message.content}" {repr(ctx.message)}'
		core.logger.error(f'{log}\n{format_exc()}')
		await bot.get_channel(core.error_logging_channel).send(f'<@{bot.owner_id}>', delete_after=30)


	# @bot.event
	# async def on_guild_join(guild):
	#     botdata.logger.info(f'El bot ha entrado a un servidor: {repr(guild)}')


	# Start the bot
	async with bot:
		core.cursor.execute(f"SELECT VALUE FROM RESOURCES WHERE KEY='{core.bot_mode}_token'")
		token = core.cursor.fetchall()[0][0]
		core.conn.commit()
		await bot.start(token)
		del token

asyncio.run(main())