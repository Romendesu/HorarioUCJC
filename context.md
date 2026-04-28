4.0 Clasificación de Requisitos.
Esta estructura organiza los requisitos que se han analizado bajo la metodología MoSCoW, permitiendo a los interesados visualizar claramente el alcance del Producto Mínimo Viable (MVP) frente a las evoluciones planificadas para el futuro. 

Categoría
Prioridad
Objetivo Principal
Requisitos Funcionales Involucrados
Requisitos No Funcionales Involucrados
Must Have
Requisitos imprescindibles
Operatividad core y validación de reglas del horario.
RF-01, RF-02, RF-02.1, RF-04, RF-05, RF-05.1, RF-07, RF-08.1, RF-11.
RNF-04,RNF-05,
RNF-07, RNF-17, RNF-03, RNF - 09, RNF-14, RNF-16, RNF-17 
Should Have
Requisitos importantes
Usabilidad, reporting y eficiencia operativa.
RF-03, RF-03.1, RF-08, RF-09, RF-10,RF-12,RF-14.
RNF-01, RNF-02, RNF-06, RNF-08.1, RNF-12, RNF-18, RNF-19
Could Have
Requisitos deseables
Comunicación proactiva e integración ecosistémica.
RF-06,RF-08,RF-13
RNF-08, RNF-10, RNF-15
Won’t Have
Requisitos que no se deben implementar por el momento 
Escalabilidad masiva y funciones de gestión avanzada.
RF-12.3
RNF-11



4.1 Must Have
RF - 01: El sistema debe permitir al personal administrativo gestionar el ciclo completo de horarios (creación, edición y borrado) segmentando por titulación, curso y año académico.
RF - 02: Se debe implementar un motor de reglas que valide, en tiempo real, la disponibilidad del profesorado contra la carga asignada, impidiendo la programación de sesiones simultáneas para un mismo docente (Hard Constraints).
RF - 02.1: El motor de reglas debe garantizar, mediante un reporte de auditoría, que cada curso académico cumpla estrictamente con el total de horas lectivas requeridas por el plan de estudios antes de permitir su aprobación definitiva.
RF - 04: El sistema debe incluir un estado de "Workflow" para los horarios generados (Borrador → Revisión → Aprobado/Rechazado). Este proceso debe requerir la validación formal de un usuario con rol de Decanato o Dirección Académica.
RF - 05: El sistema debe proporcionar una interfaz de configuración dinámica para definir el marco temporal académico. Esta herramienta debe permitir la gestión de: sesiones lectivas, franjas horarias personalizadas y días lectivos, adaptándose a la normativa específica de cada centro.
RF - 05.1: Los parámetros definidos en esta configuración actuarán como reglas de negocio base para el motor de generación de horarios, garantizando que el sistema sea adaptable a distintos planes de estudio y calendarios institucionales sin requerir cambios en el código fuente.
RF - 07: Una vez generado el horario por el motor de reglas, el sistema debe habilitar una interfaz de edición manual para que el perfil de Dirección realice ajustes excepcionales antes de pasar al estado de 'Revisión'.
RF - 08.1: Los profesores podrán marcar franjas de 'disponibilidad preferente' y 'bloqueos de indisponibilidad', los cuales serán tomados en cuenta por el motor de generación automática de horarios.
RF - 11: El sistema debe proporcionar una interfaz de consulta avanzada que permita a los estudiantes visualizar su horario académico completo. La herramienta deberá soportar filtros multinivel para recuperar la información, garantizando que los datos mostrados correspondan únicamente a las asignaturas matriculadas del usuario.
RNF-03: El sistema debe mantener la integridad y los tiempos de respuesta definidos (RNF-02) bajo una concurrencia de hasta 500 usuarios conectados simultáneamente, soportando picos de tráfico sin degradación del rendimiento o errores de conexión (HTTP 5xx).
RNF-04: El sistema debe implementar un mecanismo de autenticación robusta que valide la identidad del usuario mediante credenciales cifradas (usuario y contraseña).
RNF-05: El sistema debe garantizar la confidencialidad absoluta de la Información de Identificación Personal (PII) de profesores y estudiantes, cumpliendo estrictamente con el RGPD.
RNF-07: El sistema debe gestionar los permisos mediante un modelo de Control de Acceso Basado en Roles (RBAC).
RNF - 09: El sistema debe implementar un sistema de notificaciones basado en una jerarquía semántica (informativa, advertencia, error y éxito), utilizando un lenguaje natural y libre de tecnicismos que permita al usuario identificar la causa del evento y la acción correctiva necesaria.
RNF-14: El sistema debe implementar un servicio centralizado de registros (logs) que capture eventos críticos, errores de ejecución, advertencias y actividades de acceso. 
RNF-16: El sistema debe emplear un diseño basado en configuración (no hardcoded) que permita la adición de nuevas titulaciones, modificar los campos de la duración de las asignaturas o la integración de asignaturas compartidas entre departamentos.
RNF-17: El sistema debe garantizar una disponibilidad de servicio del 99,5% mensual.
Restricciones de Dominio (Todas): Todas las reglas de negocio descritas en la sección 3.3 se consideran de cumplimiento obligatorio para la validez del motor de horarios.
4.2 Should Have
RF - 03: El sistema debe generar informes dinámicos filtrados por titulación, curso, asignatura o profesorado.
RF - 03.1: Los informes deben ser exportables a PDF (estándar de visualización) y Excel (estándar de manipulación de datos).
RF - 08: El sistema debe permitir que el profesorado gestione su disponibilidad horaria mediante una interfaz intuitiva.
RF - 09: El sistema debe proporcionar al profesorado una vista personalizada de su carga docente, permitiendo la consulta centralizada de todas las sesiones, asignaturas y grupos asignados.
RF - 10: El sistema debe implementar un motor de monitorización que notifique automáticamente al profesor sobre cualquier alteración en su programación académica.
RF - 12: El sistema debe implementar un motor de alertas automáticas para notificar a los estudiantes sobre cambios relevantes en su carga lectiva.
RF - 14: El sistema debe incluir un motor de validación que analice la carga lectiva del estudiante y generar alertas automáticas ante conflictos horarios o de solapamiento derivados de la matriculación en asignaturas de diferentes cursos o niveles académicos.
RNF-01: Completar la generación de horarios en un tiempo inferior a 300 segundos.
RNF-02: La interfaz debe responder a las consultas de horarios realizadas por estudiantes o profesores en un tiempo inferior a 2 segundos, medido desde la emisión de la solicitud HTTP hasta la renderización completa del componente visual en el cliente (Time to Interactive).
RNF-06: El sistema debe integrar un módulo de auditoría (logs) que registre de forma persistente e inalterable cualquier modificación.
RNF - 08.1: La interfaz debe alinearse con la identidad corporativa de la Universidad Camilo José Cela.
RNF-12: El sistema debe garantizar la interoperabilidad con los ecosistemas de software de la UCJC mediante APIs RESTful.
RNF-18 / RNF-19: Copias de seguridad diarias y Plan de Recuperación ante Desastres.

4.3 Could Have
RF - 06: El sistema debe permitir la vinculación de profesores titulares a asignaturas específicas y el registro de perfiles suplentes categorizados por área de conocimiento.
RF - 08.2: Cada actualización de disponibilidad debe quedar registrada en el historial del profesor para auditoría.
RF - 13: El sistema debe identificar y mostrar de forma clara aquellas asignaturas que son compartidas entre diferentes titulaciones (asignaturas transversales) con un indicador visual.
RNF - 08: La interfaz debe ser intuitiva para cualquier usuario, permitiendo que un usuario nuevo pueda generar o consultar horarios sin necesidad de formación previa.
RNF - 10: Implementar una arquitectura de información plana que permita ejecutar tareas críticas mediante un recorrido máximo de 5 acciones.
RNF-15: La arquitectura del sistema debe estar diseñada para ser escalable linealmente.

4.4 Won’t Have

RF - 12.3 (Opcional): El envío de mensajes mediante el correo electrónico corporativo (se priorizan las notificaciones in-app).
RNF-11: Aunque es un requisito de compatibilidad, las versiones específicas de navegadores del año 2026 (como Chrome v145.X) quedan fuera del alcance del desarrollo inicial actual si el entorno de ejecución actual es previo a esa fecha.

