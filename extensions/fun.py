import asyncio
from random import choice, randint

import discord
from discord import app_commands
from discord.ext import commands
from numpy import empty

import modded_libraries.tictactoe as ttt
from requests import get

import core


class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	# soy
	@app_commands.command()
	@app_commands.checks.cooldown(1, 1.5)
	async def soy(self, interaction):
		await interaction.response.send_message(choice((
			'Eres re gay, te encanta chuparla',
			'Eres un wn con pija dorada',
			'Eres un jugador de Free Fire y te matan 2374 veces por partida',
			'Eres mi exclavo sexual B)',
			'Eres un gamer de nivel superior :cowboy:',
			'Eres el novio de Trump B(',
			'Eres el CEO de Anonymous y le puedes hackear la PC al Tech Nigga',
			'Eres hijo de WindyGirk y Yao Cabrera',
			'Eres hijo de Elon Musk :o',
			'gay',
			'Eres más gordo que Nikocado Avocado',
			'Sos un capo sabelo',
			'Eres anti-vacunas',
			'Eres alguien',
			'Zoquete',
			'Eres Eren Jeager',
			'Un indigente',
			'Eres un gordo termotanque',
			'La reencarnación de la Reina Isabel II',
			'Serás el primer ser humano en pisar Jupiter',
			'Tu vieja',
			'No sé',
			'Eres un jugador de Genshin Impact al que hay que alejar de los niños cuanto antes',
			'Eres un jugador de lol que pesa 180 kg'
		)))


	# iq
	@app_commands.command(name='iq')
	@app_commands.checks.cooldown(1, 1.5)
	@app_commands.rename(user='usuario')
	async def _iq(self, interaction, user:discord.Member=None):
		"""
		user: discord.Member
			Usuario al que buscar IQ
		"""
		iqs = (
			'-10, tu cabeza está en blanco, ni siquiera deberias estar respirando :thinking:',
			'0, cómo entraste siquiera a este servidor?',
			'10, no sabes ni leer seguro',
			'30, un perro iguala tu inteligencia',
			'50, seguro tus padres son hermanos :pensive:',
			'60, alto retraso mental tienes',
			'80, no eres muy tonto, pero no eres inteligente hm',
			'100, justo en la media :o',
			'120, felicidades, ahora te hacen bullying por ser diferente',
			'140, seguro eres el gafitas del salón de clases',
			'150, no puedes cargar con el peso de tu cerebro',
			'170, el Einstein te dicen',
			'200 :0000',
			'300, tu cerebro es una pc master race dou',
			'infinito qqq'
		)
		msg = f'{"Tienes" if user == None else user.name + ", tienes"} un IQ de {choice(iqs)}'
		await interaction.response.send_message(msg)


	# dadjoke
	@app_commands.command()
	@app_commands.checks.cooldown(1, 5.0)
	@app_commands.rename(search='buscar', joke_id='id', image='imagen')
	async def dadjoke(self, interaction, search:str=None, joke_id:str=None, image:bool=False):
		"""
		search: str
			Buscar una broma con el termino indicado
		joke_id: str
			Buscar una broma por su ID
		image: bool
			Mostrar la broma como imagen
		"""
		#search
		if search != None:
			request = get('https://icanhazdadjoke.com/search', params={'term':search}, headers={'Accept':'application/json'}).json()
			try:
				request = request['results'][0]
			except IndexError:
				await interaction.response.send_message(core.Warning.error('No se encontraron resultados'), ephemeral=True)
				return
		# id
		elif joke_id != None:
			url = 'https://icanhazdadjoke.com/j/' + joke_id
		# random
		else:
			url = 'https://icanhazdadjoke.com/'
		if search == None:
			request = get(url, headers={'Accept':'application/json'}).json()
		try:
			request_id = request['id']
			if image:
				url = f'https://icanhazdadjoke.com/j/{request_id}.png'
				embed = discord.Embed(title='Dad joke', colour=core.default_color(interaction)).set_image(url=url).set_footer(text='Joke ID: '+request_id)
			else:
				embed = discord.Embed(title='Dad joke', description=request['joke'], colour=core.default_color(interaction)).set_footer(text='Joke ID: '+request_id)
		except KeyError:
			await interaction.response.send_message(core.Warning.error('ID inválida'), ephemeral=True)
		else: 
			await interaction.response.send_message(embed=embed)


	# nothing
	@app_commands.command()
	async def nothing(self, interaction):
		pass


	# gay
	@app_commands.command()
	@app_commands.checks.cooldown(1, 1.5)
	@app_commands.rename(user='usuario')
	async def gay(self, interaction, user:discord.Member=None):
		"""
		user: discord.Member
			Usuario al que medirle la homosexualidad
		"""
		username = interaction.user.name if user == None else user.name
		percent = randint(0, 100)
		extra = {
			10:'se le cayó el pene',
			9:'le dan asco las mujeres',
			8:'se corre al pensar en hombres',
			7:'le encanta chupar piroca',
			6:'está pensando en penes ahora mismo',
			5:'es bisexual, re normie',
			4:'seguro está enamorado de su mejor amigo',
			3:'es el chico afeminado del grupo',
			2:'aunque no lo acepte, le excita un poco el porno gay',
			1:'hombre heterosexual promedio',
			0:'le dan asco los hombres'
		}[percent//10]
		embed = discord.Embed(
			title='Medidor gamer de homosexualidad',
			description=f'{username} es un {percent}% gay, {extra}.',
			colour=core.default_color(interaction)
		)
		await interaction.response.send_message(embed=embed)


	# tictactoe
	tictactoe_group = app_commands.Group(name='tictactoe', description='...')


	@tictactoe_group.command(name='against-machine')
	@app_commands.checks.cooldown(1, 15)
	async def against_machine(self, interaction: discord.Interaction):
		game = core.TicTacToe(interaction, interaction.user, interaction.guild.me)
		await interaction.response.send_message(game.get_content(), view=game)


	@tictactoe_group.command(name='against-player')
	@app_commands.checks.cooldown(1, 15)
	@app_commands.rename(opponent='oponente')
	async def against_player(self, interaction: discord.Interaction, opponent:discord.Member=None):
		"""
		opponent: discord.Member
			Usuario contra el que quieres jugar
		"""
		if opponent == None:
			join_view = core.JoinView(interaction)
			await interaction.response.send_message(core.Warning.searching(f'**{interaction.user.name}** está buscando un oponente para jugar Tic Tac Toe'), view=join_view)
			await join_view.wait()

			if join_view.user == None:
				return

			else:
				opponent = join_view.user
				await join_view.interaction.response.defer()

		else:
			if opponent.bot:
				await interaction.response.send_message(core.Warning.error('No puedes jugar contra un bot'), ephemeral=True)
				return
			ask_view = core.Confirm(interaction, opponent)
			ask_string = f'{opponent.mention} ¿Quieres unirte a la partida de Tic Tac Toe de **{interaction.user.name}**?' if opponent.id != interaction.user.id else f'¿Estás tratando de jugar contra ti mismo?'
			await interaction.response.send_message(ask_string, view=ask_view)
			await ask_view.wait()

			if ask_view.value == None:
				return
			
			elif not ask_view.value:
				await ask_view.last_interaction.response.edit_message(content=core.Warning.cancel('La partida fue rechazada'), view=ask_view)
				return

			else:
				await ask_view.last_interaction.response.defer()

		game = core.TicTacToe(interaction, interaction.user, opponent)
		await interaction.edit_original_response(content=game.get_content(), view=game)


	# 8ball
	@app_commands.command(name='8ball')
	@app_commands.checks.cooldown(1, 2.5)
	@app_commands.rename(question='pregunta')
	async def _8ball(self, interaction, question:str):
		"""
		question: str
			Pregunta que el bot responderá
		"""
		await interaction.response.send_message(embed=core.embed_author(
			user=interaction.user, 
			embed=discord.Embed(
				title='8ball',
				description=question,
				colour=core.default_color(interaction)
			).add_field(
				name='Respuesta',
				value=choice((
					'Sí', 'No', 'En efecto', 'Quizás', 'Mañana', 'Imposible',
					'El simple hecho de que consideraras que eso podría ser cierto es un insulto hacia la inteligencia humana',
					'¿No era obvio que sí?', 'Está científicamente comprobado que sí',
					'No, imbécil', 'Es muy probable', 'Es casi imposible', 'Para nada',
					'Totalmente', 'No lo sé', 'h', 'No lo sé, busca en Google',
					f'No lo sé, preguntale a {choice(list(filter(lambda x: not x.bot, interaction.guild.members))).mention}'
				))
			)
		))



async def setup(bot):
	await bot.add_cog(Fun(bot), guilds=core.bot_guilds)
