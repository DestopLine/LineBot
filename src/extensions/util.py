import asyncio
from datetime import timedelta
from operator import xor
import exceptions
import json
from random import choice, randrange
from re import findall, fullmatch, search
from urllib.parse import quote, unquote
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands

from aiohttp import ClientOSError
from requests import get
from modded_libraries.signi import get_defs
from wiktionaryparser import WiktionaryParser as WikPar

import core
import pagination


class Util(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.morse_dict = { 'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 'F':'..-.', 'G':'--.',
		'H':'....', 'I':'..', 'J':'.---', 'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'Ñ':'--.--',
		'O':'---', 'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 'U':'..-', 'V':'...-',
		'W':'.--', 'X':'-..-', 'Y':'-.--', 'Z':'--..', '1':'.----', '2':'..---', '3':'...--',
		'4':'....-', '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.', '0':'-----',
		',':'--..--', '.':'.-.-.-', '?':'..--..', '!':'--..--', '/':'-..-.', '-':'-....-', '(':'-.--.',
		')':'-.--.-', '"':'.-..-.', ':':'---...', ';':'-.-.-.', '\'':'.----.', '=':'-...-',
		'&':'.-...', '+':'.-.-.', '_':'..--.-', '$':'...-..-', '@':'.--.-.', ' ':'/'}


	def add_tag(self, interaction: discord.Interaction, name:str, content:str, nsfw:bool):
		core.cursor.execute("INSERT INTO TAGS2 VALUES(?,?,?,?,?,?)", (interaction.guild.id, interaction.user.id, name, content, int(nsfw), 0))
		core.conn.commit()


	def check_tag_name(self, interaction: discord.Interaction, tag_name: str):
		for char in tag_name:
			if char in (' ', '_', '~', '*', '`', '|', ''):
				raise ValueError('Invalid characters detected')
		if tag_name in [tag.name for tag in self.get_guild_tags(interaction)]:
			raise exceptions.ExistentTagError(f'Tag "{tag_name}" already exists')


	def get_tag(self, interaction, name:str, guild=None):
		core.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={interaction.guild_id if guild == None else guild.id} AND NAME=?", (name,))
		tag = core.cursor.fetchall()
		core.conn.commit()
		if tag != []:
			tag = tag[0]
			return core.Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5]))
		else:
			raise exceptions.NonExistentTagError('This tag does not exist')


	def get_member_tags(self, interaction, user:discord.Member):
		core.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={interaction.guild.id} AND USER={user.id}")
		tags = core.cursor.fetchall()
		core.conn.commit()
		if tags != []:
			return [core.Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5])) for tag in tags]
		else:
			raise exceptions.NonExistentTagError('This user doesn\'t have tags')


	def get_guild_tags(self, interaction):
		core.cursor.execute(f"SELECT * FROM TAGS2 WHERE GUILD={interaction.guild.id}")
		tags = core.cursor.fetchall()
		core.conn.commit()
		if tags != []:
			return [core.Tag(interaction, tag[0], tag[1], tag[2], tag[3], bool(tag[4]), bool(tag[5])) for tag in tags]
		else:
			raise exceptions.NonExistentTagError('This server doesn\'t have tags')


	# choose
	@app_commands.command()
	@app_commands.checks.cooldown(1, 3)
	@app_commands.rename(
		option1='opción1',
		option2='opción2',
		option3='opción3',
		option4='opción4',
		option5='opción5',
		option6='opción6',
		option7='opción7',
		option8='opción8',
		option9='opción9',
		option10='opción10',
	)
	async def choose(
		self,
		interaction:discord.Interaction,
		option1:str,
		option2:str,
		option3:str=None,
		option4:str=None,
		option5:str=None,
		option6:str=None,
		option7:str=None,
		option8:str=None,
		option9:str=None,
		option10:str=None,
	):
		embed = discord.Embed(
			title='Mi elección es...',
			description=choice(list(filter(lambda x: x != None, [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]))),
			colour=core.default_color(interaction)
		)
		await interaction.response.send_message(embed=embed)


	# poll
	@app_commands.command()
	@app_commands.checks.cooldown(1, 10)
	@app_commands.rename(
		description='descripción',
		option1='opción1',
		option2='opción2',
		option3='opción3',
		option4='opción4',
		option5='opción5',
		option6='opción6',
		option7='opción7',
		option8='opción8',
		option9='opción9',
		option10='opción10',
	)
	async def poll(
		self,
		interaction:discord.Interaction,
		description: app_commands.Range[str, 1, 256],
		option1:str,
		option2:str,
		option3:str=None,
		option4:str=None,
		option5:str=None,
		option6:str=None,
		option7:str=None,
		option8:str=None,
		option9:str=None,
		option10:str=None,
	):
		"""
		description: app_commands.Range[str, 1, 256]
			Una pregunta, tema o afirmación que describa la encuesta
		"""
		emojis = [f'{number}\ufe0f\u20e3' for number in range(1, 10)] + [u'\U0001f51f',]
		options = list(filter(lambda x: x != None, [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]))
		embed = discord.Embed(
			title=description,
			description='\n'.join([f'{emojis[option]} {options[option]}' for option in range(len(options))]),
			colour=core.default_color(interaction)
		)
		embed.set_author(name=f'Encuesta hecha por {str(interaction.user.name)}', icon_url=interaction.user.avatar.url)
		await interaction.response.send_message(embed=embed)
		for option in range(len(options)):
			await (await interaction.original_response()).add_reaction(emojis[option])


	# avatar
	@app_commands.command()
	@app_commands.checks.cooldown(1, 3)
	async def avatar(self, interaction: discord.Interaction, user: Union[discord.User, discord.Member]=None):
		if user == None:
			user = interaction.user
		await interaction.response.send_message(embed=discord.Embed(
			title=f'Avatar de {str(user)}',
			colour=core.default_color(interaction)
		).set_image(url=user.display_avatar.url))


	# tag
	@app_commands.guild_only()
	class TagGroup(app_commands.Group):
		pass
	tag_group = TagGroup(name='tag', description='...')


	# tag show
	@tag_group.command(name='show')
	@app_commands.rename(tag_name='tag')
	async def tag_show(self, interaction: discord.Interaction, tag_name: app_commands.Range[str, 1, 32]):
		"""
		tag_name: discord.Range[str, 1, 32]
			Nombre de un tag
		"""
		await core.tag_check(interaction)
		tag = self.get_tag(interaction, tag_name)
		if not (not interaction.channel.is_nsfw() and bool(tag.nsfw)):
			await interaction.response.send_message(await commands.clean_content().convert(interaction, tag.content))
		else:
			await interaction.response.send_message(core.Warning.error('Este tag solo puede mostrarse en canales NSFW'), ephemeral=True)


	# tag toggle
	@app_commands.checks.cooldown(1, 10, key=lambda i: i.guild_id)
	@tag_group.command(name='toggle')
	async def tag_toggle(self, interaction: discord.Interaction):
		if interaction.channel.permissions_for(interaction.user).manage_guild:
			core.cursor.execute(f"SELECT GUILD FROM TAGSENABLED WHERE GUILD={interaction.guild_id}")
			check = core.cursor.fetchall()
			if check == []:
				confirmation = core.Confirm(interaction, interaction.user)
				await interaction.response.send_message(core.Warning.question('Los tags en este servidor están desactivados. ¿Quieres activarlos?'), view=confirmation, ephemeral=True)
				await confirmation.wait()

				if confirmation.value == None:
					return

				confirmation.clear_items()

				if confirmation.value:
					core.cursor.execute(f"INSERT INTO TAGSENABLED VALUES({interaction.guild_id})")
					await confirmation.last_interaction.response.edit_message(content=core.Warning.success('Se activaron los tags en este servidor'), view=confirmation)

				else:
					await confirmation.last_interaction.response.edit_message(content=core.Warning.cancel('No se activaran los tags en este servidor'), view=confirmation)

			else:
				confirmation = core.Confirm(interaction, interaction.user)
				await interaction.response.send_message(core.Warning.question('Los tags en este servidor están activados. ¿Quieres desactivarlos?'), view=confirmation, ephemeral=True)
				await confirmation.wait()

				if confirmation.value == None:
					return

				confirmation.clear_items()

				if confirmation.value:
					core.cursor.execute(f"DELETE FROM TAGSENABLED WHERE GUILD={interaction.guild_id}")
					await confirmation.last_interaction.response.edit_message(content=core.Warning.success('Se desactivaron los tags en este servidor'), view=confirmation)

				else:
					await confirmation.last_interaction.response.edit_message(content=core.Warning.cancel('No se desactivarán los tags en este servidor'), view=confirmation)
			
			core.conn.commit()

		else:
			await interaction.response.send_message(core.Warning.error('Necesitas permiso de gestionar servidor para activar o desactivar los tags'), ephemeral=True)


	# tag add
	@app_commands.checks.cooldown(1, 10)
	@tag_group.command(name='add')
	@app_commands.rename(tag_name='nombre', tag_content='contenido')
	async def tag_add(
		self,
		interaction:discord.Interaction, 
		tag_name: app_commands.Range[str, 1, 32], 
		tag_content: str,
		nsfw: bool = False
	):
		"""
		tag_name: app_commands.Range[str, 1, 32]
			Nombre del tag que quieres crear
		tag_content: str
			Contenido del tag que quieres crear
		nsfw: bool = False
			Determina si el tag puede mostrarse únicamente en canales NSFW
		"""
		await core.tag_check(interaction)
		self.check_tag_name(interaction, tag_name)
		if interaction.channel.nsfw:
			nsfw = True
		self.add_tag(interaction, tag_name, tag_content, nsfw)
		await interaction.response.send_message(core.Warning.success(f'Se agregó el tag **{await commands.clean_content().convert(interaction, tag_name)}**'))


	# tag gift
	@app_commands.checks.cooldown(1, 10)
	@tag_group.command(name='gift')
	@app_commands.rename(tag_name='tag', user='usuario')
	async def tag_gift(self, interaction: discord.Interaction, 
		tag_name: app_commands.Range[str, 1, 32],
		user: discord.Member
	):
		await core.tag_check(interaction)
		if user == interaction.user:
			await interaction.response.send_message(core.Warning.error('No puedes regalarte un tag a ti mismo'), ephemeral=True)
		elif user.bot:
			await interaction.response.send_message(core.Warning.error('No puedes regalarle un tag a un bot'), ephemeral=True)
		else:
			tag: core.Tag = self.get_tag(interaction, tag_name)
			if tag.user.id != interaction.user.id:
				await interaction.response.send_message(core.Warning.error('No puedes regalar el tag de otra persona'), ephemeral=True)
				return
			gift_permission = core.Confirm(interaction, user)
			await interaction.response.send_message(core.Warning.question(f'{user.mention} ¿Quieres aceptar el tag **{await commands.clean_content().convert(interaction, tag.name)}** por parte de {interaction.user.name}?'), view=gift_permission)
			await gift_permission.wait()

			if gift_permission.value == None:
				return
			
			gift_permission = gift_permission.clear_items()

			if gift_permission.value:
				tag.gift(user)
				await gift_permission.last_interaction.response.edit_message(content=core.Warning.success(f'El tag **{await commands.clean_content().convert(interaction, tag.name)}** fue regalado a {await commands.clean_content().convert(interaction, tag.user.name)} por parte de {await commands.clean_content().convert(interaction, interaction.user.name)}'), view=gift_permission)

			elif not gift_permission.value:
				await gift_permission.last_interaction.response.edit_message(content=core.Warning.cancel(f'{interaction.user.mention} El regalo fue rechazado'), view=gift_permission)


	# tag rename
	@app_commands.checks.cooldown(1, 5)
	@tag_group.command(name='rename')
	@app_commands.rename(old_name='tag', new_name='nuevo')
	async def tag_rename(self, interaction: discord.Interaction,
		old_name: app_commands.Range[str, 1, 32],
		new_name: app_commands.Range[str, 1, 32]
	):
		await core.tag_check(interaction)
		self.check_tag_name(interaction, new_name)
		tag = self.get_tag(interaction, old_name)
		if tag.user.id == interaction.user.id:
			if tag.name == new_name:
				await interaction.response.send_message(core.Warning.error('No puedes ponerle el mismo nombre a un tag'), ephemeral=True)
			else:
				tag.rename(new_name)
				await interaction.response.send_message(core.Warning.success(f'El nombre del tag **{await commands.clean_content().convert(interaction, old_name)}** se ha cambiado a **{await commands.clean_content().convert(interaction, new_name)}**'))

		else:
			await interaction.response.send_message(core.Warning.error('No puedes renombarar el tag de otro usuario'), ephemeral=True)


	# tag edit
	@app_commands.checks.cooldown(1, 10)
	@tag_group.command(name='edit')
	@app_commands.rename(tag_name='tag', tag_content='contenido')
	async def tag_edit(
		self,
		interaction: discord.Interaction,
		tag_name: app_commands.Range[str, 1, 32],
		tag_content: str,
		*,
		nsfw: bool = False
	):
		"""
		tag_name: app_commands.Range[str, 1, 32]
			Nombre del tag que quieres editar
		tag_content: str
			Nuevo contenido del tag
		nsfw: bool = False
			Determina si el tag puede mostrarse únicamente en canales NSFW
		"""
		await core.tag_check(interaction)
		tag = self.get_tag(interaction, tag_name)
		if interaction.user.id == tag.user.id:
			if interaction.channel.nsfw:
				nsfw = True
			tag.edit(tag_content, False, nsfw)
			await interaction.response.send_message(core.Warning.success(f'Se editó el tag **{await commands.clean_content().convert(interaction, tag_name)}**'))
		
		else:
			await interaction.response.send_message(core.Warning.error('No puedes editar tags de otros usuarios'), ephemeral=True)


	# tag delete
	@app_commands.checks.cooldown(1, 5)
	@tag_group.command(name='delete')
	@app_commands.rename(tag_name='tag')
	async def tag_delete(self, interaction: discord.Interaction, tag_name: app_commands.Range[str, 1, 32]):
		await core.tag_check(interaction)
		tag = self.get_tag(interaction, tag_name)
		if interaction.user.id == tag.user.id:
			confirmation = core.Confirm(interaction, interaction.user)
			await interaction.response.send_message(core.Warning.question(f'¿Quieres eliminar el tag **{await commands.clean_content().convert(interaction, tag_name)}**?'), view=confirmation)
			await confirmation.wait()
			
			if confirmation.value == None:
				return
			
			confirmation = confirmation.clear_items()

			if confirmation.value:
				tag.delete()
				await confirmation.last_interaction.response.edit_message(content=core.Warning.success(f'El tag **{await commands.clean_content().convert(interaction, tag_name)}** ha sido eliminado'), view=confirmation)
			
			elif not confirmation.value:
				await confirmation.last_interaction.response.edit_message(content=core.Warning.cancel(f'El tag no será eliminado'), view=confirmation)

		else: 
			await interaction.response.send_message(core.Warning.error('No puedes eliminar tags de otros usuarios'), ephemeral=True)


	# tag forcedelete
	@tag_group.command(name='forcedelete')
	@core.owner_only()
	async def forcedelete(
		self,
		interaction: discord.Interaction,
		tag_name: app_commands.Range[str, 1, 32],
		guild: int = None,
		silent: bool = False
	):
		guild = interaction.guild if guild == None else self.bot.get_guild(guild)
		tag = self.get_tag(interaction, tag_name, guild)
		tag.delete()
		await interaction.response.send_message(core.Warning.success(f'El tag **{await commands.clean_content().convert(interaction, tag_name)}** ha sido eliminado'), ephemeral=silent)


	# tag owner
	@app_commands.checks.cooldown(1, 3)
	@tag_group.command(name='owner')
	@app_commands.rename(tag_name='tag')
	async def tag_owner(self, interaction: discord.Interaction, tag_name: app_commands.Range[str, 1, 32]):
		await core.tag_check(interaction)
		tag = self.get_tag(interaction, tag_name)
		await interaction.response.send_message(core.Warning.info(f'El dueño del tag **{await commands.clean_content().convert(interaction, tag.name)}** es `{await commands.clean_content().convert(interaction, str(tag.user))}`'))


	# tag list
	@app_commands.checks.cooldown(1, 10)
	@tag_group.command(name='list')
	@app_commands.rename(user='usuario')
	async def tag_list(self, interaction: discord.Interaction, user: discord.Member = None):
		await core.tag_check(interaction)
		if user == None:
			user = interaction.user
		tags = list(map(lambda tag: f'"{tag}"', self.get_member_tags(interaction, user)))
		pages = pagination.Page.from_list(interaction, f'Tags de {user.name}', tags)
		if len(pages) == 1:
			paginator = None
		else:
			paginator = pagination.Paginator(interaction, pages=pages, entries=len(tags))
		await interaction.response.send_message(embed=pages[0].embed, view=paginator)


	# tag serverlist
	@app_commands.checks.cooldown(1, 20)
	@tag_group.command(name='serverlist')
	async def tag_serverlist(self, interaction: discord.Interaction):
		await core.tag_check(interaction)
		tags = list(map(lambda tag: f'{tag.user.name}: "{tag}"', self.get_guild_tags(interaction)))
		pages = pagination.Page.from_list(interaction, f'Tags de {interaction.guild}', tags)
		if len(pages) == 1:
			paginator = None
		else:
			paginator = pagination.Paginator(interaction, pages=pages, entries=len(tags))
		await interaction.response.send_message(embed=pages[0].embed, view=paginator)


	# someone
	@app_commands.checks.cooldown(3, 10)
	@app_commands.command()
	@app_commands.rename(mention='mencionar')
	async def someone(self, interaction: discord.Interaction, mention: bool = False):
		"""
		mention: bool = False
			Determina si mencionar o no al usuario. Requiere permiso para hacer @everyone
		"""
		if mention and interaction.channel.permissions_for(interaction.user).mention_everyone:
			await interaction.response.send_message(choice(interaction.guild.members).mention)
		else:
			await interaction.response.send_message(str(choice(interaction.guild.members)))


	class DefineGroup(app_commands.Group):
		pass
	define_group = DefineGroup(name='define', description='...')


	# # define spanish
	# @app_commands.checks.cooldown(1, 5)
	# @define_group.command()
	# async def spanish(self, interaction: discord.Interaction, query: str):
	# 	query = query.lower()
	# 	defs = ic(get_defs(query))
	# 	if defs != ['']:
	# 		embed = discord.Embed(title=query.capitalize(), colour=core.default_color(interaction)).set_author(name='DLE', icon_url=interaction.user.avatar.url)
	# 		count = 0
	# 		desc = ''
	# 		pages = []
	# 		for _def in defs:
	# 			if len(desc + f'{_def}\n') > 2048:
	# 				embed.description = desc
	# 				pages.append(pagination.Page(embed=embed))
	# 				desc = ''
	# 				embed = discord.Embed(title=query.capitalize(), colour=core.default_color(interaction)).set_author(name='DLE', icon_url=interaction.user.avatar.url)

	# 			count += 1
	# 			number = int(findall(r'^[0-9]+', _def)[0])
	# 			if count != number:
	# 				desc += '\n'
	# 				count = number
	# 			desc += f'{_def}\n'
			
	# 		embed.description = desc
	# 		pages.append(pagination.Page(embed=embed))
			
	# 		if len(pages) == 1:
	# 			paginator = None
	# 		else:
	# 			paginator = pagination.Paginator(interaction, pages=pages, entries=len(defs))
	# 		await interaction.response.send_message(embed=pages[0].embed, view=paginator)
		
	# 	else:
	# 		await interaction.response.send_message(core.Warning.error('Palabra no encontrada'))


# 	# wiktionary
# 	@commands.cooldown(1, 5.0, commands.BucketType.user)
# 	@app_commands.command(aliases=['wikt', 'wt'])
# 	async def wiktionary(self, ctx, *, query=None):
# 		if query == None:
# 			await self.send(ctx, core.Warning.error(f'Escribe una palabra en inglés para buscar su significado. Para buscar palabras en español, usa `{ctx.prefix}dle`'))
# 			ctx.command.reset_cooldown(ctx)

# 		else:
# 			query = query.capitalize()
# 			parser = WikPar()
# 			try:
# 				word = parser.fetch(query.lower())[0]
# 			except IndexError:
# 				word = {'etymology': '', 'definitions': [], 'pronunciations': {'text': [], 'audio': []}}
# 			if word == {'etymology': '', 'definitions': [], 'pronunciations': {'text': [], 'audio': []}}:
# 				await self.send(ctx, core.Warning.error('Palabra no encontrada'))
# 				ctx.command.reset_cooldown(ctx)
# 			else:
# 				pages = [pagination.Page(embed=discord.Embed(title=query, colour=core.default_color(ctx)).set_author(name='Wiktionary', icon_url=ctx.message.author.avatar.url))]
# 				entries = 0
# 				for definition in word['definitions']:
# 					value = ['']
# 					count = 0
# 					page_count = 0
					
# 					for entry in definition['text']:
# 						entries += 1 if count != 0 else 0
# 						if len(value[page_count] + f'{count}. {entry}\n' if count > 0 else f'{entry}\n') > 1022:
# 							value.append('')
# 							page_count += 1
# 							pages.append(pagination.Page(embed=discord.Embed(title=query, colour=core.default_color(ctx)).set_author(name='Wiktionary', icon_url=ctx.message.author.avatar.url)))
# 						value[page_count] += f'{count}. {entry}\n' if count > 0 else f'{entry}\n'
# 						count += 1
					
# 					for i in range(len(value)):
# 						pages[i].embed.add_field(name=definition['partOfSpeech'].capitalize(), value=value[i], inline=False)
				
# 				await core.NavBar(ctx, pages=pages, entries=entries).start()


	# binary
	class BinaryGroup(app_commands.Group):
		pass
	binary_group = BinaryGroup(name='binary', description='...')


	# binary encode
	@app_commands.checks.cooldown(1, 3)
	@binary_group.command(name='encode')
	@app_commands.rename(text='texto')
	async def binary_encode(self, interaction: discord.Interaction, text: str):
		"""
		text: str
			El texto que será codificado
		"""
		string = ' '.join(bin(ord(char)).split('b')[1].rjust(8, '0') for char in text)
		await interaction.response.send_message(f'```{string}```')


	# binary decode
	@app_commands.checks.cooldown(1, 3)
	@binary_group.command(name='decode')
	@app_commands.rename(text='texto')
	async def binary_decode(self, interaction: discord.Interaction, text: str):
		"""
		text: str
			El texto que será decodificado
		"""
		if search(r'[^0-1]', text.replace(' ', '')):
			await interaction.response.send_message(core.Warning.error('El texto debe ser binario (unos y ceros)'), ephemeral=True)

		else:
			string = text.replace(' ', '')
			string = " ".join(string[i:i+8] for i in range(0, len(string), 8))
			string = ''.join(chr(int(binary, 2)) for binary in string.split(' '))
			await interaction.response.send_message(f'```{await commands.clean_content().convert(interaction, string.replace("`", "`឵"))}```')


	# morse
	class MorseGroup(app_commands.Group):
		pass
	morse_group = MorseGroup(name='morse', description='...')


	# morse encode
	@app_commands.checks.cooldown(1, 3)
	@morse_group.command(name='encode')
	@app_commands.rename(text='texto')
	async def morse_encode(self, interaction: discord.Interaction, text: str):
		"""
		text: str
			El texto que será codificado
		"""
		string = ''
		text = text.upper()
		for letter in text:
			if letter in self.morse_dict:
				string += self.morse_dict[letter] + ' '
		await interaction.response.send_message(f'```{string}```' if string != '' else core.Warning.error('Los caracteres especificados son incompatibles'))


	# morse decode
	@app_commands.checks.cooldown(1, 3)
	@morse_group.command(name='decode')
	@app_commands.rename(text='texto')
	async def morse_decode(self, interaction: discord.Interaction, text: str):
		"""
		text: str
			El texto que será decodificado
		"""
		text += ' '
		string = ''
		citext = ''
		for letter in text:
			if letter != ' ':
				citext += letter
			else:
				if citext in list(self.morse_dict.values()):
					string += list(self.morse_dict.keys())[list(self.morse_dict.values()).index(citext)] 
				citext = ''
		await interaction.response.send_message(f'```{(await commands.clean_content().convert(interaction, string)).capitalize()}```' if string != '' else core.Warning.error('Los caracteres especificados son incompatibles'))

	
	# percentencoding
	class PercentGroup(app_commands.Group):
		pass
	percent_group = PercentGroup(name='percent-encoding', description='...')


	# percentencoding encode
	@app_commands.checks.cooldown(1, 3)
	@percent_group.command(name='encode')
	@app_commands.rename(text='texto')
	async def percentencoding_encode(self, interaction: discord.Interaction, text: str):
		"""
		text: str
			El texto que será codificado
		"""
		await interaction.response.send_message(f'```{quote(text)}```')


	# percentencoding decode
	@app_commands.checks.cooldown(1, 3)
	@percent_group.command(name='decode')
	@app_commands.rename(text='texto')
	async def percentencoding_decode(self, interaction: discord.Interaction, text: str):
		"""
		text: str
			El texto que será decodificado
		"""
		await interaction.response.send_message(f'```{await commands.clean_content().convert(interaction, unquote(text))}```')


	# userinfo
	@app_commands.checks.cooldown(1, 5)
	@app_commands.command()
	@app_commands.rename(user='usuario')
	@commands.guild_only()
	async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
		if user == None:
			user = interaction.user
		data_dict = {
			'Usuario': str(user),
			'ID': user.id,
			'Tipo de cuenta~': {True:'Bot', False:'Usuario'}[user.bot] + (' del sistema de discord' if user.system else ''),
			'Fecha de creación de la cuenta': core.fix_date(user.created_at, elapsed=True, newline=True)
		}
		if interaction.guild.get_member(user.id) != None:
			user = interaction.guild.get_member(user.id)
			data_dict.update({
				'Apodo':user.nick,
				'Fecha de entrada al servidor': core.fix_date(user.joined_at, elapsed=True, newline=True),
				'Permisos en este canal~': f'Integer: `{interaction.channel.permissions_for(user).value}`\n' + ', '.join((f'{("`"+perm[0].replace("_"," ").capitalize()+"`") if perm[1] else ""}' for perm in tuple(filter(lambda x: x[1], tuple(interaction.channel.permissions_for(user)))))),
				'Boosteando el servidor desde': core.fix_date(user.premium_since, elapsed=True, newline=True) if user.premium_since != None else None,
				'Actividades':'\n'.join(({
					discord.ActivityType.unknown: 'Desconocido ',
					discord.ActivityType.playing: 'Jugando a ',
					discord.ActivityType.streaming: 'Transmitiendo ',
					discord.ActivityType.listening: 'Escuchando ',
					discord.ActivityType.watching: 'Viendo ',
					discord.ActivityType.custom:''
					}[activity.type]+(f'**{activity.name}**' if activity.type != discord.ActivityType.custom else str(user.activity)) for activity in user.activities)) if len(user.activities) > 0 else None,
				'Color HEX':str(user.color),
				'Estados':'\n'.join((client[0]+{
						'online': 'En linea',
						'offline': 'Desconectado',
						'idle': 'Ausente',
						'dnd': 'No molestar'
					}[str(client[1])] for client in ((':desktop: ', user.desktop_status), (':iphone: ', user.mobile_status), (':globe_with_meridians: ', user.web_status)))),
				})
		embed = discord.Embed(title='Información del usuario', colour=core.default_color(interaction)).set_thumbnail(url=user.avatar.url)
		for data in data_dict:
			if data_dict[data] != None:
				if data == 'Apodo':
					embed.insert_field_at(1, name=data, value=data_dict[data])
				else:	
					embed.add_field(name=data.replace('~', ''), value=data_dict[data], inline=not data.endswith('~'))
		await interaction.response.send_message(embed=embed)


	# roleinfo
	@app_commands.checks.cooldown(1, 3)
	@app_commands.command()
	@app_commands.rename(role='rol')
	@commands.guild_only()
	async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
		data_dict = {
			'Nombre': role.name,
			'Mención': role.mention,
			'ID': role.id,
			'Posición': f'{role.position} de {len(interaction.guild.roles)-1}',
			'Mencionable': core.bools[role.mentionable],
			'Aparece separado': core.bools[role.hoist],
			'Manejado por una integración': core.bools[role.managed],
			'Color HEX': str(role.color),
			'Fecha de creación': core.fix_date(role.created_at, elapsed=True, newline=True),
			'Cantidad de usuarios': f'{len(role.members)} de {len(interaction.guild.members)}',
			'Permisos~': f'Integer: `{role.permissions.value}`\n' + ', '.join((f'{("`"+perm[0].replace("_"," ").capitalize()+"`") if perm[1] else ""}' for perm in tuple(filter(lambda x: x[1], tuple(role.permissions)))))
		}
		embed = discord.Embed(title='Información del rol', colour=core.default_color(interaction))
		embed = core.add_fields(embed, data_dict)
		await interaction.response.send_message(embed=embed)


	# channelinfo
	@app_commands.checks.cooldown(1, 3)
	@app_commands.command()
	@app_commands.rename(channel='canal')
	async def channelinfo(self, interaction: discord.Interaction, channel: app_commands.AppCommandChannel = None):
		if channel == None:
			channel = interaction.channel
		if isinstance(channel, app_commands.AppCommandChannel):
			channel = await channel.fetch()
		data_dict = {
			'Nombre': str(channel),
			'ID': channel.id,
			'Fecha de creación': core.fix_date(channel.created_at, elapsed=True, newline=True),
			'Tipo de canal': {
				discord.ChannelType.text: 'Canal de texto',
				discord.ChannelType.voice: 'Canal de voz',
				discord.ChannelType.private: 'Mensaje directo',
				discord.ChannelType.category: 'Categoría',
				discord.ChannelType.news: 'Canal de noticias',
				discord.ChannelType.stage_voice: 'Escenario',
				discord.ChannelType.news_thread: 'Hilo de noticias',
				discord.ChannelType.public_thread: 'Hilo público',
				discord.ChannelType.private_thread: 'Hilo privado',
				discord.ChannelType.forum: 'Foro'
			}[channel.type]
		}

		if channel.type in (discord.ChannelType.text, discord.ChannelType.news):
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(interaction.guild.text_channels)}',
				'Categoría': channel.category,
				'Cantidad de hilos activos': len(channel.threads),
				'Hilos se ocultan después de:': core.fix_delta(timedelta(minutes=channel.default_auto_archive_duration), compact=False),
				'Tema': channel.topic,
				'Slowmode': core.fix_delta(timedelta(seconds=channel.slowmode_delay), compact=False),
				'Miembros que pueden ver el canal': f'{len(channel.members)} de {len(interaction.guild.members)}',
				'Es NSFW': core.bools[channel.nsfw]
			})

		elif channel.type in (discord.ChannelType.news_thread, discord.ChannelType.public_thread, discord.ChannelType.private_thread):
			data_dict.update({
				'Categoría': channel.category,
				'Archivado': core.bools[channel.archived],
				'Bloqueado': core.bools[channel.locked],
				'Dueño': str(channel.owner),
				'Canal principal': str(channel.parent),
				'Slowmode': core.fix_delta(timedelta(seconds=channel.slowmode_delay), compact=False),
			})

		elif channel.type == discord.ChannelType.stage_voice:
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(interaction.guild.stage_channels)}',
				'Categoría': channel.category,
				'Es NSFW': core.bools[channel.nsfw],
				'Bitrate': f'{channel.bitrate//1000}kbps',
				'Límite de usuarios': channel.user_limit if channel.user_limit != 0 else 'Sin límite',
				'Cantidad de usuarios en el canal': f'{len(channel.members)} usuarios\n{len(channel.speakers)} oradores\n{len(channel.listeners)} oyentes\n{len(channel.moderators)} moderadores\n{len(channel.requesting_to_speak)} solicitudes para hablar' if channel.members != [] else None,
			})

		elif channel.type == discord.ChannelType.forum:
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(interaction.guild.text_channels)}',
				'Categoría': channel.category,
				'Cantidad de hilos activos': len(channel.threads),
				'Emoji de reacción por defecto': channel.default_reaction_emoji,
				'Hilos se ocultan después de:': core.fix_delta(timedelta(minutes=channel.default_auto_archive_duration), compact=False),
				'Layout': {
					discord.ForumLayoutType.not_set: 'Sin seleccionar',
					discord.ForumLayoutType.list_view: 'Vista de lista',
					discord.ForumLayoutType.gallery_view: 'Vista de galería'
				}[channel.default_layout],
				'Slowmode': core.fix_delta(timedelta(seconds=channel.slowmode_delay), compact=False),
				'Es NSFW': core.bools[channel.nsfw],
			})

		elif channel.type == discord.ChannelType.voice:
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(interaction.guild.voice_channels)}',
				'Categoría': channel.category,
				'Bitrate': f'{channel.bitrate//1000}kbps',
				'Límite de usuarios': channel.user_limit if channel.user_limit != 0 else 'Sin límite',
				'Cantidad de usuarios en el canal': f'{len(channel.members)} de {len(interaction.guild.members)}' if channel.members != [] else None,
			})

		elif channel.type == discord.ChannelType.category:
			data_dict.update({
				'Posición': f'{channel.position+1} de {len(interaction.guild.channels)}',
				'Es NSFW': core.bools[channel.nsfw],
				'Cantidad de canales': f'De texto: {len(channel.text_channels)}\nDe voz: {len(channel.voice_channels)}\nTotal: {len(channel.channels)}'
			})

		embed = discord.Embed(title='Información del canal', colour=core.default_color(interaction))
		embed = core.add_fields(embed, data_dict)
		await interaction.response.send_message(embed=embed)


	# serverinfo
	@app_commands.checks.cooldown(1, 3)
	@app_commands.command()
	@commands.guild_only()
	async def serverinfo(self, interaction: discord.Interaction):
		guild = interaction.guild
		data_dict = {
			'Nombre': guild.name,
			'ID': guild.id,
			'Fecha de creación~': core.fix_date(guild.created_at, elapsed=True),
			'Límite AFK': core.fix_delta(timedelta(seconds=guild.afk_timeout), compact=False),
			'Canal AFK': guild.afk_channel.mention if guild.afk_channel != None else None,
			'Canal de mensajes del sistema': guild.system_channel.mention if guild.system_channel != None else None,
			'Dueño': guild.owner.mention,
			'Máximo de miembros': guild.max_members,
			'Descripción': guild.description,
			'Autenticación de 2 factores': core.bools[bool(guild.mfa_level)],
			'Nivel de verificación~': {
				discord.VerificationLevel.none: 'Ninguno',
				discord.VerificationLevel.low: 'Bajo: Los miembros deben tener un email verificado en su cuenta',
				discord.VerificationLevel.medium: 'Medio: Los miembros deben tener un email verificado y estar registrados por más de 5 minutos',
				discord.VerificationLevel.high: 'Alto: Los miembros deben tener un email verificado, estar registrados por más de 5 minutos y estar en el servidor por más de 10 minutos',
				discord.VerificationLevel.highest: 'Muy alto: Los miembros deben tener un teléfono verificado en su cuenta'
			}[guild.verification_level],
			'Filtro de contenido explícito~': {
				discord.ContentFilter.disabled: 'Deshabilitado',
				discord.ContentFilter.no_role: 'Analizar el contenido multimedia de los miembros sin rol',
				discord.ContentFilter.all_members: 'Analizar el contenido multimedia de todos los miembros'
			}[guild.explicit_content_filter],
			'Nivel NSFW~': {
				discord.NSFWLevel.default: 'Por defecto: El servidor aún no ha sido categorizado',
				discord.NSFWLevel.safe: 'Seguro: El servidor no tiene contenido NSFW',
				discord.NSFWLevel.explicit: 'Explícito: El servidor tiene contenido NSFW',
				discord.NSFWLevel.age_restricted: 'Restringido por edad: El servidor podría tener contenido NSFW'
			}[guild.nsfw_level],
			'Características~': ', '.join((f'`{feature}`' for feature in guild.features)),
			'Número de canales': f'De texto: {len(guild.text_channels)}\nDe voz: {len(guild.voice_channels)}\nEscenarios: {len(guild.stage_channels)}\nForos: {len(guild.forums)}\nCategorías: {len(guild.categories)}\nTotal: {len(guild.channels)}',
			'Cantidad de miembros': f'Usuarios: {len(tuple(filter(lambda x: not x.bot, guild.members)))}\nBots: {len(tuple(filter(lambda x: x.bot, guild.members)))}\nTotal: {len(guild.members)}',
			'Cantidad de roles': len(guild.roles)
		}

		embed = discord.Embed(title='Información del servidor', colour=core.default_color(interaction))
		if str(guild.icon.url) != '':
			embed.set_thumbnail(url=guild.icon.url)
		embed = core.add_fields(embed, data_dict)
		await interaction.response.send_message(embed=embed)


	# count
	@app_commands.checks.cooldown(1, 2)
	@app_commands.command()
	@app_commands.rename(to_count='contar', text='texto')
	async def count(self, interaction: discord.Interaction, text: str, to_count: str = None):
		"""
		text: str
			El texto en el que buscar palabras o caracteres
		to_count: str = None
			Palabra que contar en el texto. Dejar vacío para contar cualquier palabra o carácter
		"""
		count = text.count(to_count)
		embed = discord.Embed(title='Contador de palabras', colour=core.default_color(interaction))
		if to_count == None:
			data_dict = {
				'Cantidad de caracteres': len(text),
				'Cantidad de palabras': len(findall(r'[A-Za-z]+', text))
			}

		else:
			if to_count.startswith(' ') or to_count.endswith(' '):
				to_count = f'"{to_count}"'
			data_dict = {
				'Palabras a contar~': to_count,
				'Caracteres que coinciden': f'{len(to_count*count)} de {len(text)}\n{round(100 / (len(text) / len(to_count*count)), 4) if count > 0 else 0}%'
			}
			if len(to_count) > 1:
				spaced_count = len(findall(r'[^A-Za-z]' + to_count + r'[^A-Za-z]', text))
				data_dict.update({
					'Palabras que coinciden': f'{spaced_count} de {len(text.split(" "))}\n{round(100 / (len(text.split(" ")) / spaced_count), 4) if spaced_count > 0 else 0}%',
				})
		embed = core.add_fields(embed, data_dict)
		await interaction.response.send_message(embed=embed)


	# randomnumber
	@app_commands.command()
	@app_commands.rename(start='mínimo', stop='máximo', step='salto')
	async def randomnumber(self, interaction: discord.Interaction, start: int, stop: int, step: app_commands.Range[int, 1, 1000000000000000] = 1):
		"""
		start: int
			Mínimo valor posible, se incluye en el rango
		stop: int
			Máximo valor posible, se excluye del rango
		step: int = 1
			Distancia entre cada número del rango, el valor por defecto es 1
		"""
		if start >= stop:
			await interaction.response.send_message(core.Warning.error('Intervalo inválido. Revisa que el primer número sea menor que el segundo'), ephemeral=True)
			return

		await interaction.response.send_message(embed=discord.Embed(
			title = f'Número aleatorio entre {start} y {stop}',
			description = str(randrange(start, stop, step)),
			colour = core.default_color(interaction)
		))



async def setup(bot):
	await bot.add_cog(Util(bot), guilds=core.bot_guilds)