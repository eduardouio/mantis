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

        # Crear equipos basados en la documentación usando campos básicos
        self.create_bateria_sanitaria_hombre(faker)
        self.create_bateria_sanitaria_mujer(faker)
        self.create_plantas_tratamiento_agua(faker)
        self.create_plantas_tratamiento_agua_residual(faker)
        self.create_tanques_agua_cruda(faker)
        self.create_tanques_agua_residual(faker)
        self.create_lavamanos(faker)
        self.create_camper_bano(faker)
        self.create_estacion_urinario(faker)
        self.create_bombas(faker)
        
        print(f'Se han creado {ResourceItem.objects.count()} equipos en total')

    def create_bateria_sanitaria_hombre(self, faker):
        """Crear baterías sanitarias para hombres"""
        for i in range(5):
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Batería Sanitaria Hombre {i+1}",
                type='EQUIPO',
                subtype='BATERIA SANITARIA HOMBRE',
                brand=faker.random_element(['Portatil Pro', 'SaniTech', 'EcoPorta']),
                model=f'BSH-{faker.random_number(3)}',
                code=f'BSH-{str(i+1).zfill(3)}',
                serial_number=f'SN-BSH-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(200, 250),
                width=faker.random_int(100, 150),
                depth=faker.random_int(100, 150),
                weight=faker.random_int(80, 120),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(15000, 25000),
                # Usar los nombres de campos del modelo
                paper_dispenser=faker.boolean(),
                soap_dispenser=faker.boolean(),
                napkin_dispenser=faker.boolean(),
                urinals=faker.boolean(),
                seats=faker.boolean(),
                toilet_pump=faker.boolean(),
                sink_pump=faker.boolean(),
                toilet_lid=faker.boolean(),
                bathroom_bases=faker.boolean(),
                ventilation_pipe=faker.boolean(),
                notes=f'Batería sanitaria equipada con accesorios varios',
                is_active=True
            )

    def create_bateria_sanitaria_mujer(self, faker):
        """Crear baterías sanitarias para mujeres"""
        for i in range(5):
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Batería Sanitaria Mujer {i+1}",
                type='EQUIPO',
                subtype='BATERIA SANITARIA MUJER',
                brand=faker.random_element(['Portatil Pro', 'SaniTech', 'EcoPorta']),
                model=f'BSM-{faker.random_number(3)}',
                code=f'BSM-{str(i+1).zfill(3)}',
                serial_number=f'SN-BSM-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(200, 250),
                width=faker.random_int(100, 150),
                depth=faker.random_int(100, 150),
                weight=faker.random_int(80, 120),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(15000, 25000),
                # Usar los nombres de campos del modelo (sin urinales para mujeres)
                paper_dispenser=faker.boolean(),
                soap_dispenser=faker.boolean(),
                napkin_dispenser=faker.boolean(),
                urinals=False,
                seats=faker.boolean(),
                toilet_pump=faker.boolean(),
                sink_pump=faker.boolean(),
                toilet_lid=faker.boolean(),
                bathroom_bases=faker.boolean(),
                ventilation_pipe=faker.boolean(),
                notes=f'Batería sanitaria equipada con accesorios varios',
                is_active=True
            )

    def create_plantas_tratamiento_agua(self, faker):
        """Crear plantas de tratamiento de agua"""
        capacidades = ['10M3', '15M3', '25M3']
        for i in range(3):
            capacidad = faker.random_element(capacidades)
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Planta Tratamiento Agua {capacidad} - {i+1}",
                type='EQUIPO',
                subtype='PLANTA DE TRATAMIENTO DE AGUA',
                brand=faker.random_element(['AquaTech', 'WaterPro', 'HydroClean']),
                model=f'PTA-{faker.random_number(3)}',
                code=f'PTA-{str(i+1).zfill(3)}',
                serial_number=f'SN-PTA-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(150, 200),
                width=faker.random_int(200, 300),
                depth=faker.random_int(200, 300),
                weight=faker.random_int(500, 800),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(80000, 120000),
                # Usar los nombres de campos del modelo
                blower_brand=faker.company(),
                blower_model=faker.bothify(text='BLW-##??'),
                engine_brand=faker.company(),
                engine_model=faker.bothify(text='MOT-##??'),
                belt_brand=faker.company(),
                belt_model=faker.bothify(text='BND-##??'),
                belt_type=faker.random_element(['A', 'B']),
                blower_pulley_brand=faker.company(),
                blower_pulley_model=faker.bothify(text='PLB-##??'),
                motor_pulley_brand=faker.company(),
                motor_pulley_model=faker.bothify(text='PLM-##??'),
                electrical_panel_brand=faker.company(),
                electrical_panel_model=faker.bothify(text='TBE-##??'),
                motor_guard_brand=faker.company(),
                motor_guard_model=faker.bothify(text='GDM-##??'),
                notes=f'Planta de tratamiento de agua de {capacidad}',
                is_active=True
            )

    def create_plantas_tratamiento_agua_residual(self, faker):
        """Crear plantas de tratamiento de agua residual"""
        capacidades = ['10M3', '15M3', '25M3']
        for i in range(3):
            capacidad = faker.random_element(capacidades)
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Planta Tratamiento Agua Residual {capacidad} - {i+1}",
                type='EQUIPO',
                subtype='PLANTA DE TRATAMIENTO DE AGUA RESIDUAL',
                brand=faker.random_element(['AquaTech', 'WaterPro', 'HydroClean']),
                model=f'PTAR-{faker.random_number(3)}',
                code=f'PTAR-{str(i+1).zfill(3)}',
                serial_number=f'SN-PTAR-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(150, 200),
                width=faker.random_int(200, 300),
                depth=faker.random_int(200, 300),
                weight=faker.random_int(500, 800),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(80000, 120000),
                # Campo obligatorio para este tipo
                plant_capacity=capacidad,
                # Usar los nombres de campos del modelo
                blower_brand=faker.company(),
                blower_model=faker.bothify(text='BLW-##??'),
                engine_brand=faker.company(),
                engine_model=faker.bothify(text='MOT-##??'),
                belt_brand=faker.company(),
                belt_model=faker.bothify(text='BND-##??'),
                belt_type=faker.random_element(['A', 'B']),
                blower_pulley_brand=faker.company(),
                blower_pulley_model=faker.bothify(text='PLB-##??'),
                motor_pulley_brand=faker.company(),
                motor_pulley_model=faker.bothify(text='PLM-##??'),
                electrical_panel_brand=faker.company(),
                electrical_panel_model=faker.bothify(text='TBE-##??'),
                motor_guard_brand=faker.company(),
                motor_guard_model=faker.bothify(text='GDM-##??'),
                notes=f'Planta de tratamiento de agua residual de {capacidad}',
                is_active=True
            )

    def create_tanques_agua_cruda(self, faker):
        """Crear tanques de almacenamiento de agua cruda"""
        capacidades = [500, 750, 1000, 1500, 2000]
        for i in range(4):
            capacidad = faker.random_element(capacidades)
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Tanque Agua Cruda {capacidad} gal - {i+1}",
                type='EQUIPO',
                subtype='TANQUES DE ALMACENAMIENTO AGUA CRUDA',
                brand=faker.random_element(['TankTech', 'AquaStore', 'WaterTank']),
                model=f'TAC-{faker.random_number(3)}',
                code=f'TAC-{str(i+1).zfill(3)}',
                serial_number=f'SN-TAC-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(180, 220),
                width=faker.random_int(120, 180),
                depth=faker.random_int(120, 180),
                weight=faker.random_int(100, 200),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(20000, 35000),
                # Usar el nombre correcto del campo
                capacity_gallons=capacidad,
                # Campos específicos para tanques
                blower_brand=faker.company(),
                blower_model=faker.bothify(text='BLW-##??'),
                engine_brand=faker.company(),
                engine_model=faker.bothify(text='MOT-##??'),
                belt_brand=faker.company(),
                belt_model=faker.bothify(text='BND-##??'),
                belt_type=faker.random_element(['A', 'B']),
                blower_pulley_brand=faker.company(),
                blower_pulley_model=faker.bothify(text='PLB-##??'),
                motor_pulley_brand=faker.company(),
                motor_pulley_model=faker.bothify(text='PLM-##??'),
                electrical_panel_brand=faker.company(),
                electrical_panel_model=faker.bothify(text='TBE-##??'),
                motor_guard_brand=faker.company(),
                motor_guard_model=faker.bothify(text='GDM-##??'),
                notes=f'Tanque de almacenamiento de agua cruda con capacidad de {capacidad} galones',
                is_active=True
            )

    def create_tanques_agua_residual(self, faker):
        """Crear tanques de almacenamiento de agua residual"""
        capacidades = [500, 750, 1000, 1500, 2000]
        for i in range(4):
            capacidad = faker.random_element(capacidades)
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Tanque Agua Residual {capacidad} gal - {i+1}",
                type='EQUIPO',
                subtype='TANQUES DE ALMACENAMIENTO AGUA RESIDUAL',
                brand=faker.random_element(['TankTech', 'AquaStore', 'WaterTank']),
                model=f'TAR-{faker.random_number(3)}',
                code=f'TAR-{str(i+1).zfill(3)}',
                serial_number=f'SN-TAR-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(180, 220),
                width=faker.random_int(120, 180),
                depth=faker.random_int(120, 180),
                weight=faker.random_int(100, 200),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(20000, 35000),
                # Usar el nombre correcto del campo
                capacity_gallons=capacidad,
                # Campos específicos para tanques
                blower_brand=faker.company(),
                blower_model=faker.bothify(text='BLW-##??'),
                engine_brand=faker.company(),
                engine_model=faker.bothify(text='MOT-##??'),
                belt_brand=faker.company(),
                belt_model=faker.bothify(text='BND-##??'),
                belt_type=faker.random_element(['A', 'B']),
                blower_pulley_brand=faker.company(),
                blower_pulley_model=faker.bothify(text='PLB-##??'),
                motor_pulley_brand=faker.company(),
                motor_pulley_model=faker.bothify(text='PLM-##??'),
                electrical_panel_brand=faker.company(),
                electrical_panel_model=faker.bothify(text='TBE-##??'),
                motor_guard_brand=faker.company(),
                motor_guard_model=faker.bothify(text='GDM-##??'),
                notes=f'Tanque de almacenamiento de agua residual con capacidad de {capacidad} galones',
                is_active=True
            )

    def create_lavamanos(self, faker):
        """Crear lavamanos"""
        for i in range(6):
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Lavamanos {i+1}",
                type='EQUIPO',
                subtype='LAVAMANOS',
                brand=faker.random_element(['WashTech', 'CleanHands', 'SaniWash']),
                model=f'LM-{faker.random_number(3)}',
                code=f'LM-{str(i+1).zfill(3)}',
                serial_number=f'SN-LM-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(80, 120),
                width=faker.random_int(60, 100),
                depth=faker.random_int(40, 80),
                weight=faker.random_int(15, 30),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(5000, 10000),
                # Usar los nombres de campos del modelo
                foot_pumps=faker.boolean(),
                sink_soap_dispenser=faker.boolean(),
                paper_towels=faker.boolean(),
                notes=f'Lavamanos con accesorios varios',
                is_active=True
            )

    def create_camper_bano(self, faker):
        """Crear camper baño"""
        for i in range(3):
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Camper Baño {i+1}",
                type='EQUIPO',
                subtype='CAMPER BAÑO',
                brand=faker.random_element(['CamperTech', 'MobileBath', 'PortaCamper']),
                model=f'CB-{faker.random_number(3)}',
                code=f'CB-{str(i+1).zfill(3)}',
                serial_number=f'SN-CB-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(250, 300),
                width=faker.random_int(200, 250),
                depth=faker.random_int(150, 200),
                weight=faker.random_int(200, 300),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(40000, 60000),
                # Usar los nombres de campos del modelo (igual que batería sanitaria hombre)
                paper_dispenser=faker.boolean(),
                soap_dispenser=faker.boolean(),
                napkin_dispenser=faker.boolean(),
                urinals=faker.boolean(),
                seats=faker.boolean(),
                toilet_pump=faker.boolean(),
                sink_pump=faker.boolean(),
                toilet_lid=faker.boolean(),
                bathroom_bases=faker.boolean(),
                ventilation_pipe=faker.boolean(),
                notes=f'Camper baño equipado con accesorios varios',
                is_active=True
            )

    def create_estacion_urinario(self, faker):
        """Crear estaciones cuádruples de urinario"""
        for i in range(2):
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Estación Cuádruple Urinario {i+1}",
                type='EQUIPO',
                subtype='ESTACION CUADRUPLE URINARIO',
                brand=faker.random_element(['UriTech', 'QuadStation', 'MultiUri']),
                model=f'ECU-{faker.random_number(3)}',
                code=f'ECU-{str(i+1).zfill(3)}',
                serial_number=f'SN-ECU-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(180, 220),
                width=faker.random_int(300, 400),
                depth=faker.random_int(80, 120),
                weight=faker.random_int(80, 120),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(25000, 40000),
                notes='Estación cuádruple de urinarios',
                is_active=True
            )

    def create_bombas(self, faker):
        """Crear bombas"""
        for i in range(4):
            status = faker.random_element(['DISPONIBLE', 'RENTADO', 'EN REPARACION', 'FUERA DE SERVICIO'])
            ResourceItem.objects.create(
                name=f"Bomba {i+1}",
                type='EQUIPO',
                # No hay subtipo específico para bombas en TYPE_EQUIPMENT, usar None
                subtype=None,
                brand=faker.random_element(['PumpTech', 'AquaPump', 'FlowMaster']),
                model=f'B-{faker.random_number(3)}',
                code=f'B-{str(i+1).zfill(3)}',
                serial_number=f'SN-B-{faker.unique.numerify("######")}',
                date_purchase=faker.date_between(start_date='-5y', end_date='-1y'),
                height=faker.random_int(40, 80),
                width=faker.random_int(30, 60),
                depth=faker.random_int(30, 60),
                weight=faker.random_int(10, 25),
                status=status,
                repair_reason=faker.sentence() if status == 'EN REPARACION' else None,
                base_price=faker.random_int(8000, 15000),
                notes='Bomba de agua',
                is_active=True
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
        if not technicals.exists():
            print('No hay técnicos para asignar pases. Ejecute load_technical primero.')
            return

        bloques = [choice[0] for choice in PassTechnical.BLOQUE_CHOICES]

        # Seleccionar aleatoriamente técnicos que tendrán pases (entre 60% y 80%)
        selected_technicals_count = int(
            len(technicals) * random.uniform(0.6, 0.8))
        selected_technicals = random.sample(
            list(technicals), k=selected_technicals_count)

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
                selected_bloques = random.sample(
                    bloque_choices, min(num_passes, len(bloque_choices)))

                for bloque in selected_bloques:
                    fecha_caducidad = faker.date_between(
                        start_date='+3m', end_date='+2y')
                    PassVehicle.objects.create(
                        vehicle=vehicle,
                        bloque=bloque,
                        fecha_caducidad=fecha_caducidad
                    )

        print(
            f'Se han creado {PassVehicle.objects.count()} pases de vehículos')

    def load_vehicle_certifications(self, faker):
        if CertificationVehicle.objects.exists():
            print('Ya existen certificaciones de vehículos')
            return True

        vehicles = Vehicle.objects.all()
        if not vehicles.exists():
            print(
                'No hay vehículos para asignar certificaciones. Ejecute load_vehicle primero.')
            return

        certification_name_choices = [
            choice[0] for choice in CertificationVehicle.CERTIFICATION_NAME_CHOICES]

        for vehicle in vehicles:
            # Decidir aleatoriamente si este vehículo tendrá certificaciones (e.g., 80% de probabilidad)
            if random.random() < 0.8:
                # Crear entre 1 y len(certification_name_choices) certificaciones para el vehículo
                num_certifications = random.randint(
                    1, len(certification_name_choices))
                selected_cert_names = random.sample(
                    certification_name_choices, num_certifications)

                for cert_name in selected_cert_names:
                    date_start = faker.date_between(
                        start_date='-2y', end_date='-1m')
                    date_end = faker.date_between(
                        start_date='+1m', end_date='+2y')
                    description = faker.sentence() if random.random() < 0.5 else None

                    CertificationVehicle.objects.create(
                        vehicle=vehicle,
                        name=cert_name,
                        date_start=date_start,
                        date_end=date_end,
                        description=description
                    )

        print(
            f'Se han creado {CertificationVehicle.objects.count()} certificaciones de vehículos')
        selected_technicals = random.sample(
            list(technicals), k=selected_technicals_count)

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
                selected_bloques = random.sample(
                    bloque_choices, min(num_passes, len(bloque_choices)))

                for bloque in selected_bloques:
                    fecha_caducidad = faker.date_between(
                        start_date='+3m', end_date='+2y')
                    PassVehicle.objects.create(
                        vehicle=vehicle,
                        bloque=bloque,
                        fecha_caducidad=fecha_caducidad
                    )

        print(
            f'Se han creado {PassVehicle.objects.count()} pases de vehículos')

    def load_vehicle_certifications(self, faker):
        if CertificationVehicle.objects.exists():
            print('Ya existen certificaciones de vehículos')
            return True

        vehicles = Vehicle.objects.all()
        if not vehicles.exists():
            print(
                'No hay vehículos para asignar certificaciones. Ejecute load_vehicle primero.')
            return

        certification_name_choices = [
            choice[0] for choice in CertificationVehicle.CERTIFICATION_NAME_CHOICES]

        for vehicle in vehicles:
            # Decidir aleatoriamente si este vehículo tendrá certificaciones (e.g., 80% de probabilidad)
            if random.random() < 0.8:
                # Crear entre 1 y len(certification_name_choices) certificaciones para el vehículo
                num_certifications = random.randint(
                    1, len(certification_name_choices))
                selected_cert_names = random.sample(
                    certification_name_choices, num_certifications)

                for cert_name in selected_cert_names:
                    date_start = faker.date_between(
                        start_date='-2y', end_date='-1m')
                    date_end = faker.date_between(
                        start_date='+1m', end_date='+2y')
                    description = faker.sentence() if random.random() < 0.5 else None

                    CertificationVehicle.objects.create(
                        vehicle=vehicle,
                        name=cert_name,
                        date_start=date_start,
                        date_end=date_end,
                        description=description
                    )

        print(
            f'Se han creado {CertificationVehicle.objects.count()} certificaciones de vehículos')
