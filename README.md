# HorarioUCJC

Sistema web de generación y gestión de horarios académicos para la Universidad Camilo José Cela (UCJC). Automatiza la creación de horarios por titulación, curso y semestre, aplicando restricciones duras de disponibilidad y detección de conflictos en tiempo real.

---

## Funcionalidades implementadas

### Autenticación y roles (RBAC)
- Inicio de sesión con credenciales cifradas
- Tres roles: **Decano**, **Profesor** y **Estudiante**
- Redirección automática al dashboard correspondiente según rol

### Panel del Decano

**Gestión de catálogo**
- Grados con duración configurable
- Asignaturas con soporte M2M (una asignatura puede pertenecer a varios grados), semestre (`1`, `2`, `a` anual) y créditos ECTS
- Cursos académicos con estado activo/inactivo
- Profesores con disponibilidad semanal y asignaturas asignadas (M2M)
- Estudiantes con grado y año de carrera

**Generación automática de horarios**
- Motor de reglas configurable por el decano: hora de inicio, duración de sesión y número de franjas
- Regla fija: **2 sesiones semanales por asignatura**, en días distintos
- Último curso del grado: franja de tarde (15:00) aplicada automáticamente
- Filtrado de asignaturas por semestre del horario (+ anuales)
- Hard constraints: sin colisión de profesor, sin colisión de aula, sin doble sesión del grupo en el mismo slot
- Soft constraint: respeto de la disponibilidad declarada del profesor; si no hay candidato disponible, la sesión se crea sin profesor y se emite advertencia
- Fallback: si ningún profesor está asignado a la asignatura, se avisa y se usa cualquier disponible

**Edición manual de horarios (estado borrador/revisión)**
- Grid semanal interactivo con **drag & drop** para mover sesiones entre franjas y días
- Detección de conflictos en tiempo real durante el arrastre: alerta amarilla con descripción del conflicto (grupo ocupado, profesor ocupado en este horario, profesor ocupado en otro horario)
- Soltar en slot con conflicto está bloqueado; solo se permite en slots verdes libres
- Panel lateral "Posibilidades por sesión": muestra cuántos slots sin conflicto tiene disponibles cada sesión, con indicador de color (rojo/ámbar/verde) y barra proporcional
- Añadir sesión manualmente con validación de conflictos en tiempo real en el modal (botón deshabilitado si hay conflicto)
- Eliminar sesiones directamente desde el grid o desde la lista
- Workflow de estados: **Borrador → Revisión → Aprobado / Rechazado**
- Validación técnica: comprueba que cada asignatura del semestre tenga exactamente 2 sesiones, sin colisiones de profesor ni de aula

**Usuarios**
- Crear, editar y eliminar profesores y estudiantes
- Asignar disponibilidad semanal y asignaturas a profesores desde el panel

### Vista del Estudiante
- Calendario semanal con grid dinámico que deriva las franjas horarias de las sesiones reales
- Filtra el horario aprobado por grado **y** año del estudiante (no mezcla cursos)
- Vista de hoy con próxima sesión y horas lectivas
- Vista móvil adaptada (lista diaria) y escritorio (grid semanal)

### Vista del Profesor
- Calendario semanal con todas sus sesiones en el curso académico activo

---

## Datos de prueba

El proyecto incluye un comando de seeding para poblar la base de datos sin horarios:

```bash
python manage.py seed                        # datos por defecto
python manage.py seed --flush                # limpia antes de sembrar
python manage.py seed --profesores 20 --estudiantes 80
```

Crea: 3 cursos académicos · 6 grados · ~51 asignaturas (con semestre y grados M2M) · N profesores (con 2-4 asignaturas aleatorias) · N estudiantes.

Contraseñas por defecto: profesores → `profesor123` / estudiantes → `alumno123`

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Django 5 + PostgreSQL |
| Frontend | Tailwind CSS v4 + Alpine.js |
| Autenticación | django.contrib.auth |
| CSS build | django-tailwind (`python manage.py tailwind build`) |
| Datos de prueba | Management command `seed` |

---

## Instalación

### Requisitos previos

- Python 3.12+ con gestor de entornos (uv, pip…)
- Node.js con npm o pnpm
- PostgreSQL

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Romendesu/HorarioUCJC.git
cd HorarioUCJC

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Instalar dependencias Node (Tailwind)
npm install

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales de base de datos y SECRET_KEY de Django

# 5. Aplicar migraciones
python manage.py migrate

# 6. Compilar estilos
python manage.py tailwind build

# 7. (Opcional) Poblar con datos de prueba
python manage.py seed --flush

# 8. Iniciar el servidor
python manage.py runserver
```

Para crear un usuario decano:

```bash
python manage.py createsuperuser
# Luego, desde el admin de Django, crear un objeto Decano vinculado al superusuario
```

---

## Estructura del proyecto

```
HorarioUCJC/
├── apps/
│   ├── core/           # Modelos principales (Grado, Asignatura, Horario, SesionHorario)
│   │   ├── models.py
│   │   ├── services.py # Motor de generación y validación de horarios
│   │   └── management/commands/seed.py
│   ├── authy/          # Modelos de usuario (Estudiante, Profesor, Decano)
│   └── dashboard/      # Vistas y URLs del panel de control
├── horario/            # Configuración Django + enrutado raíz
├── templates/          # Plantillas HTML por rol y sección
├── theme/              # Configuración y fuente de Tailwind CSS v4
├── .env.example
├── manage.py
├── requirements.txt
└── package.json
```

---

## Contribuciones

1. Haz un fork del repositorio
2. Crea una rama: `git checkout -b feature/nombre-funcionalidad`
3. Commit: `git commit -m "feat: descripción del cambio"`
4. Push: `git push origin feature/nombre-funcionalidad`
5. Abre un Pull Request

---

## Autor

**Romendesu** — [@Romendesu](https://github.com/Romendesu)
