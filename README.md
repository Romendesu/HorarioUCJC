# HorarioUCJC
Repositorio para el trabajo Horario UCJC por parte de Rodrigo Moreno Menéndez en la asignatura Desarrollo de Software y Sistemas.

# Esquema de Base de Datos Tipado (PostgreSQL)

## 1. Núcleo Académico

### Titulacion
- id: UUID (PK)
- nombre: VARCHAR(150) NOT NULL
- descripcion: TEXT

### CursoAcademico
- id: UUID (PK)
- anio_inicio: INT NOT NULL
- anio_fin: INT NOT NULL
- estado: VARCHAR(20) CHECK (estado IN ('activo', 'cerrado'))

### Curso
- id: UUID (PK)
- numero: INT NOT NULL
- titulacion_id: INT (FK)

### Asignatura
- id: UUID (PK)
- codigo: VARCHAR(20) UNIQUE NOT NULL
- nombre: VARCHAR(150) NOT NULL
- horas_totales: INT NOT NULL
- titulacion_id: INT (FK)
- es_transversal: BOOLEAN DEFAULT FALSE

### Grupo
- id: UUID (PK)
- nombre: VARCHAR(20)
- tipo: VARCHAR(20) CHECK (tipo IN ('teoria', 'practica', 'laboratorio'))
- curso_id: INT (FK)

---

## 2. Usuarios y Roles

### Usuario
- id: SERIAL (PK)
- nombre: VARCHAR(150) NOT NULL
- email: VARCHAR(150) UNIQUE NOT NULL
- password_hash: TEXT NOT NULL
- activo: BOOLEAN DEFAULT TRUE

### Rol
- id: SERIAL (PK)
- nombre: VARCHAR(50) UNIQUE NOT NULL

### UsuarioRol
- usuario_id: INT (FK)
- rol_id: INT (FK)
- PRIMARY KEY (usuario_id, rol_id)

---

## 3. Profesorado

### Profesor
- id: SERIAL (PK)
- usuario_id: INT (FK)
- departamento: VARCHAR(100)

### AsignacionDocente
- id: SERIAL (PK)
- profesor_id: INT (FK)
- asignatura_id: INT (FK)
- es_titular: BOOLEAN DEFAULT TRUE
- area_conocimiento: VARCHAR(100)

---

## 4. Disponibilidad del Profesorado

### DisponibilidadProfesor
- id: SERIAL (PK)
- profesor_id: INT (FK)
- dia_semana: SMALLINT CHECK (dia_semana BETWEEN 1 AND 7)
- hora_inicio: TIME NOT NULL
- hora_fin: TIME NOT NULL
- tipo: VARCHAR(20) CHECK (tipo IN ('preferente', 'bloqueado'))

### HistorialDisponibilidad
- id: SERIAL (PK)
- profesor_id: INT (FK)
- cambios_json: JSONB
- timestamp: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 5. Infraestructura

### Aula
- id: SERIAL (PK)
- nombre: VARCHAR(50)
- capacidad: INT
- tipo: VARCHAR(50)

---

## 6. Configuración Académica

### ConfiguracionAcademica
- id: SERIAL (PK)
- curso_academico_id: INT (FK)
- parametros_json: JSONB

### FranjaHoraria
- id: SERIAL (PK)
- hora_inicio: TIME NOT NULL
- hora_fin: TIME NOT NULL

### DiaLectivo
- id: SERIAL (PK)
- nombre: VARCHAR(20)

---

## 7. Horarios

### Horario
- id: SERIAL (PK)
- titulacion_id: INT (FK)
- curso_id: INT (FK)
- curso_academico_id: INT (FK)
- estado: VARCHAR(20) CHECK (estado IN ('borrador', 'revision', 'aprobado', 'rechazado'))

### Sesion
- id: SERIAL (PK)
- horario_id: INT (FK)
- asignatura_id: INT (FK)
- profesor_id: INT (FK)
- grupo_id: INT (FK)
- aula_id: INT (FK)
- dia_semana: SMALLINT CHECK (dia_semana BETWEEN 1 AND 7)
- franja_horaria_id: INT (FK)

---

## 8. Auditoría y Logs

### Auditoria
- id: SERIAL (PK)
- usuario_id: INT (FK)
- accion: VARCHAR(100)
- entidad: VARCHAR(100)
- valor_anterior: JSONB
- valor_nuevo: JSONB
- timestamp: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### LogSistema
- id: SERIAL (PK)
- nivel: VARCHAR(10) CHECK (nivel IN ('INFO', 'WARN', 'ERROR', 'CRITICAL'))
- mensaje: TEXT
- user_id: INT (FK)
- session_id: VARCHAR(100)
- error_code: VARCHAR(50)
- timestamp: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 9. Notificaciones

### Notificacion
- id: SERIAL (PK)
- usuario_id: INT (FK)
- tipo: VARCHAR(20) CHECK (tipo IN ('info', 'warning', 'error'))
- mensaje: TEXT
- leido: BOOLEAN DEFAULT FALSE
- timestamp: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 10. Estudiantes y Matrícula

### Estudiante
- id: SERIAL (PK)
- usuario_id: INT (FK)
- titulacion_id: INT (FK)

### Matricula
- id: SERIAL (PK)
- estudiante_id: INT (FK)
- asignatura_id: INT (FK)
- curso_academico_id: INT (FK)

---

## 11. Motor de Reglas

### Regla
- id: SERIAL (PK)
- tipo: VARCHAR(10) CHECK (tipo IN ('hard', 'soft'))
- descripcion: TEXT
- activa: BOOLEAN DEFAULT TRUE

### ResultadoValidacion
- id: SERIAL (PK)
- horario_id: INT (FK)
- es_valido: BOOLEAN
- reporte_json: JSONB

---

## 12. Exportaciones

### Exportacion
- id: SERIAL (PK)
- usuario_id: INT (FK)
- tipo: VARCHAR(10) CHECK (tipo IN ('PDF', 'Excel'))
- parametros: JSONB
- fecha: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
