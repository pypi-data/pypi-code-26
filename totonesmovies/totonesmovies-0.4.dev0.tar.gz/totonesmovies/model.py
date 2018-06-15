class Pelicula:
	""" Manipula todos los datos y el comportamiento asociado a las peliculas. """
	def __init__(self,imdb_code,name):
    	""" Seteo los atributos inicialmente en 0 y vacio """
    	self.imdb_code= imdb_code if imdb_code is not None and isnumeric(imdb_code) else ""
    	self.name= name if name is not None else ""

    	self.torrents = [] # 
    	self.cast = [] #
    	self.poster = "avatar.jpg"

