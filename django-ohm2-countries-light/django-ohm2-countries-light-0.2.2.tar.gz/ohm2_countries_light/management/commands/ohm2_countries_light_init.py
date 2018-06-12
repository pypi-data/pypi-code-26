from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from ohm2_handlers_light import utils as h_utils
from ohm2_countries_light import utils as ohm2_countries_light_utils
from ohm2_countries_light import settings
import os, pycountry

class DummyCountry(object):

	def __init__(self, name, official_name, alpha_2, alpha_3, numeric):
		self.name = name.strip().title()
		self.official_name = official_name.strip().title()
		self.alpha_2 = alpha_2.strip()
		self.alpha_3 = alpha_3.strip()
		self.numeric = numeric.strip()


class Command(BaseCommand):
	
	def add_arguments(self, parser):
		parser.add_argument('-f', '--flags',
							action = 'store_true',
							default = False)

	def handle(self, *args, **options):
		flags = options["flags"]
		
		england = DummyCountry("England", "England", "XE", "XEN", "900")
		scotland = DummyCountry("Scotland", "Scotland", "XS", "XSC", "905")
		wales = DummyCountry("Wales", "Wales", "XW", "XWA", "910")
		kosovo = DummyCountry("Kosovo", "Republic of Kosovo", "XK", "XKX", "950")


		countries = list(pycountry.countries)
		countries += [
			england,
			scotland,
			wales,
			kosovo,
		]

		for c in countries:

			if flags:
				flag_small_dst_path = os.path.join(settings.FLAGS_SMALL_BASE_PATH, c.alpha_2.lower() + ".png")
				flag_small_exist = os.path.isfile(flag_small_dst_path)
				if flag_small_exist:
					flag_small = h_utils.new_local_file(flag_small_dst_path)
				else:
					flag_small = None

			else:
				flag_small = None		

			
			official_name = getattr(c, "official_name", c.name)
			country = ohm2_countries_light_utils.get_or_none_country(alpha_3 = c.alpha_3)
			if country is None:
				country = ohm2_countries_light_utils.create_country(c.name, official_name, c.alpha_2, c.alpha_3, c.numeric,
													  				flag_small = flag_small)
			else:
				country = ohm2_countries_light_utils.update_country(country, flag_small = flag_small)
			
			
				


		
			


			