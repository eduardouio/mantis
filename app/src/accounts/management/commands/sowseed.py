from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel
import random
from faker import Faker
from datetime import date, datetime
import json
from datetime import timedelta
from accounts.models import Technical, License, VaccinationRecord, PassTechnical
from equipment.models import ResourceItem, Vehicle, PassVehicle, CertificationVehicle
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
        print('creamos las licencias')
        self.load_license(faker)
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
        print('creamos los pases de vehículos')
        self.load_vehicle_passes(faker)
        print('creamos las certificaciones de vehículos')
        self.load_vehicle_certifications(faker)

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

        # Opciones para los nuevos campos
        subtipos = [choice[0] for choice in ResourceItem._meta.get_field('subtipo').choices]
        unidades_capacidad = [choice[0] for choice in ResourceItem._meta.get_field('unidad_capacidad').choices]
        capacidades_planta = [choice[0] for choice in ResourceItem._meta.get_field('capacidad_planta').choices]
        status_choices = [choice[0] for choice in ResourceItem._meta.get_field('status').choices]

        # Crear equipos con datos aleatorios usando los nuevos campos
        equipment_types = ['EQUIPO', 'SERVICIO']
        
        for i in range(50):  # Crear 50 equipos de ejemplo
            equipment_type = random.choice(equipment_types)
            
            # Datos básicos
            base_data = {
                'name': faker.company() + ' ' + faker.word().title(),
                'type': equipment_type,
                'brand': faker.company() if equipment_type == 'EQUIPO' else 'SIN MARCA',
                'model': faker.bothify(text='MOD-##??') if equipment_type == 'EQUIPO' and random.random() > 0.3 else 'N/A',
                'code': faker.unique.bothify(text='EQ-####'),
                'serial_number': faker.unique.bothify(text='SN-????-####') if equipment_type == 'EQUIPO' and random.random() > 0.2 else None,
                'date_purchase': faker.date_between(start_date='-5y', end_date='today') if equipment_type == 'EQUIPO' and random.random() > 0.4 else None,
                'status': random.choice(status_choices),
                'is_active': random.choice([True, True, True, False])
            }
            
            # Solo para equipos, agregar campos específicos
            if equipment_type == 'EQUIPO':
                # Subtipo aleatorio
                subtipo = random.choice(subtipos) if random.random() > 0.2 else None
                base_data['subtipo'] = subtipo
                
                # Dimensiones y peso
                if random.random() > 0.3:
                    base_data.update({
                        'height': random.randint(50, 300),
                        'width': random.randint(40, 250),
                        'depth': random.randint(30, 200),
                        'weight': random.randint(10, 500)
                    })
                
                # Capacidad
                if random.random() > 0.4:
                    base_data['capacidad'] = round(random.uniform(5.0, 1000.0), 2)
                    base_data['unidad_capacidad'] = random.choice(unidades_capacidad)
                
                # Capacidad de planta específica para plantas de tratamiento de agua residual
                if subtipo == 'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL':
                    base_data['capacidad_planta'] = random.choice(capacidades_planta)
                
                # Motivo de reparación si está en reparación
                if base_data['status'] == 'EN REPARACION':
                    base_data['motivo_reparacion'] = faker.paragraph()
                
                # Características específicas según el subtipo
                if subtipo == 'LAVAMANOS':
                    base_data.update({
                        'bombas_pie': random.choice([True, False]),
                        'dispensador_jabon_lavamanos': random.choice([True, False])
                    })
                
                elif subtipo in ['BATERIA SANITARIA HOMBRE', 'BATERIA SANITARIA MUJER']:
                    base_data.update({
                        'dispensador_papel': random.choice([True, False]),
                        'dispensador_jabon': random.choice([True, False]),
                        'dispensador_servilletas': random.choice([True, False]),
                        'asientos': random.choice([True, False]),
                        'bomba_bano': random.choice([True, False]),
                        'bomba_lavamanos': random.choice([True, False]),
                        'tapa_inodoro': random.choice([True, False]),
                        'bases_banos': random.choice([True, False]),
                        'tubo_ventilacion': random.choice([True, False])
                    })
                    
                    # Urinales solo para baterías de hombre
                    if subtipo == 'BATERIA SANITARIA HOMBRE':
                        base_data['urinales'] = random.choice([True, False])
                    else:
                        base_data['urinales'] = False

                # Campos especiales para plantas y tanques
                if subtipo in [
                    'PLANTA DE TRATAMIENTO DE AGUA',
                    'PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
                    'TANQUES DE ALMACENAMIENTO AGUA CRUDA',
                    'TANQUES DE ALMACENAMIENTO AGUA RESIDUAL'
                ]:
                    base_data.update({
                        'blower_marca': faker.company(),
                        'blower_modelo': faker.bothify(text='BLW-##??'),
                        'motor_marca': faker.company(),
                        'motor_modelo': faker.bothify(text='MOT-##??'),
                        'banda_marca': faker.company(),
                        'banda_modelo': faker.bothify(text='BND-##??'),
                        'banda_tipo': random.choice(['A', 'B']),
                        'polea_blower_marca': faker.company(),
                        'polea_blower_modelo': faker.bothify(text='PLB-##??'),
                        'polea_motor_marca': faker.company(),
                        'polea_motor_modelo': faker.bothify(text='PLM-##??'),
                        'tablero_electrico_marca': faker.company(),
                        'tablero_electrico_modelo': faker.bothify(text='TBE-##??'),
                        'guarda_motor_marca': faker.company(),
                        'guarda_motor_modelo': faker.bothify(text='GDM-##??')
                    })
                else:
                    # Para otros subtipos, asegurar que los campos estén vacíos
                    base_data.update({
                        'blower_marca': None,
                        'blower_modelo': None,
                        'motor_marca': None,
                        'motor_modelo': None,
                        'banda_marca': None,
                        'banda_modelo': None,
                        'banda_tipo': None,
                        'polea_blower_marca': None,
                        'polea_blower_modelo': None,
                        'polea_motor_marca': None,
                        'polea_motor_modelo': None,
                        'tablero_electrico_marca': None,
                        'tablero_electrico_modelo': None,
                        'guarda_motor_marca': None,
                        'guarda_motor_modelo': None
                    })
                
                # Notas aleatorias
                if random.random() > 0.6:
                    base_data['notes'] = faker.paragraph()
            
            try:
                ResourceItem.objects.create(**base_data)
                print(f'Creado equipo: {base_data["code"]} - {base_data["name"]}')
            except Exception as e:
                print(f'Error creando equipo {base_data["code"]}: {str(e)}')
                continue
        
        # También cargar desde JSON si existe (manteniendo compatibilidad)
        try:
            with open('seed/equipments.json', 'r') as file:
                file_content = json.load(file)

            for equipment_data in file_content:
                # Asegurar que el serial_number sea único y se genere si no está en el JSON
                if 'serial_number' not in equipment_data or not equipment_data['serial_number']:
                    equipment_data['serial_number'] = faker.unique.bothify(text='SN-????-####')
                
                # Agregar campos por defecto para compatibilidad con el modelo actualizado
                equipment_data.setdefault('subtipo', None)
                equipment_data.setdefault('capacidad', None)
                equipment_data.setdefault('unidad_capacidad', None)
                equipment_data.setdefault('capacidad_planta', None)
                equipment_data.setdefault('motivo_reparacion', None)
                
                # Campos booleanos por defecto
                boolean_fields = [
                    'bombas_pie', 'dispensador_jabon_lavamanos', 'dispensador_papel',
                    'dispensador_jabon', 'dispensador_servilletas', 'urinales',
                    'asientos', 'bomba_bano', 'bomba_lavamanos', 'tapa_inodoro',
                    'bases_banos', 'tubo_ventilacion'
                ]
                
                for field in boolean_fields:
                    equipment_data.setdefault(field, False)
                
                try:
                    ResourceItem.objects.create(**equipment_data)
                    print(f'Creado equipo desde JSON: {equipment_data["code"]}')
                except Exception as e:
                    print(f'Error creando equipo desde JSON {equipment_data.get("code", "Unknown")}: {str(e)}')
                    continue
        
        except FileNotFoundError:
            print('Archivo seed/equipments.json no encontrado, continuando solo con datos generados')
        except Exception as e:
            print(f'Error leyendo archivo JSON: {str(e)}')
        
        print(f'Se han creado {ResourceItem.objects.count()} equipos en total')

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
        if not technicals.exists():
            print('No hay técnicos para asignar pases. Ejecute load_technical primero.')
            return

        bloques = [choice[0] for choice in PassTechnical.BLOQUE_CHOICES]

        # Seleccionar aleatoriamente técnicos que tendrán pases (entre 60% y 80%)
        selected_technicals_count = int(len(technicals) * random.uniform(0.6, 0.8))
        selected_technicals = random.sample(list(technicals), k=selected_technicals_count)


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

    def load_vehicle_passes(self, faker):
        if PassVehicle.objects.exists():
            print('Ya existen pases de vehículos')
            return True

        vehicles = Vehicle.objects.all()
        if not vehicles.exists():
            print('No hay vehículos para asignar pases. Ejecute load_vehicle primero.')
            return

        bloque_choices = [choice[0] for choice in PassVehicle.BLOQUE_CHOICES]

        for vehicle in vehicles:
            # Decidir aleatoriamente si este vehículo tendrá pases (e.g., 70% de probabilidad)
            if random.random() < 0.7:
                # Crear entre 1 y 3 pases para el vehículo
                num_passes = random.randint(1, 3)
                selected_bloques = random.sample(bloque_choices, min(num_passes, len(bloque_choices)))

                for bloque in selected_bloques:
                    fecha_caducidad = faker.date_between(start_date='+3m', end_date='+2y')
                    PassVehicle.objects.create(
                        vehicle=vehicle,
                        bloque=bloque,
                        fecha_caducidad=fecha_caducidad
                    )
        
        print(f'Se han creado {PassVehicle.objects.count()} pases de vehículos')

    def load_vehicle_certifications(self, faker):
        if CertificationVehicle.objects.exists():
            print('Ya existen certificaciones de vehículos')
            return True

        vehicles = Vehicle.objects.all()
        if not vehicles.exists():
            print('No hay vehículos para asignar certificaciones. Ejecute load_vehicle primero.')
            return

        certification_name_choices = [choice[0] for choice in CertificationVehicle.CERTIFICATION_NAME_CHOICES]

        for vehicle in vehicles:
            # Decidir aleatoriamente si este vehículo tendrá certificaciones (e.g., 80% de probabilidad)
            if random.random() < 0.8:
                # Crear entre 1 y len(certification_name_choices) certificaciones para el vehículo
                num_certifications = random.randint(1, len(certification_name_choices))
                selected_cert_names = random.sample(certification_name_choices, num_certifications)

                for cert_name in selected_cert_names:
                    date_start = faker.date_between(start_date='-2y', end_date='-1m')
                    date_end = faker.date_between(start_date='+1m', end_date='+2y')
                    description = faker.sentence() if random.random() < 0.5 else None

                    CertificationVehicle.objects.create(
                        vehicle=vehicle,
                        name=cert_name,
                        date_start=date_start,
                        date_end=date_end,
                        description=description
                    )
        
        print(f'Se han creado {CertificationVehicle.objects.count()} certificaciones de vehículos')
