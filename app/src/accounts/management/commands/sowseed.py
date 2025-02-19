from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel
import random
from faker import Faker
from datetime import date
import json
from datetime import timedelta
from accounts.models import Technical, License, WorkJournal
from equipment.models import ResourceItem, Vehicle
from projects.models import Partner


class Command(BaseCommand):
    help = 'This command creates a list of users'

    def handle(self, *args, **options):
        faker = Faker()
        print('creamos el superuser')
        self.createSuperUser()
        print('creamos los tecnicos')
        self.load_technical(faker)
        print('creamos los registros de jornadas')
        self.load_work_journal(faker)
        #print('creamos las licencias')
        #self.load_license(faker)
        print('creamos los equipos')
        self.load_equipment(faker)
        print('creamos los vehiculos')
        self.load_vehicle(faker)
        print('creamos los proveedores')
        self.load_suppliers(faker)

    def createSuperUser(self):
        user = CustomUserModel.get('eduardouio7@gmail.com')
        if user:
            print('Ya existe el usuario')
            return True
        user = CustomUserModel(
            email='eduardouio7@gmail.com',
            is_staff=True,
            is_superuser=True
        )
        user.set_password('seguro')
        user.save()

        user_test = CustomUserModel(
            email='test@peisol.com.ec',
            first_name='Usuario',
            last_name='Pruebas'
        )
        user_test.set_password('seguro')
        user_test.save()

    def load_technical(self, faker):
        if Technical.objects.exists():
            print('Ya existen los tecnicos')
            return True

        with open('seed/technicals.json', 'r') as file:
            file_content = json.load(file)

        for technical in file_content:
            Technical.objects.create(
                **technical
            )
            #CustomUserModel.objects.create(
            #    email=technical['email'],
            #    first_name=technical['first_name'],
            #    last_name=technical['last_name'],
            #    role=technical['role']
            #)

    def load_work_journal(self, faker):
        if WorkJournal.objects.exists():
            print('Ya existen los registros')
            return True
        technicals = Technical.objects.all()

        for technical in technicals:
            start_date = faker.date_time_this_year()
            WorkJournal.objects.create(
                technical=technical,
                date_start=start_date,
                date_end=start_date + timedelta(days=22),
                is_active=True
            )

    def load_license(self, faker):
        if License.objects.exists():
            print('Ya existen las licencias')
            return True

        users = CustomUserModel.objects.exclude(is_superuser=True)
        for user in users:
            License.objects.create(
                license_key=faker.uuid4(),
                user=user,
                role=user.role,
                activated_on=faker.date_time_this_year(),
                expires_on=faker.future_datetime(),
                is_active=True
            )

    def load_equipment(self, faker):
        if ResourceItem.objects.exists():
            print('Ya existen los equipos')
            return True

        with open('seed/equipments.json', 'r') as file:
            file_content = json.load(file)

        for equipment in file_content:
            print(equipment['code'])
            ResourceItem.objects.create(
                **equipment
            )

    def load_vehicle(self, faker):
        if Vehicle.objects.exists():
            print('Ya existen los vehiculos')
            return True
        with open('seed/vehicles.json', 'r') as file:
            file_content = json.load(file)

            for vehicle in file_content:
                Vehicle.objects.create(**vehicle)

    def load_suppliers(self, faker):
        if Partner.objects.exists():
            print('Ya existen los proveedores')
            return True

        with open('seed/suppliers.json', 'r') as file:
            file_content = json.load(file)

        for supplier in file_content:
            Partner.objects.create(
                **supplier
            )
