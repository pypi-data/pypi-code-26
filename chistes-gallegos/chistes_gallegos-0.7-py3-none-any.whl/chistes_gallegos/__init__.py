import random

def get_joke():
    return random.choice([
        u'Por que han dejado de poner peliculas en los aviones en Galicia? ' + 
        u'Porque al terminar la pelicula todos salian por la puerta de atras. ',
        u'¿Cuántos gallegos se necesitan para hundir un submarino?' +
        u' - Dos, uno que golpee de afuera y otro que abra la escotilla.',
        u'Un gallego se muere de la risa, le hacen la autopsia y no le encuentran el chiste.',
        u'Por que a los gallegos no les gusta subirse a la ' +
        u'planta alta de los buses de dos pisos? ' +
        u'porque el piso superior no tiene chofer.'
    ])
