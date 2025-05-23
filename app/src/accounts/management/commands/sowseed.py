from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel
import random
from faker import Faker
from datetime import date, datetime
import json
from datetime import timedelta
from accounts.models import Technical, License, VaccinationRecord, PassTechnical
from equipment.models import ResourceItem, Vehicle
from projects.models import Partner


class Command(BaseCommand):
    help = 'This command creates a list of users'

    def handle(self, *args, **options):
        faker = Faker(['es_ES'])
        print('creamos el superuser')
        self.createSuperUser()
        print('creamos los tecnicos')
        self.load_technical(faker)
        print('creamos los registros de jornadas')
        # print('creamos las licencias')
        # self.load_license(faker)
        print('creamos los equipos')
        self.load_equipment(faker)
        print('creamos los vehiculos')
        self.load_vehicle(faker)
        print('creamos los proveedores')
        self.load_suppliers(faker)
        print('creamos los registros de vacunación')
        self.load_vaccination_records(faker)
        print('creamos los pases técnicos')
        self.load_technical_passes(faker)

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
        if Technical.objects.count() >= 20:
            print('Ya existen suficientes técnicos')
            return True

        # Limpiar técnicos existentes si hay menos de 20
        if Technical.objects.exists():
            Technical.objects.all().delete()

        # Areas de trabajo disponibles
        work_areas = [choice[0]
                      for choice in Technical._meta.get_field('work_area').choices]

        # Crear 20 técnicos con datos aleatorios
        for i in range(20):
            birth_date = faker.date_of_birth(minimum_age=20, maximum_age=55)
            date_joined = faker.date_between(
                start_date='-5y', end_date='today')

            # Fechas para certificados y licencias
            license_issue_date = faker.date_between(
                start_date='-3y', end_date='-6m')
            license_expiry_date = faker.date_between(
                start_date='+6m', end_date='+3y')

            defensive_issue_date = faker.date_between(
                start_date='-2y', end_date='-3m')
            defensive_expiry_date = faker.date_between(
                start_date='+3m', end_date='+2y')

            mae_issue_date = faker.date_between(
                start_date='-18m', end_date='-2m')
            mae_expiry_date = faker.date_between(
                start_date='+2m', end_date='+18m')

            medical_issue_date = faker.date_between(
                start_date='-1y', end_date='-1m')
            medical_expiry_date = faker.date_between(
                start_date='+1m', end_date='+1y')

            # Aleatoriamente dejar algunos campos vacíos
            if random.random() > 0.7:
                defensive_issue_date = None
                defensive_expiry_date = None

            if random.random() > 0.6:
                mae_issue_date = None
                mae_expiry_date = None

            technical = Technical.objects.create(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                work_area=random.choice(work_areas),
                dni=faker.unique.numerify('##########'),
                nro_phone=faker.numerify('09########'),
                birth_date=birth_date,
                date_joined=date_joined,
                license_issue_date=license_issue_date,
                license_expiry_date=license_expiry_date,
                defensive_driving_certificate_issue_date=defensive_issue_date,
                defensive_driving_certificate_expiry_date=defensive_expiry_date,
                mae_certificate_issue_date=mae_issue_date,
                mae_certificate_expiry_date=mae_expiry_date,
                medical_certificate_issue_date=medical_issue_date,
                medical_certificate_expiry_date=medical_expiry_date,
                is_iess_affiliated=random.choice([True, True, True, False]),
                has_life_insurance_policy=random.choice([True, False]),
                quest_ncst_code=faker.bothify(
                    text='QUEST-####-??') if random.random() > 0.4 else None,
                quest_instructor=faker.name() if random.random() > 0.4 else None,
                quest_start_date=faker.date_between(
                    start_date='-1y', end_date='today') if random.random() > 0.4 else None,
                quest_end_date=faker.date_between(
                    start_date='today', end_date='+1y') if random.random() > 0.4 else None,
                notes=faker.paragraph() if random.random() > 0.5 else None,
                is_active=random.choice([True, True, True, False])
            )

            # Crear usuario para algunos técnicos
            if random.random() > 0.6:
                try:
                    user = CustomUserModel.objects.create(
                        email=technical.email,
                        first_name=technical.first_name,
                        last_name=technical.last_name,
                        role='TECNICO'
                    )
                    user.set_password('seguro')
                    user.save()
                except:
                    pass

        print(f'Se han creado {Technical.objects.count()} técnicos')


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

    def load_vaccination_records(self, faker):
        if VaccinationRecord.objects.exists():
            print('Ya existen registros de vacunación')
            return True

        technicals = Technical.objects.all()
        vaccine_types = [choice[0] for choice in VaccinationRecord._meta.get_field(
            'vaccine_type').choices]

        for technical in technicals:
            # Decidir aleatoriamente cuántas vacunas tendrá este técnico (0-6)
            num_vaccines = random.randint(0, 6)
            if num_vaccines == 0:
                continue  # Este técnico no tiene vacunas

            # Seleccionar tipos de vacunas al azar sin repetir
            selected_vaccines = random.sample(vaccine_types, num_vaccines)

            for vaccine_type in selected_vaccines:
                application_date = faker.date_between(
                    start_date='-3y', end_date='today')

                # Determinar si es una vacuna de múltiples dosis
                multi_dose = random.random() > 0.5

                if multi_dose:
                    dose_number = random.randint(1, 3)
                    # Si no es la última dosis, establece fecha para la próxima
                    if dose_number < 3 and random.random() > 0.3:  # Algunas no tienen próxima dosis aunque deberían
                        next_dose_date = application_date + \
                            timedelta(days=random.randint(30, 180))
                    else:
                        next_dose_date = None
                else:
                    dose_number = None
                    next_dose_date = None

                VaccinationRecord.objects.create(
                    technical=technical,
                    vaccine_type=vaccine_type,
                    application_date=application_date,
                    dose_number=dose_number,
                    next_dose_date=next_dose_date,
                    notes=faker.paragraph() if random.random() > 0.7 else None
                )

        print(f'Se han creado {VaccinationRecord.objects.count()} registros de vacunación para {len(set(VaccinationRecord.objects.values_list("technical", flat=True)))} técnicos')

    def load_technical_passes(self, faker):
        if PassTechnical.objects.exists():
            print('Ya existen pases técnicos')
            return True

        technicals = Technical.objects.all()
        bloques = [choice[0] for choice in PassTechnical.BLOQUE_CHOICES]

        # Seleccionar aleatoriamente técnicos que tendrán pases (entre 60% y 80%)
        selected_technicals = random.sample(list(technicals), k=int(
            len(technicals) * random.uniform(0.6, 0.8)))

        for technical in selected_technicals:
            # Fecha de caducidad entre 3 meses y 2 años en el futuro
            fecha_caducidad = faker.date_between(
                start_date='+3m', end_date='+2y')

            # Seleccionar un bloque aleatorio
            bloque = random.choice(bloques)

            PassTechnical.objects.create(
                technical=technical,
                bloque=bloque,
                fecha_caducidad=fecha_caducidad
            )

        print(f'Se han creado {PassTechnical.objects.count()} pases técnicos')
