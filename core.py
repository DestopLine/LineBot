import asyncio
from datetime import datetime, timedelta

from exceptions import BlacklistUserError, ImageNotFound
from random import choice
from re import fullmatch
from sqlite3 import connect
from requests import head
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

import logging

# stable / dev
bot_mode = 'dev'
bot_version = '2.0'
bot_ready_at = datetime.utcnow()
bot_guild = discord.Object(id=724380436775567440)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging_file = f'{Path().resolve().parent}\\logs\\{datetime.today().date()}_{bot_mode}.log'
handler = logging.FileHandler(filename=logging_file, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

default_prefix = {'stable':'l!', 'dev':'ld!'}[bot_mode]
prefix_table = {'stable':"PREFIXES", 'dev':"DEVPREFIXES"}[bot_mode]

error_logging_channel = 725390426780991531

check_emoji = '<:check:873788609398968370>'
cross_emoji = '<:x_:873229915170947132>'
circle_emoji = '<:o_:873229913518383126>'
empty_emoji = '<:empty:873754002427359252>'

conn = connect(f'{Path().resolve().parent}\\data.sqlite3')
cursor = conn.cursor()

returned_value = None

descs = {
	'ping': 'Muestra en milisegundos lo que tarda el bot en enviar un mensaje desde que mandaste el comando',
	'help': 'Muestra una página de ayuda general o de un comando específico///[comando]',
	'soy': 'Descubre quién eres',
	'say': 'Haz que el bot diga algo///<texto>',
	'emojitext': 'Devuelve el texto transformado en emojis///<texto>',
	'replace': 'Reemplaza el texto del primer parámetro por el segundo parametro en un tercer parámetro. Usa comillas para para los 2 primeros parámetros para usar espacios: `"text 1" "texto 2" texto 3`///<reemplazar esto> <por esto> <en este texto>',
	'spacedtext': 'Devuelve el texto enviado con cada letra espaciada el número de veces indicado///<número de espacios> <texto>',
	'vaporwave': 'Devuelve el texto en vaporwave///<texto>',
	'choose': 'Devuelve una de las opciones dadas, o "Si" o "No" si no le das opciones. Las opciones se separan por comas///[opciones]',
	'poll': 'Crea encuestas de manera sencilla. Los emojis se separan por espacios poniendo `-e` delante, si no se epecifican emojis e usaran :+1: y :-1:///<cuerpo de la encuesta> [-e emojis]',
	'kao': 'Devuelve una lista de kaomojis o un kaomoji específico///[kaomoji] [delete]',
	'purge': 'Elimina la cantidad de mensajes indicada///<número de mensajes a eliminar>',
	'avatar': 'Obtiene tú foto de perfil o la de otro usuario///[usuario]',
	'kick': 'Kickea o expulsa a un miembro del servidor///<miembro> [razón]',
	'ban': 'Banea a un miembro del servidor///<miembro> [razón]',
	'unban': 'Revoca el baneo a un usuario///<ID del usuario> [razón]',
	'defemoji': 'Envia emojis en el estado por defecto de tu dispositivo: \\😂. Si el emoji es personalizado de un server, se enviará su ID///<emojis>',
	'sarcastic': 'ConVIeRtE el TEXtO a SarcAStiCO///<texto>',
	'iq': 'Calcula tu IQ o el de otra persona///[miembro]',
	'tag': 'Añade o usa tags tuyos o de otras personas///<nombre del tag>\ntoggle\ngift <usuario>\nrename <tag> <nuevo nombre>\nedit <tag> <nuevo contenido>\nadd <nombre del tag> <contenido del tag> [flags: -img, -nsfw]\nremove <nombre del tag>\nowner <tag>\nlist [usuario]\nserverlist',
	'links': 'Obtén los links oficiales del bot',
	'someone': 'Menciona a alguien aleatorio del server',
	'ocr': 'Transcribe el texto de la última imagen enviada en el chat///[URL|imagen]',
	'joke': 'Envia un chiste que da menos risa que los de Siri///[ID del chiste] [-img]',
	'nothing': 'Literalmente no hace nada',
	'gay': 'Detecta como de homosexual eres///[usuario]',
	'prefix': 'Cambia el prefijo del bot a nivel de server. Para crear un prefijo con espacios, escribelo entre comillas: `"prefijo"`///<prefijo>',
	'changelog': 'Revisa el registro de cambios de cada versión del bot, o de la última dejando en blanco los parámetros///[versión]\nlist',
	'color': 'Cambia el color de los embeds del bot///<color>\nlist\ndefault',
	'wiktionary': 'Busca una palabra en inglés en el diccionario de Wiktionary///<palabra o expresión>',
	'dle': 'Busca una palabra en español en el Diccionario de la lengua española///<palabra>',
	'die': 'Apaga el bot',
	'getmsg': 'Obtiene los datos de un mensaje///<id>',
	'eval': 'Ejecuta código///<código>',
	'reload': 'Recarga un módulo///<módulo>',
	'unload': 'Descarga un módulo///<módulo>',
	'load': 'Carga un módulo///<módulo>',
	'binary': 'Codifica o decodifica código binario///encode <texto>\ndecode <texto>',
	'morse': 'Codifica o decodifica código morse///encode <texto>\ndecode <texto>',
	'hackban': 'Banea a un usuario sin necesidad de que esté en el server///<ID del usuario> [razón]',
	'userinfo': 'Obtiene información de un usuario. Habrá más información si este usuario se encuentra en este servidor///[usuario]',
	'roleinfo': 'Obtiene información de un rol///<rol>',
	'channelinfo': 'Obtiene la información de un canal de cualquier tipo o una categoría///[canal o categoría]',
	'serverinfo': 'Obtiene la información de este servidor',
	'blacklist': 'Mete o saca a un usuario de la blacklist///<user>',
	'uppercase': 'Convierte un texto a mayúsculas///<texto>',
	'lowercase': 'Convierte un texto a minúsculas///<texto>',
	'swapcase': 'Intercambia las minúsculas y las mayúsculas de un texto///<texto>',
	'capitalize': 'Convierte la primera letra de cada palabra a mayúsculas///<texto>',
	'count': 'Cuenta cuantas veces hay una letra o palabra dentro de otro texto. Recuerda que puedes usar comillas para usar espacios en el primer texto. Puedes pasar comillas vacías ("") para contar caracteres y palabras en general en un texto///<letra o palabras> <texto>',
	'botinfo': 'Obtiene información sobre el bot',
	'tictactoe': 'Juega una partida de Tic Tac Toe contra la maquina o contra un amigo///[usuario]',
	'reverse': 'Revierte un texto///<texto>',
	'randomnumber': 'Obtiene un número aleatorio entre el intervalo especificado. Puedes usar número negativos///<desde el 0 hasta este número>\n<desde este número> <hasta este>',
	'8ball': 'Preguntale algo el bot para que te responda///<pregunta>',
	'didyoumean': 'Escribe un texto que te corrija Google a otro. Separa los 2 textos por punto y coma entre espacios: ` ; `///<Texto 1> ; <Texto 2>',
	'drake': 'Haz un meme con la plantilla de drake. Separa los 2 textos por punto y coma entre espacios: ` ; `///<Texto 1> ; <Texto 2>',
	'bad': 'Ta mal///[imagen]',
	'amiajoke': 'Am I a joke to you?///[imagen]',
	'jokeoverhead': 'El que no entendía la broma///[imagen]',
	'salty': 'El ardido///[imagen]',
	'birb': 'Random birb',
	'dog': 'Imagen random de un perro',
	'cat': 'Imagen random de un gato',
	'sadcat': 'Imagen random de un gato triste',
	'calling': 'Tom llamando hm///<texto>',
	'captcha': 'Cursed captcha///<texto>',
	'facts': 'facts///<texto>',
	'supreme': 'Texto con fuente de Supreme///<light o dark> <texto>',
	'commandstats': 'Muestra cuales son los comandos más usados o cuantos veces se ha usado un comando///[comando]',
	'r34': 'Busca en rule34.xxx. Deja vacío para buscar imagenes aleatorias///[búsqueda]',
	'mcskin': 'Busca una skin de Minecraft según el nombre del usuario que pases///<usuario>',
	'percentencoding': 'Codifica o decodifica código porcentaje o código URL///encode <texto>\ndecode <texto>'
}

colors = {
	'random':discord.Colour.default(),
	'teal':discord.Colour.teal(),
	'dark teal':discord.Colour.dark_teal(),
	'green':discord.Colour.green(),
	'dark green':discord.Colour.dark_green(),
	'blue':discord.Colour.blue(),
	'dark blue':discord.Colour.dark_blue(),
	'purple':discord.Colour.purple(),
	'dark purple':discord.Colour.dark_purple(),
	'magenta':discord.Colour.magenta(),
	'dark magenta':discord.Colour.dark_magenta(),
	'gold':discord.Colour.gold(),
	'dark gold':discord.Colour.dark_gold(),
	'orange':discord.Colour.orange(),
	'dark orange':discord.Colour.dark_orange(),
	'red':discord.Colour.red(),
	'dark red':discord.Colour.dark_red(),
	'lighter grey':discord.Colour.lighter_grey(),
	'dark grey':discord.Colour.dark_grey(),
	'light grey':discord.Colour.light_grey(),
	'darker grey':discord.Colour.darker_grey(),
	'blurple':discord.Colour.blurple(),
	'greyple':discord.Colour.greyple()
}

bucket_types = {
	commands.BucketType.default: 'global',
	commands.BucketType.user: 'usuario',
	commands.BucketType.guild: 'servidor',
	commands.BucketType.channel: 'canal',
	commands.BucketType.member: 'miembro',
	commands.BucketType.category: 'categoría',
	commands.BucketType.role: 'rol'
}

bools = {True: 'Sí', False: 'No'}

links = {
	'Invítame a un servidor': 'https://discord.com/oauth2/authorize?client_id=582009564724199434&scope=bot&permissions=-9',
	'Mi página de DBL': 'https://top.gg/bot/582009564724199434',
	'Vota por mí': 'https://top.gg/bot/582009564724199434/vote'
}


def default_color(ctx):
	cursor.execute(f"SELECT VALUE FROM COLORS WHERE ID={ctx.message.author.id}")
	color = cursor.fetchall()
	if ctx.guild == None:
		return discord.Colour.blue()
	elif color == []:
		try:
			return ctx.guild.me.color
		except AttributeError:
			return discord.Color.blue()
	else:
		if color[0][0] == 0:
			return colors[choice(tuple(colors)[1:])].value
		return int(color[0][0])


# async def askyn(ctx, message:str, timeout=12.0, user=None):
# 	class View(discord.ui.View):
# 		result = None
# 		def check(self, button, interaction):
# 			if interaction.user == ctx.author:
# 				result = button.custom_id == 'yes'

# 		@discord.ui.button(custom_id='yes', style=discord.ButtonStyle.green, emoji=check_emoji)
# 		async def yes_callback(self, button, interaction):
# 			return self.check(button, interaction)

# 		@discord.ui.button(custom_id='no', style=discord.ButtonStyle.red, emoji=cross_emoji)
# 		async def no_callback(self, button, interaction):
# 			return self.check(button, interaction)

# 		async def on_timeout(self):
# 			for child in self.children:
# 				child.disabled = True
# 			await question.edit(view=view)
# 			return None

# 	user = ctx.author if user == None else user
# 	await ctx.bot.get_cog('GlobalCog').send(ctx, Warning.question(message), view=View())
	# //////////
	# def check(interaction, button):
	# 	return interaction.message.id == question.id and interaction.author.id == user.id
	# try:
	# 	interaction, button = await ctx.bot.wait_for('button_click', timeout=timeout, check=check)
	# except asyncio.TimeoutError:
		# for i in range(len(view[0])):
		# 	view[0][i].disabled = True
		# await question.edit(view=view)
		# return None
	# await interaction.defer()
	# return button.custom_id == 'yes'


# async def ask(ctx, message:str, *, timeout=12.0, user=None, regex=None, raises=False):
# 	user = ctx.author if user == None else user
# 	question = await ctx.send(Warning.question(message))
# 	def check(message):
# 		return message.author.id == user.id and (fullmatch(regex, message.content) if regex != None else True) and message.channel.id == ctx.channel.id
# 	try:
# 		message = await ctx.bot.wait_for('message', timeout=timeout, check=check)
# 	except asyncio.TimeoutError:
# 		if raises:
# 			await question.delete()
# 			raise asyncio.TimeoutError
# 		else:
# 			await ctx.bot.get_cog('GlobalCog').send(ctx, Warning.error(f'{user.mention} No respondiste a tiempo'))
# 			return None
# 	await ctx.channel.delete_messages((question, message))
# 	return message.content


async def get_channel_image(ctx):
	async for msg in ctx.history(limit=30):
		if msg.attachments != []:
			return msg.attachments[0].url
		elif msg.embeds != []:
			embed = msg.embeds[0]
			for check in [embed.image.url, embed.thumbnail.url]:
				if check != discord.Embed.Empty:
					return check
	raise ImageNotFound('Image not detected in the channel')


def is_url_image(image_url):
	image_formats = ("image/png", "image/jpeg", "image/jpg")
	r = head(image_url)
	if r.headers["content-type"] in image_formats:
		return True
	return False


async def get_user(ctx, arg:str):
	try:
		return await commands.UserConverter().convert(ctx, arg)
	except:
		try:
			return await ctx.bot.fetch_user(int(arg))
		except:
			return await commands.UserConverter().convert(ctx, '0')


def owner(ctx):
	if ctx.author.id == ctx.bot.owner_id:
		return True
	else:
		raise commands.NotOwner()


def is_owner():
	def predicate(ctx):
		return owner(ctx)
	return commands.check(predicate)


def check_blacklist(ctx, user=None, raises=True):
	user = ctx.author if user == None else user
	cursor.execute(f"SELECT USER FROM BLACKLIST WHERE USER={user.id}")
	check = cursor.fetchall()
	conn.commit()
	if check == []:
		return True
	if raises:
		raise BlacklistUserError('This user is in the blacklist')
	else:
		return False


def config_commands(bot):
	for command in bot.tree.get_commands(guild=bot_guild):
		if command.name in descs:
			command.description = descs[command.name]

		# if command.cog.qualified_name == 'Owner':
		# 	command.add_check(owner)
		# 	bot.add_check(check_blacklist)


def fix_delta(delta:timedelta, *, ms=False, limit=3):
	years = delta.days // 365
	days = delta.days - years * 365
	hours = delta.seconds // 3600
	minutes = (delta.seconds - hours * 3600) // 60
	seconds = (delta.seconds - minutes * 60 - hours * 3600)
	seconds += float(str(delta.microseconds / 1000000)[:3]) if ms and seconds < 10 else 0
	measures = {
		'y': years,
		'd': days,
		'h': hours,
		'm': minutes,
		's': seconds
	}
	for key in tuple(filter(lambda x: measures[x] == 0, measures)):
		measures.pop(key)
	for key in tuple(filter(lambda x: tuple(measures).index(x)+1 > limit, measures)):
		measures.pop(key)
	return ' '.join((f'{measures[measure]}{measure}' for measure in measures))


def fix_date(date:datetime, elapsed=False, newline=False):
	result = f'{date.day}/{date.month}/{date.year} {date.hour}:{date.minute}:{date.second} UTC'
	if elapsed:
		delta = fix_delta(datetime.utcnow() - date)
		result += ('\n' if newline else ' ') + f'(Hace {delta})'
	return result


def add_fields(embed:discord.Embed, data_dict:dict, *, inline_char='~'):
	inline_char = '' if inline_char == None else inline_char
	for data in data_dict:
		if data_dict[data] not in (None, ''):
			if inline_char != '':
				embed.add_field(name=data.replace(inline_char, ''), value=str(data_dict[data]), inline=not data.endswith(inline_char))
			else:
				embed.add_field(name=data, value=str(data_dict[data]), inline=False)
	return embed


def embed_author(embed:discord.Embed, user:discord.User):
	return embed.set_author(name=user.name, icon_url=user.avatar.url)



class ChannelConverter(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			argument = await commands.TextChannelConverter().convert(ctx, argument)
		except:
			try:
				argument = await commands.VoiceChannelConverter().convert(ctx, argument)
			except:
				try:
					argument = await commands.CategoryChannelConverter().convert(ctx, argument)
				except:
					raise commands.BadArgument(f'Channel "{argument}" not found')

		return argument



class Page:
	__slots__ = ('content', 'embed')

	def __init__(self, content: str=None, *, embed: discord.Embed=None):
		self.content = content
		self.embed = embed

	@staticmethod
	def from_list(ctx, title:str, iterable: list, *, colour=None):
		formated = []
		count = 0
		for i in iterable:
			count += 1
			formated.append(f'{count}. {i}')

		pages = []
		for i in range(int((len(formated) - 1)//20 + 1)):
			pages.append(Page(embed=discord.Embed(
				title=title,
				description='\n'.join(formated[i*20:i*20+20]),
				colour=default_color(ctx)
			)))
		return pages



class NavBar:
	__slots__ = ('ctx', 'page_num', 'page', 'pages', 'entries', 'timeout', 'edited_at', 'nav_data', 'message', 'view', 'interaction', 'button')

	def __init__(self, ctx:commands.Context, *, pages: list=[], entries: int=None, timeout=180.0):
		self.ctx = ctx
		self.page_num = 1
		self.page = None
		self.pages = []
		self.entries = entries
		self.timeout = timeout
		self.add_pages(pages)
		self.edited_at = ctx.message.edited_at
		self.nav_data = {
			'first': (u'\U000023ee', 3, 1),
			'back': (u'\U00002b05', 2, 1),
			'next': (u'\U000027a1', 2, len(self.pages)),
			'last': (u'\U000023ed', 3, len(self.pages)),
			'search': (u'\U0001f522', 4, 0),
			# 'stop': (u'\U000023f9', 2, 0)
		}


	def add_pages(self, pages:list):
		count = 0
		for page in pages:
			count += 1
			if page.embed != None:
				page.embed.set_footer(text=(f'Página {len(self.pages)+count} de {len(pages) + len(self.pages)}' if len(self.pages)+len(pages) > 1 else '') + f'{(str(" ("+str(self.entries)+" resultados)")) if self.entries != None else ""}' + (f' | {page.embed.footer.text}' if page.embed.footer.text != discord.Embed.Empty else ""))
		self.pages += pages


	async def start(self):
		self.view = None
		if len(self.pages) > 1:
			self.view = [[]]
			self.page = self.pages[0]
			for custom_id in self.nav_data:
				data = self.nav_data[custom_id]
				if len(self.pages) >= data[1]:
					self.view[0].append(discord.ui.Button(custom_id=custom_id, emoji=data[0], style=discord.ButtonStyle.blurple, disabled=(custom_id in list(self.nav_data.keys())[:2])))
		self.message = await self.ctx.bot.get_cog('GlobalCog').send(self.ctx, self.pages[0].content, embed=self.pages[0].embed, view=self.view)
		if self.view != None:
			await self.wait()


	def check(self, interaction, button):
		if self.edited_at != self.ctx.message.edited_at:
			raise ValueError
		elif interaction.message.id == self.message.id and interaction.author == self.ctx.author:
			return True
		else:
			return False

	async def wait(self):
		try:
			self.interaction, self.button = await self.ctx.bot.wait_for('button_click', timeout=self.timeout, check=self.check)
		except asyncio.TimeoutError:
			await self.message.edit(view=[])
		except ValueError:
			pass

		else:
			await self.interaction.defer()
			nav_id = str(self.button.custom_id)
			if nav_id == 'first' and self.page_num != 1:
				await self.set_page(1)

			elif nav_id == 'back' and self.page_num != 1:
				await self.set_page(self.page_num-1)

			elif nav_id == 'next' and self.page_num != len(self.pages):
				await self.set_page(self.page_num+1)

			elif nav_id == 'last' and self.page_num != len(self.pages):
				await self.set_page(len(self.pages))

			elif nav_id == 'search':
				for i in range(5):
					self.view[0][i].disabled = True
				await self.interaction.edit(view=self.view)
				try:
					search = int(await ask(self.ctx, 'Escribe la pagina a la que quieres ir', regex=r'[0-9]+', timeout=20, raises=True))
				except asyncio.TimeoutError:
					for i in range(5):
						self.view[0][i].disabled = False
					await self.message.edit(view=self.view)
				else:
					if search != self.page_num and (0 < search < len(self.pages)+1):
						await self.set_page(search, interact=False)

			# elif self.nav_emojis[reaction][0] == 'stop':
			# 	await self.message.delete()
			# 	return

			await self.wait()


	async def set_page(self, page:int, interact=True):
		self.page = self.pages[page-1]
		self.page_num = page
		for i in range(len(self.view[0])):
			component = self.view[0][i]
			disabled = self.nav_data[component.custom_id][2] == self.page_num
			self.view[0][i].disabled = disabled
		await (self.interaction.edit if interact else self.message.edit)(content=self.page.content, embed=self.page.embed, view=self.view)



class Warning:
	@staticmethod
	def success(text:str, unicode=False):
		return Warning.emoji_warning((':white_check_mark:', u'\U00002705'), text, unicode)

	@staticmethod
	def cancel(text:str, unicode=False):
		return Warning.emoji_warning((':negative_squared_cross_mark:', u'\U0000274e'), text, unicode)

	@staticmethod
	def error(text:str, unicode=False):
		return Warning.emoji_warning((':warning:', u'\U000026a0'), text, unicode)

	@staticmethod
	def question(text:str, unicode=False):
		return Warning.emoji_warning((':grey_question:', u'\U00002754'), text, unicode)

	@staticmethod
	def info(text:str, unicode=False):
		return Warning.emoji_warning((':information_source:', u'\U00002139'), text, unicode)

	@staticmethod
	def loading(text:str, unicode=False):
		return Warning.emoji_warning((':arrows_counterclockwise:', u'\U0001f504'), text, unicode)

	@staticmethod
	def emoji_warning(emoji, text, unicode):
		return f'{emoji[int(unicode)]} {text}.'



class Tag:
	__slots__ = ('ctx', 'guild', 'user', 'name', 'content', 'img', 'nsfw')

	def __init__(self, ctx, guild_id:int, user_id:int, name:str, content:str, img:bool, nsfw:bool):
		self.ctx = ctx
		self.guild = ctx.bot.get_guild(guild_id)
		self.user = ctx.bot.get_user(user_id)
		self.name = name
		self.content = content
		self.img = img
		self.nsfw = nsfw

	def __str__(self):
		return self.name

	def gift(self, user:discord.Member):
		cursor.execute(f"UPDATE TAGS2 SET USER={user.id} WHERE GUILD={self.guild.id} AND NAME=?", (self.name,))
		conn.commit()
		self.user = user

	def rename(self, name:str):
		cursor.execute(f"UPDATE TAGS2 SET NAME=? WHERE GUILD={self.guild.id} AND NAME=?", (name, self.name))
		conn.commit()
		self.name = name

	def edit(self, content:str, img:bool, nsfw:bool):
		self.content = content
		self.img = img
		self.nsfw = nsfw
		cursor.execute(f"UPDATE TAGS2 SET CONTENT=?, IMG={int(self.img)}, NSFW={int(self.nsfw)} WHERE GUILD={self.guild.id} AND NAME=?", (self.content, self.name))
		conn.commit()

	def delete(self):
		cursor.execute(f"DELETE FROM TAGS2 WHERE GUILD={self.guild.id} AND NAME=?", (self.name,))
		conn.commit()