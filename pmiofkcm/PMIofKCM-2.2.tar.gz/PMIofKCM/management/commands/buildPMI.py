# author: Shane Yu  date: April 8, 2017
from django.core.management.base import BaseCommand, CommandError
from udic_nlp_API.settings_database import uri
from PMIofKCM import PMI

class Command(BaseCommand):
	help = 'use this for build pmi of kcm!'
	def add_arguments(self, parser):
		# Positional arguments
		parser.add_argument('--lang', type=str)
		
	def handle(self, *args, **options):
		self.stdout.write(self.style.SUCCESS('start building PMI model!!!'))
		p = PMI(options['lang'], uri)
		p.build()
		p = PMI(options['lang'], uri)
		self.stdout.write(self.style.SUCCESS("測試：臺南市的pmi"))
		self.stdout.write(str(p.get("臺南市", 10)))
		self.stdout.write(self.style.SUCCESS('build PMI model success!!!'))