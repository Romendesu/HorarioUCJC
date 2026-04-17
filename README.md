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

> *(Actualiza esta sección con el stack real del proyecto)*

- **Frontend:** HTML, CSS, JavaScript *(o el framework utilizado)*
- **Backend:** *(framework/lenguaje utilizado)*
- **Base de datos:** *(base de datos utilizada)*
- **Autenticación:** *(sistema de autenticación utilizado)*

---

## 🚀 Instalación y ejecución

### Requisitos previos

- *(Ej: Node.js v18+, Python 3.10+, PHP 8+, etc.)*
- *(Ej: MySQL / PostgreSQL / SQLite)*

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Romendesu/HorarioUCJC.git
cd HorarioUCJC

# 2. Instalar dependencias
# (ajusta según el gestor de paquetes de tu proyecto)
npm install
# o
pip install -r requirements.txt
# o
composer install

# 3. Configurar variables de entorno
cp .env.example .env
# Edita el archivo .env con tus credenciales de base de datos

# 4. Ejecutar migraciones
# (ajusta según tu stack)
php artisan migrate
# o
python manage.py migrate

# 5. Iniciar el servidor de desarrollo
npm run dev
# o
php artisan serve
# o
python manage.py runserver
```

---

## 📁 Estructura del proyecto

```
HorarioUCJC/
├── src/                  # Código fuente principal
├── public/               # Archivos públicos / assets
├── views/                # Vistas y plantillas
├── routes/               # Definición de rutas
├── controllers/          # Lógica de controladores
├── models/               # Modelos de datos
├── .env.example          # Ejemplo de configuración
└── README.md
```

> *(Ajusta la estructura según la organización real del proyecto)*

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