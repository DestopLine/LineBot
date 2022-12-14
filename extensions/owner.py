import asyncio
from cProfile import label
from math import floor
from re import DOTALL, findall, fullmatch
from timeit import default_timer as timer

import discord
from discord import app_commands
from discord.ext import commands

import core


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	# die
	@app_commands.command()
	@core.owner_only()
	async def die(self, interaction):
		await interaction.response.send_message(u'\U0001f480', ephemeral=True)
		print('\nBot apagado')
		try:
			await self.bot.close()
		except RuntimeError:
			pass


	# getmsg
	@app_commands.command()
	@core.owner_only()
	async def getmsg(self, interaction, id:str):
		msg = await interaction.channel.fetch_message(id)
		await interaction.response.send_message(f'```py\n{msg}\n```', ephemeral=True)


	# eval
	@app_commands.command()
	@core.owner_only()
	async def eval(self, interaction, ephemeral:bool=False, silent:bool=False):
		class CodeModal(discord.ui.Modal, title='Eval'):
			answer = discord.ui.TextInput(label='Código', style=discord.TextStyle.paragraph)

			def __init__(self, bot):
				super().__init__()
				self.bot = bot

			async def on_submit(self, interaction:discord.Interaction):
				await interaction.response.defer(ephemeral=ephemeral or silent, thinking=True)
				code = self.answer.value
				if not silent:
					return_line = findall(r'[^ ].+$', code.splitlines()[-1])[0]
					code = code[:-(len(return_line))] + f'core.eval_returned_value = {return_line}'

				code = '''@self.bot.tree.command()\n@core.owner_only()\nasync def evalcmd(interaction):\n    '''+code.replace('\n','\n    ')
				try:
					exec(code)
					start = timer()
					try:
						await self.bot.tree.get_command('evalcmd').callback(interaction)
					except Exception as e:
						core.eval_returned_value = e
					end = timer()
					if not silent:
						types = ''
						returned_value = core.eval_returned_value
						while True:
							try:
								types += str(type(returned_value))
								if not isinstance(returned_value, str):
									iter(returned_value)
								else:
									raise TypeError
							except TypeError:
								break
							else:
								try:
									if len(returned_value) == 0:
										break
									returned_value = returned_value[0]
								except (TypeError, KeyError):
									returned_value = tuple(returned_value)[0]

						await interaction.followup.send(embed=discord.Embed(
							title='Resultados del eval',
							description=f'Tipo de dato y resultado:\n```py\n{types}\n```\n```py\n{returned_value}\n```',
							colour=core.default_color(interaction)
						).set_footer(text=f'Ejecutado en {floor((end - start) * 1000)}ms'))
						core.returned_value = None
					else:
						await interaction.followup.send(u'\U00002705')
				finally:
					try:
						self.bot.tree.remove_command('evalcmd')
					except TypeError:
						pass

		await interaction.response.send_modal(CodeModal(self.bot))


	# reload
	@app_commands.command()
	@core.owner_only()
	async def reload(self, interaction, extension:str, sync:bool=False):
		await interaction.response.defer(ephemeral=True, thinking=True)
		await self.bot.reload_extension('extensions.' + extension)
		core.config_commands(self.bot)
		core.logger.info(f'"{extension}" extension reloaded')
		if sync:
			await core.sync_tree(self.bot)
		await interaction.followup.send(u'\U00002705')


	# unload
	@app_commands.command()
	@core.owner_only()
	async def unload(self, interaction, extension:str, sync:bool=False):
		await interaction.response.defer(ephemeral=True, thinking=True)
		await self.bot.unload_extension('extensions.' + extension)
		core.config_commands(self.bot)
		core.logger.info(f'"{extension}" extension unloaded')
		if sync:
			await core.sync_tree(self.bot)
		await interaction.followup.send(u'\U00002705')


	# load
	@app_commands.command()
	@core.owner_only()
	async def load(self, interaction, extension:str, sync:bool=False):
		await interaction.response.defer(ephemeral=True, thinking=True)
		await self.bot.load_extension('extensions.' + extension)
		core.config_commands(self.bot)
		core.logger.info(f'"{extension}" extension unloaded')
		if sync:
			await core.sync_tree(self.bot)
		await interaction.followup.send(u'\U00002705')


	# blacklist
	@app_commands.command()
	@core.owner_only()
	async def blacklist(self, interaction, user:discord.User):
		if core.check_blacklist(interaction, user, False):
			core.cursor.execute(f"INSERT INTO BLACKLIST VALUES({user.id})")
			await interaction.response.send_message(u'\U00002935', ephemeral=True)
		
		else:
			core.cursor.execute(f"DELETE FROM BLACKLIST WHERE USER={user.id}")
			await interaction.response.send_message(u'\U00002934', ephemeral=True)

		core.conn.commit()


async def setup(bot):
	await bot.add_cog(Owner(bot), guilds=core.bot_guilds)
