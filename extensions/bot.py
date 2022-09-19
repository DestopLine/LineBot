import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process, virtual_memory, cpu_percent

import core


class About(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		# self.send = bot.get_cog('GlobalCog').send


	# help
# 	@commands.cooldown(1, 1.5, commands.BucketType.user)
# 	@commands.command(name='help')
# 	async def _help(self, ctx, command=None):
# 		if command == None:
# 			emb = helpsys.get_all(ctx)
# 			await self.send(ctx, embed=emb)
# 		elif self.bot.get_command(command) in self.bot.commands:
# 			command = self.bot.get_command(command)
# 			emb = helpsys.get_cmd(ctx, command.name)
# 			await self.send(ctx, embed=emb)
# 		else:
# 			await self.send(ctx, core.Warning.error(f'El comando **{await commands.clean_content().convert(ctx, command)}** no existe'))
# 			ctx.command.reset_cooldown(ctx)


	# ping
	@app_commands.command(name='ping')
	async def _ping(self, interaction: discord.Interaction):
		content = core.Warning.info('El ping es de')[:-1]
		await interaction.response.send_message(content)
		response = await interaction.original_response()
		ping = (interaction.created_at - response.created_at).microseconds // 1000
		await response.edit(content=content + f' **{ping} ms**.')


# 	# uptime
# 	@commands.command()
# 	async def uptime(self, ctx):
# 		delta = core.fix_delta(datetime.utcnow() - core.bot_ready_at)
# 		await self.send(ctx, core.Warning.info(f'Online por **{delta}**'))


# 	# links
# 	@commands.command(aliases=('invite', 'vote'))
# 	async def links(self, ctx):
# 		emb = discord.Embed(title='Links', colour=core.default_color(ctx))
# 		for link in core.links:
# 			emb.add_field(name=link, value=f'[Aquí]({core.links[link]})')
# 		await self.send(ctx, embed=emb)


# 	#prefix
# 	@commands.cooldown(1, 5.0, commands.BucketType.guild)
# 	@commands.command(aliases=['lineprefix'])
# 	@commands.guild_only()
# 	async def prefix(self, ctx, prefix=None):
# 		if not ctx.channel.permissions_for(ctx.message.author).manage_guild:
# 			await self.send(ctx, core.Warning.error('Necesitas permiso de administrador para cambiar el prefijo del servidor'))
# 			ctx.command.reset_cooldown(ctx)

# 		else:
# 			if prefix == None:
# 				await self.send(ctx, embed=helpsys.get_cmd(ctx, 'prefix'))
# 				return

# 			elif len(prefix) > 16:
# 				await self.send(ctx, core.Warning.error('El límite de carácteres de un prefijo es 16'))
# 				ctx.command.reset_cooldown(ctx)
# 				return

# 			elif prefix == core.default_prefix:
# 				core.cursor.execute(f"DELETE FROM {core.prefix_table} WHERE ID={ctx.guild.id}")

# 			else:
# 				core.cursor.execute(f"SELECT PREFIX FROM {core.prefix_table} WHERE ID={ctx.guild.id}")
# 				check = core.cursor.fetchall()
# 				if check == []:
# 					core.cursor.execute(f"INSERT INTO {core.prefix_table} VALUES({ctx.guild.id},?)", (prefix,))
# 				else:
# 					core.cursor.execute(f"UPDATE {core.prefix_table} SET PREFIX=? WHERE ID={ctx.guild.id}", (prefix,))

# 			core.conn.commit()
# 			del self.bot.get_cog('GlobalCog').cached_prefixes[ctx.guild.id]
# 			await self.send(ctx, core.Warning.success(f'El prefijo ha sido actualizado correctamente a `{await commands.clean_content().convert(ctx, prefix)}`'))


# 	#changelog
# 	@commands.cooldown(1, 3.0, commands.BucketType.user)
# 	@commands.command(aliases=['release', 'version'])
# 	async def changelog(self, ctx, version=None):
# 		title = 'Changelog'
# 		sql = {'stable':"SELECT VERSION FROM CHANGELOG WHERE HIDDEN=0", 'dev':"SELECT VERSION FROM CHANGELOG"}[core.bot_mode]
		
# 		if version == 'list':
# 			core.cursor.execute(sql)
# 			versions = core.cursor.fetchall()
# 			core.conn.commit()
# 			versions.reverse()
# 			embed = discord.Embed(title='Changelog', colour=core.default_color(ctx))
# 			version_list = ', '.join([f'`{version[0]}`' for version in versions])
# 			embed.add_field(name='Lista de versiones:', value=version_list)
# 			embed.set_footer(text=f'Cantidad de versiones: {len(versions)}')
# 			await self.send(ctx, embed=embed)

# 		else:
# 			if version == None:
# 				core.cursor.execute(f"SELECT * FROM CHANGELOG WHERE VERSION='{core.bot_version}'")
# 				summary = core.cursor.fetchall()[0]
# 			else:
# 				core.cursor.execute(sql)
# 				versions = core.cursor.fetchall()
# 				core.conn.commit()
# 				if (version,) in versions:
# 					core.cursor.execute(f"SELECT * FROM CHANGELOG WHERE VERSION=?", (version,))
# 					summary = core.cursor.fetchall()[0]
# 				else:
# 					await self.send(ctx, core.Warning.error('Versión inválida'))
# 					ctx.command.reset_cooldown(ctx)
# 					return
# 			core.conn.commit()
# 			embed = discord.Embed(title=f'Versión {summary[0]} - {summary[1]}', description=summary[2], colour=core.default_color(ctx))
# 			embed.set_footer(text=f'Escribe "{ctx.prefix}changelog list" para ver la lista de versiones')
# 			await self.send(ctx, embed=embed)


# 	# color
# 	@commands.cooldown(1, 1.5, commands.BucketType.user)
# 	@commands.command()
# 	async def color(self, ctx, *, value=None):
# 		components = discord.ActionRow(
# 			discord.SelectMenu(
# 				custom_id='Color',
# 				options=[discord.SelectOption(label='Default', value='default')] + [
# 					discord.SelectOption(
# 						label=color.capitalize(),
# 						value=color
# 					) for color in core.colors
# 				]
# 			)
# 		)
# 		msg = await self.send(ctx, 'Elige un color para tus embeds:', components=components)
# 		def check(interaction, select_menu):
# 			return interaction.author.id == ctx.author.id and select_menu.message.id == ctx.message.id
# 		try:
# 			interaction, select_menu = await ctx.bot.wait_for('selection_select', timeout=120, check=check)
# 		except asyncio.TimeoutError:
# 			await msg.edit(components=components.disable_all_select_menus())
# 			return
# 		await interaction.defer()
# 		value = select_menu.value

# 		# if value == 'list':
# 		# 	color_string = ''
# 		# 	for color in botdata.colors:
# 		# 		color_string += f'- {color}\n'
# 		# 	color_embed = discord.Embed(title='Colores disponibles', description=color_string, colour=botdata.default_color(ctx))
# 		# 	await self.send(ctx, embed=color_embed)

# 		if value == 'default':
# 			core.cursor.execute(f"DELETE FROM COLORS WHERE ID={ctx.message.author.id}")
# 			await interaction.edit(core.Warning.success('El color ha sido reestablecido', components=[]))

# 		else:
# 			if value == 'random':
# 				new_value = 0
# 			else:
# 				try:
# 					new_value = (await commands.ColourConverter().convert(ctx, value)).value
# 				except:
# 					await interaction.edit(core.Warning.error(f'Selecciona un color válido, escribe un código hex (`{ctx.prefix}color #00ffaa`) o selecciona "Default" para reestablecer el color al del rol del bot.'))
# 					ctx.command.reset_cooldown(ctx)
# 					return

# 			core.cursor.execute(f"SELECT ID FROM COLORS WHERE ID={ctx.message.author.id}")
# 			check = core.cursor.fetchall()
# 			if check == []:
# 				core.cursor.execute(f"INSERT INTO COLORS VALUES({ctx.message.author.id}, ?)", (new_value,))
# 			else:
# 				core.cursor.execute(f"UPDATE COLORS SET VALUE=? WHERE ID={ctx.message.author.id}", (new_value,))
# 			await interaction.edit(core.Warning.success(f'El color ha sido cambiado a **{value}**'))

# 		core.conn.commit()


# 	# botinfo
# 	@commands.cooldown(1, 3.0, commands.BucketType.user)
# 	@commands.command(aliases=['stats'])
# 	async def botinfo(self, ctx):
# 		embed = discord.Embed(title='Información del bot', colour=core.default_color(ctx))
# 		data_dict = {
# 			'Librería': f'Discord.py {discord.__version__}',
# 			'Uso de RAM y CPU': f'RAM: {Process().memory_info().vms//1000000} MB \
# / {virtual_memory().used//1000000/1000} GB / {virtual_memory().total//1000000000} GB\n\
# CPU: {Process().cpu_percent()}% / {cpu_percent()}%',
# 			'Uptime': core.fix_delta(datetime.utcnow() - core.bot_ready_at),
# 			'Cantidad de servidores': len(ctx.bot.guilds),
# 			'Cantidad de usuarios': len(ctx.bot.users),
# 			'Dueño del bot': ctx.bot.get_user(ctx.bot.owner_id).mention,
# 			'Links': ' | '.join((f'[{link}]({core.links[link]})' for link in core.links))
# 		}
# 		embed = core.add_fields(embed, data_dict, inline_char=None)
# 		await self.send(ctx, embed=embed)


# 	# commandstats
# 	@commands.cooldown(1, 15.0, commands.BucketType.guild)
# 	@commands.command(aliases=['commanduses', 'cmdstats', 'cmduses'])
# 	async def commandstats(self, ctx, command=None):
# 		if command == None:
# 			core.cursor.execute("SELECT * FROM COMMANDSTATS")
# 			stats = core.cursor.fetchall()
# 			stats.sort(key=lambda x: x[1], reverse=True)
# 			fstats = list(map(lambda x: f'`{x[0]}` - {x[1]}', stats))
# 			pages = core.Page.from_list(ctx, 'Comandos más usados (Desde 27/06/2020)', fstats)
# 			await core.NavBar(ctx, pages=pages, entries=len(fstats)).start()

# 		else:
# 			core.cursor.execute("SELECT * FROM COMMANDSTATS WHERE COMMAND=?", (command,))
# 			stats = core.cursor.fetchall()
# 			if stats == []:
# 				await self.send(ctx, core.Warning.error('El comando que escribiste no existe o no se ha usado'))

# 			else:
# 				stats = stats[0]
# 				await self.send(ctx, core.Warning.info(f'`{stats[0]}` se ha usado {stats[1]} {"veces" if stats[1] != 1 else "vez"}'))
			
# 			ctx.command.reset_cooldown(ctx)
		
# 		core.conn.commit()


async def setup(bot):
	await bot.add_cog(About(bot), guild=core.bot_guild)
