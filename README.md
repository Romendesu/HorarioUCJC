# 📅 HorarioUCJC

Sistema web de generación de horarios académicos para la Universidad Camilo José Cela (UCJC). Este proyecto tiene como objetivo automatizar y facilitar la creación de horarios para docentes y asignaturas, evitando conflictos de disponibilidad y optimizando la distribución de clases.

> ⚠️ **Estado del proyecto:** En desarrollo. Actualmente se encuentran implementadas las **vistas (diseño UI)** y el **sistema de autenticación**. El motor de generación automática de horarios está pendiente de implementación.

---

## ✨ Funcionalidades implementadas

- 🔐 **Autenticación de usuarios** — Registro, inicio de sesión y gestión de sesiones.
- 🎨 **Vistas y diseño de la interfaz** — Todas las pantallas del sistema están maquetadas y funcionales a nivel visual.

## 🚧 Funcionalidades pendientes

- ⚙️ Motor de generación automática de horarios
- 📋 Gestión de asignaturas, aulas y docentes
- 🔁 Detección y resolución de conflictos de horario
- 📤 Exportación de horarios generados

---

## 🛠️ Tecnologías utilizadas

- **Frontend:** HTML, CSS, JavaScript, TailwindCSS
- **Backend:** Django
- **Base de datos:** PostgreSQL
- **Autenticación:** django.contrib.auth

---

## 🚀 Instalación y ejecución

### Requisitos previos

- *Gestor de Node (npm, pnpm...), Gestor de Python (p.ej: uv, pip, pipx...)*
- *PostgreSQL)*

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Romendesu/HorarioUCJC.git
cd HorarioUCJC

# 2. Instalar dependencias

pip install -r requirements.txt
# o
composer install

# 3. Configurar variables de entorno
cp .env.example .env
# Edita el archivo .env con tus credenciales de base de datos + secret key de Django

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Iniciar el servidor de desarrollo
python manage.py runserver

```

---

## 📁 Estructura del proyecto

```
HorarioUCJC/
├── apps/                  # Aplicaciones del proyectp
├── horario/               # Configuración + enrutado
├── static/                # Archivos estáticos
├── templates/             # Templates del proyecto
├── theme/                 # TailwindCSS
├── .env.example           # Ejemplo de configuración
├── .gitignore             # Ignorar cache + archivos secretos
├── manage.py              # Ejecucción del proyecto
├── requirements.txt       # Dependencias de Python
├── package.json           # Dependencias de Node
└── README.md
```


---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas colaborar:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad: `git checkout -b feature/nombre-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m "feat: descripción del cambio"`
4. Sube los cambios: `git push origin feature/nombre-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más información.

---

## 👤 Autor

**Romendesu**
- GitHub: [@Romendesu](https://github.com/Romendesu)