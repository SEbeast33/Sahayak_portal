from django.core.management.base import BaseCommand
from schemes.views import index_all_schemes, create_index

class Command(BaseCommand):
    help = 'Index all schemes in Elasticsearch'

    def handle(self, *args, **options):
        self.stdout.write('Creating Elasticsearch index...')
        create_index()
        
        self.stdout.write('Starting to index schemes...')
        if index_all_schemes():
            self.stdout.write(self.style.SUCCESS('Successfully indexed all schemes'))
        else:
            self.stdout.write(self.style.ERROR('Failed to index schemes')) 