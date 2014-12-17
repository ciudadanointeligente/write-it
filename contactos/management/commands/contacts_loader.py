# coding= utf-8
from django.core.management.base import BaseCommand
from contactos.models import Contact, ContactType
from popit.models import Person
from django.contrib.auth.models import User
import csv


class Command(BaseCommand):
    args = '<owner contact_type csv_file>'

    def handle(self, *args, **options):
        owner_id = User.objects.get(username=args[0]).id
        file_path = args[2]
        file_lines = csv.reader(open(file_path, 'rb'), delimiter=',')
        file_lines.next()
        # contact_indices = [i for i, x in enumerate(first_line) if x == "contact"]
        # TO DO: Iterate and do something with other types of contacts like twitter, whats app, etc.
        # Retrieve mails
        mail_type = ContactType.objects.get(name=args[1])
        second_line = file_lines.next()
        name_index = second_line.index("person name")
        mail_indices = [i for i, x in enumerate(second_line) if x == "mail"]
        for line in file_lines:
            person = Person.objects.get(name=line[name_index])
            for index in mail_indices:
                mail = line[index].decode('utf-8')
                if mail != '':
                    try:
                        Contact.objects.create(
                            contact_type=mail_type,
                            person_id=person.id,
                            owner_id=owner_id,
                            value=mail,
                            )
                    except:
                        print u'excepción con el contacto ' + person.name
