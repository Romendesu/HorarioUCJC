import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import Grado, Asignatura, CursoAcademico
from apps.authy.models import Estudiante, Profesor, Decano

GRADOS = [
    {"nombre": "Ingeniería Informática", "duracion": 4},
    {"nombre": "Administración y Dirección de Empresas", "duracion": 4},
    {"nombre": "Psicología", "duracion": 4},
    {"nombre": "Derecho", "duracion": 4},
    {"nombre": "Comunicación Audiovisual", "duracion": 4},
    {"nombre": "Diseño de Interiores", "duracion": 4},
]

# Asignaturas: (nombre, descripcion, creditos, semestre, [grados_extra])
# semestre: '1' = primer semestre, '2' = segundo semestre, 'a' = anual
# grados_extra: lista de nombres de grados adicionales que comparten la asignatura
ASIGNATURAS = {
    "Ingeniería Informática": [
        ("Fundamentos de Programación",      "Introducción a la programación estructurada y orientada a objetos.", 6, "1", []),
        ("Estructuras de Datos y Algoritmos","Análisis y diseño de estructuras de datos clásicas.",               6, "2", []),
        ("Bases de Datos",                   "Diseño y gestión de bases de datos relacionales y no relacionales.", 6, "1", []),
        ("Redes de Computadores",            "Arquitectura de redes, protocolos y comunicación.",                 6, "2", []),
        ("Sistemas Operativos",              "Gestión de procesos, memoria y sistemas de archivos.",              6, "1", []),
        ("Inteligencia Artificial",          "Métodos de búsqueda, aprendizaje automático y representación.",    6, "2", []),
        ("Ingeniería del Software",          "Metodologías ágiles, UML y gestión de proyectos software.",        6, "1", []),
        ("Seguridad Informática",            "Criptografía, seguridad en redes y hacking ético.",                 4, "2", []),
        ("Cálculo",                          "Derivadas, integrales y ecuaciones diferenciales.",                 6, "a", []),
        ("Álgebra Lineal",                   "Vectores, matrices y transformaciones lineales.",                   6, "1", []),
        ("Estadística y Probabilidad",       "Distribuciones, inferencia estadística y regresión.",              6, "2", ["Psicología", "Administración y Dirección de Empresas"]),
        ("Computación en la Nube",           "Servicios cloud, contenedores y arquitecturas distribuidas.",       4, "2", []),
    ],
    "Administración y Dirección de Empresas": [
        ("Contabilidad Financiera",          "Principios de contabilidad y estados financieros.",                 6, "a", []),
        ("Marketing",                        "Estrategias de mercado, segmentación y posicionamiento.",          6, "1", ["Comunicación Audiovisual"]),
        ("Economía de la Empresa",           "Microeconomía y macroeconomía aplicada a la empresa.",             6, "a", []),
        ("Dirección de Recursos Humanos",    "Gestión del talento, selección y evaluación del desempeño.",       6, "2", []),
        ("Derecho Empresarial",              "Marco jurídico de las sociedades mercantiles.",                    4, "1", ["Derecho"]),
        ("Finanzas Corporativas",            "Valoración de empresas, inversión y financiación.",                6, "2", []),
        ("Gestión de Operaciones",           "Cadena de suministro, logística y producción.",                    6, "1", []),
        ("Emprendimiento e Innovación",      "Creación de empresas, lean startup y business model canvas.",      4, "2", ["Ingeniería Informática"]),
    ],
    "Psicología": [
        ("Psicología General",               "Bases de la percepción, atención, memoria y aprendizaje.",         6, "a", []),
        ("Neurociencia Cognitiva",           "Bases neurológicas del comportamiento y la cognición.",            6, "1", []),
        ("Psicología del Desarrollo",        "Etapas del desarrollo humano a lo largo del ciclo vital.",         6, "2", []),
        ("Psicopatología",                   "Clasificación y diagnóstico de trastornos mentales.",              6, "1", []),
        ("Técnicas de Evaluación",           "Tests psicométricos y evaluación psicológica clínica.",            6, "2", []),
        ("Psicología Social",                "Influencia social, actitudes y comportamiento en grupo.",          6, "1", []),
        ("Intervención Clínica",             "Terapias cognitivo-conductuales y de tercera generación.",         6, "2", []),
    ],
    "Derecho": [
        ("Introducción al Derecho",          "Fuentes del derecho y sistema jurídico español.",                  6, "a", []),
        ("Derecho Civil",                    "Obligaciones, contratos y derechos reales.",                       6, "a", []),
        ("Derecho Penal",                    "Teoría del delito y sistema de penas.",                            6, "1", []),
        ("Derecho Constitucional",           "Constitución española, derechos fundamentales y órganos del Estado.", 6, "2", []),
        ("Derecho Mercantil",                "Sociedades, contratos mercantiles y propiedad intelectual.",       6, "1", []),
        ("Derecho Administrativo",           "Acto administrativo, procedimiento y contratación pública.",      6, "2", []),
        ("Derecho Internacional",            "Tratados internacionales, organismos y derecho comunitario.",     4, "1", []),
        ("Derecho Procesal",                 "Proceso civil y penal, tutela judicial efectiva.",                  6, "2", []),
    ],
    "Comunicación Audiovisual": [
        ("Narrativa Audiovisual",            "Guion, estructura dramática y lenguaje cinematográfico.",          6, "a", []),
        ("Producción Audiovisual",           "Planificación, rodaje y postproducción de proyectos.",            6, "1", []),
        ("Fotografía y Composición",         "Técnica fotográfica, iluminación y composición visual.",          6, "2", ["Diseño de Interiores"]),
        ("Periodismo Digital",               "Redacción multimedia, SEO y gestión de redes sociales.",          6, "1", []),
        ("Edición de Vídeo",                 "Montaje, color grading y efectos visuales.",                      6, "2", []),
        ("Comunicación Publicitaria",        "Creatividad publicitaria, briefing y campañas integradas.",       6, "1", []),
        ("Diseño Gráfico",                   "Tipografía, identidad visual y diseño editorial.",                 4, "2", ["Diseño de Interiores"]),
        ("Podcast y Radio",                  "Producción sonora, voz y programas radiofónicos.",                 4, "1", []),
    ],
    "Diseño de Interiores": [
        ("Fundamentos del Diseño",           "Color, forma, textura y composición espacial.",                    6, "a", []),
        ("Historia del Arte y Diseño",       "Estilos, movimientos y referentes históricos del diseño.",        6, "a", []),
        ("Representación Gráfica",           "Dibujo técnico, perspectiva y planos a escala.",                  6, "1", []),
        ("Diseño de Espacios Residenciales", "Distribución, mobiliario y materialidad en viviendas.",           6, "2", []),
        ("Iluminación en Interiores",        "Técnicas de iluminación natural y artificial en espacios.",       4, "1", []),
        ("Modelado 3D y Visualización",      "Software BIM, renders y presentación de proyectos.",              6, "2", []),
        ("Sostenibilidad en el Diseño",      "Materiales ecológicos, eficiencia energética y biofilia.",        4, "1", []),
        ("Proyecto Fin de Grado",            "Desarrollo y presentación de un proyecto integral de diseño.",    12, "a", []),
    ],
}

NOMBRES = ["Alejandro", "María", "Carlos", "Laura", "José", "Ana", "Pedro", "Lucía",
           "Miguel", "Elena", "David", "Sara", "Daniel", "Carmen", "Pablo", "Paula",
           "Antonio", "Marta", "Francisco", "Isabel", "Manuel", "Sofía", "Rafael", "Claudia"]

APELLIDOS = ["García", "Martínez", "López", "Sánchez", "González", "Pérez", "Rodríguez",
             "Fernández", "Jiménez", "Ruiz", "Moreno", "Hernández", "Díaz", "Torres",
             "Ramírez", "Flores", "Vega", "Castro", "Reyes", "Ortega", "Silva", "Romero"]

DIAS = ['l', 'm', 'x', 'j', 'v']
CURSOS_ACADEMICOS = ["2022-2023", "2023-2024", "2024-2025"]


def nombre_usuario(nombre, apellido, contador):
    base = f"{nombre.lower()}.{apellido.lower().replace(' ', '')}"
    return base if contador == 0 else f"{base}{contador}"


class Command(BaseCommand):
    help = "Rellena la base de datos con datos de prueba (sin horarios)."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true",
                            help="Elimina todos los datos existentes antes de sembrar.")
        parser.add_argument("--profesores", type=int, default=12,
                            help="Número de profesores a crear (default: 12).")
        parser.add_argument("--estudiantes", type=int, default=40,
                            help="Número de estudiantes a crear (default: 40).")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("  Limpiando datos existentes...")
            Asignatura.objects.all().delete()
            Grado.objects.all().delete()
            CursoAcademico.objects.all().delete()
            Profesor.objects.all().delete()
            Estudiante.objects.all().delete()
            User.objects.filter(is_superuser=False).exclude(
                perfil_decano__isnull=False
            ).delete()
            self.stdout.write(self.style.WARNING("  Datos anteriores eliminados."))

        # ── Cursos académicos ────────────────────────────────────────────
        self.stdout.write("  Creando cursos académicos...")
        cursos = []
        for i, año in enumerate(CURSOS_ACADEMICOS):
            ca, _ = CursoAcademico.objects.get_or_create(
                año=año,
                defaults={"estado": "activo" if i == len(CURSOS_ACADEMICOS) - 1 else "inactivo"},
            )
            cursos.append(ca)
        self.stdout.write(self.style.SUCCESS(f"    {len(cursos)} cursos académicos."))

        # ── Grados y asignaturas ─────────────────────────────────────────
        self.stdout.write("  Creando grados y asignaturas...")
        grados_creados = {}
        for data in GRADOS:
            grado, _ = Grado.objects.get_or_create(
                nombre=data["nombre"],
                defaults={"duracion": data["duracion"]},
            )
            grados_creados[data["nombre"]] = grado

        total_asig = 0
        for grado_nombre, asigs in ASIGNATURAS.items():
            grado_principal = grados_creados.get(grado_nombre)
            if not grado_principal:
                continue
            for nombre, desc, creditos, semestre, grados_extra in asigs:
                asig, created = Asignatura.objects.get_or_create(
                    nombre=nombre,
                    defaults={"descripcion": desc, "creditos": creditos, "semestre": semestre},
                )
                # Asignar grados (principal + extras)
                todos = [grado_principal] + [
                    grados_creados[g] for g in grados_extra if g in grados_creados
                ]
                asig.grados.add(*todos)
                if created:
                    total_asig += 1

        self.stdout.write(self.style.SUCCESS(
            f"    {len(grados_creados)} grados, {total_asig} asignaturas nuevas."
        ))

        # ── Profesores ───────────────────────────────────────────────────
        self.stdout.write(f"  Creando {options['profesores']} profesores...")
        todas_asigs = list(Asignatura.objects.all())
        usados = set(User.objects.values_list("username", flat=True))
        creados_prof = 0
        for _ in range(options["profesores"]):
            nombre = random.choice(NOMBRES)
            apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            contador = 0
            username = nombre_usuario(nombre, apellido.split()[0], contador)
            while username in usados:
                contador += 1
                username = nombre_usuario(nombre, apellido.split()[0], contador)
            usados.add(username)

            user = User.objects.create_user(
                username=username,
                email=f"{username}@ucjc.edu",
                password="profesor123",
                first_name=nombre,
                last_name=apellido,
            )
            dias_disp = random.sample(DIAS, random.randint(3, 5))
            prof = Profesor.objects.create(
                user=user,
                disponibilidad=sorted(dias_disp, key=lambda d: DIAS.index(d)),
            )
            # Asignar entre 2 y 4 asignaturas aleatorias
            if todas_asigs:
                asigs_prof = random.sample(todas_asigs, min(random.randint(2, 4), len(todas_asigs)))
                prof.asignaturas.set(asigs_prof)
            creados_prof += 1
        self.stdout.write(self.style.SUCCESS(f"    {creados_prof} profesores creados."))

        # ── Estudiantes ──────────────────────────────────────────────────
        self.stdout.write(f"  Creando {options['estudiantes']} estudiantes...")
        creados_est = 0
        for _ in range(options["estudiantes"]):
            nombre = random.choice(NOMBRES)
            apellido = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            contador = 0
            username = nombre_usuario(nombre, apellido.split()[0], contador)
            while username in usados:
                contador += 1
                username = nombre_usuario(nombre, apellido.split()[0], contador)
            usados.add(username)

            grado = random.choice(list(grados_creados.values()))
            anio = random.randint(1, grado.duracion)
            user = User.objects.create_user(
                username=username,
                email=f"{username}@ucjc.edu",
                password="alumno123",
                first_name=nombre,
                last_name=apellido,
            )
            Estudiante.objects.create(user=user, anio=anio, carrera=grado.nombre)
            creados_est += 1
        self.stdout.write(self.style.SUCCESS(f"    {creados_est} estudiantes creados."))

        # ── Resumen ──────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seed completado:"))
        self.stdout.write(f"  Cursos académicos : {CursoAcademico.objects.count()}")
        self.stdout.write(f"  Grados            : {Grado.objects.count()}")
        self.stdout.write(f"  Asignaturas       : {Asignatura.objects.count()}")
        self.stdout.write(f"  Profesores        : {Profesor.objects.count()}")
        self.stdout.write(f"  Estudiantes       : {Estudiante.objects.count()}")
        self.stdout.write("")
        self.stdout.write("  Contraseñas por defecto:")
        self.stdout.write("    Profesores  → profesor123")
        self.stdout.write("    Estudiantes → alumno123")
