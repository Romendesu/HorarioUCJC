"""
Motor de Generación de Horarios — v2

RF-02:   Hard constraint — ningún profesor en dos aulas simultáneas.
RF-02.1: Auditoría de horas lectivas totales antes de aprobar.
RF-05:   Marco temporal académico configurable (FRANJAS_HORARIAS).
RF-08.1: Soft constraint — respetar disponibilidad declarada del profesorado.
"""

from django.db import transaction
from datetime import time

from apps.core.models import Grado, Asignatura, CursoAcademico, Horario, SesionHorario
from apps.authy.models import Profesor


# ---------------------------------------------------------------------------
# Motor principal
# ---------------------------------------------------------------------------

class GeneradorHorarios:
    """
    Genera un horario semanal de plantilla para un grado/curso dado.

    Constraints implementados
    -------------------------
    Hard (RF-02):
      - Un mismo (profesor, día, franja) no puede aparecer en dos sesiones.
      - Un mismo (aula, día, franja) no puede aparecer en dos sesiones.
      - Un mismo (horario, día, franja) solo puede tener una sesión
        (un grupo de alumnos no puede estar en dos sitios).

    Soft (RF-08.1):
      - Se excluyen los profesores que no tienen el día marcado como
        disponible. Si no hay ningún profesor disponible, la sesión se
        crea sin profesor y se emite una advertencia.

    Distribución equitativa:
      - Se eligen primero los días con menos sesiones ya asignadas.
      - No se repite la misma asignatura dos veces en el mismo día.
    """

    # Franjas horarias lectivas (modificable para configuración dinámica RF-05)
    FRANJAS_HORARIAS: list[tuple[str, str]] = [
        ('08:30', '10:00'),
        ('10:00', '11:30'),
        ('11:30', '13:00'),
        ('13:00', '14:30'),
        ('14:30', '16:00'),
        ('16:00', '17:30'),
        ('17:30', '19:00'),
        ('19:00', '20:30'),
    ]

    DIAS_SEMANA: list[str] = ['l', 'm', 'x', 'j', 'v']

    AULAS: list[str] = [
        'Aula A-1', 'Aula A-2', 'Aula A-3', 'Aula A-4',
        'Aula B-1', 'Aula B-2', 'Aula B-3',
        'Laboratorio 1', 'Laboratorio 2',
        'Sala de Conferencias',
    ]

    def __init__(self, curso_academico: CursoAcademico, grado: Grado, curso: int):
        self.curso_academico = curso_academico
        self.grado = grado
        self.curso = curso
        self.errores: list[str] = []
        self.advertencias: list[str] = []

        # ── Estructuras de seguimiento de ocupación ──────────────────────
        # Slots ya usados por el horario que estamos construyendo.
        # Clave: (dia, franja_idx)
        self._slots_horario: set = set()

        # Slots ocupados por cada profesor en todo el año académico.
        # Clave: profesor.id  →  set de (dia, franja_idx)
        self._slots_profesor: dict = {}

        # Slots ocupados por cada aula en todo el año académico.
        # Clave: nombre_aula  →  set de (dia, franja_idx)
        self._slots_aula: dict = {}

        # Sesiones por día — para distribución equitativa.
        self._carga_dia: dict = {d: 0 for d in self.DIAS_SEMANA}

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generar(self) -> Horario | None:
        """Genera el horario. Devuelve el objeto Horario o None si hay errores."""
        if not self._validar_entrada():
            return None

        asignaturas = Asignatura.objects.filter(grado=self.grado)
        if not asignaturas.exists():
            self.errores.append("El grado no tiene asignaturas asignadas.")
            return None

        # Cargar ocupación existente del año académico (otros horarios ya
        # generados) para respetar los hard constraints cross-group.
        self._cargar_ocupacion_existente()

        with transaction.atomic():
            horario = Horario.objects.create(
                curso_academico=self.curso_academico,
                grado=self.grado,
                curso=self.curso,
                estado='borrador',
            )
            self._generar_sesiones(horario, asignaturas)
            return horario

    # ------------------------------------------------------------------
    # Validación de entrada
    # ------------------------------------------------------------------

    def _validar_entrada(self) -> bool:
        if not self.curso_academico:
            self.errores.append("Debe especificar un curso académico.")
        if not self.grado:
            self.errores.append("Debe especificar un grado.")
        if not self.curso or self.curso < 1 or self.curso > self.grado.duracion:
            self.errores.append(
                f"El curso debe estar entre 1 y {self.grado.duracion}."
            )
        return len(self.errores) == 0

    # ------------------------------------------------------------------
    # Carga de ocupación existente (cross-horario)
    # ------------------------------------------------------------------

    def _cargar_ocupacion_existente(self) -> None:
        """
        Lee las sesiones ya persistidas en el año académico actual e
        inicializa los rastreadores de profesor y aula. Esto garantiza
        que la nueva generación no colisione con horarios previos.
        """
        sesiones = SesionHorario.objects.filter(
            horario__curso_academico=self.curso_academico
        ).select_related('profesor')

        for sesion in sesiones:
            franja_idx = self._franja_para_hora(sesion.hora_inicio)
            if franja_idx is None:
                continue
            slot = (sesion.dia, franja_idx)

            if sesion.profesor_id:
                self._slots_profesor.setdefault(sesion.profesor_id, set()).add(slot)

            if sesion.aula:
                self._slots_aula.setdefault(sesion.aula, set()).add(slot)

    def _franja_para_hora(self, hora_inicio: time) -> int | None:
        """Devuelve el índice de franja cuya hora_inicio coincide."""
        hora_str = hora_inicio.strftime('%H:%M')
        for idx, (inicio, _) in enumerate(self.FRANJAS_HORARIAS):
            if inicio == hora_str:
                return idx
        return None

    # ------------------------------------------------------------------
    # Cálculo de sesiones semanales
    # ------------------------------------------------------------------

    def _sesiones_semanales(self, asignatura: Asignatura) -> int:
        """
        Calcula cuántas sesiones semanales (de 90 min) necesita una asignatura.

        Base ECTS española: 1 ECTS ≈ 10 horas lectivas de contacto.
        Semestral (≈15 semanas lectivas): sesiones/sem = (creditos × 10 / 15) / 1.5
        Anual     (≈30 semanas lectivas): sesiones/sem = (creditos × 10 / 30) / 1.5
        """
        divisor = 22.5 if asignatura.tipo == 's' else 45.0  # 15×1.5 | 30×1.5
        return max(1, round(asignatura.creditos * 10 / divisor))

    # ------------------------------------------------------------------
    # Selección de profesor disponible
    # ------------------------------------------------------------------

    def _profesores_validos(self, dia: str, franja_idx: int) -> list:
        """
        Devuelve profesores que cumplen:
          1. Tienen el día marcado como disponible (soft — RF-08.1).
          2. No están ya asignados a ese slot (hard — RF-02).
        """
        validos = []
        for profesor in Profesor.objects.all():
            # Filtro de disponibilidad del día
            if profesor.disponibilidad and dia not in profesor.disponibilidad:
                continue
            # Filtro de colisión de slot
            if (dia, franja_idx) in self._slots_profesor.get(profesor.id, set()):
                continue
            validos.append(profesor)
        return validos

    # ------------------------------------------------------------------
    # Selección de aula libre
    # ------------------------------------------------------------------

    def _aula_libre(self, dia: str, franja_idx: int) -> str | None:
        """Devuelve el nombre de un aula libre en el slot, o None."""
        for aula in self.AULAS:
            if (dia, franja_idx) not in self._slots_aula.get(aula, set()):
                return aula
        return None

    # ------------------------------------------------------------------
    # Búsqueda de slot válido
    # ------------------------------------------------------------------

    def _buscar_slot(self, dias_excluidos: set) -> tuple | None:
        """
        Busca (dia, franja_idx, profesor, aula) que cumpla todos los
        constraints. Estrategia greedy:
          - Días ordenados por carga ascendente (distribución equitativa).
          - Franjas en orden cronológico.
          - Profesor con menor carga asignada.
        """
        dias_candidatos = sorted(
            (d for d in self.DIAS_SEMANA if d not in dias_excluidos),
            key=lambda d: self._carga_dia[d],
        )

        for dia in dias_candidatos:
            for franja_idx in range(len(self.FRANJAS_HORARIAS)):
                # Hard: el grupo ya tiene clase en este slot
                if (dia, franja_idx) in self._slots_horario:
                    continue

                # Hard: necesitamos un aula libre
                aula = self._aula_libre(dia, franja_idx)
                if not aula:
                    continue

                # Soft: profesores disponibles y sin colisión
                disponibles = self._profesores_validos(dia, franja_idx)
                profesor = (
                    min(disponibles,
                        key=lambda p: len(self._slots_profesor.get(p.id, set())))
                    if disponibles else None
                )

                return dia, franja_idx, profesor, aula

        return None

    # ------------------------------------------------------------------
    # Registro de ocupación
    # ------------------------------------------------------------------

    def _registrar_slot(self, dia: str, franja_idx: int,
                        profesor, aula: str) -> None:
        """Marca el slot como ocupado en todas las estructuras."""
        slot = (dia, franja_idx)
        self._slots_horario.add(slot)
        self._carga_dia[dia] += 1
        if profesor:
            self._slots_profesor.setdefault(profesor.id, set()).add(slot)
        self._slots_aula.setdefault(aula, set()).add(slot)

    # ------------------------------------------------------------------
    # Generación de sesiones
    # ------------------------------------------------------------------

    def _generar_sesiones(self, horario: Horario, asignaturas) -> None:
        """Itera sobre asignaturas y asigna sus sesiones semanales."""
        for asignatura in asignaturas:
            num = self._sesiones_semanales(asignatura)
            dias_usados: set = set()  # no repetir asignatura el mismo día
            asignadas = 0

            for n in range(num):
                resultado = self._buscar_slot(dias_usados)

                if resultado is None:
                    self.advertencias.append(
                        f"'{asignatura.nombre}': no hay slot disponible "
                        f"para la sesión {n + 1}/{num}."
                    )
                    break

                dia, franja_idx, profesor, aula = resultado
                inicio_str, fin_str = self.FRANJAS_HORARIAS[franja_idx]

                SesionHorario.objects.create(
                    horario=horario,
                    asignatura=asignatura,
                    profesor=profesor,
                    dia=dia,
                    hora_inicio=time(*map(int, inicio_str.split(':'))),
                    hora_fin=time(*map(int, fin_str.split(':'))),
                    aula=aula,
                )

                self._registrar_slot(dia, franja_idx, profesor, aula)
                dias_usados.add(dia)
                asignadas += 1

                if not profesor:
                    self.advertencias.append(
                        f"'{asignatura.nombre}' — {dia} {inicio_str}: sin profesor "
                        f"disponible. La sesión se creó sin asignar."
                    )

            if asignadas < num:
                self.advertencias.append(
                    f"'{asignatura.nombre}': {asignadas}/{num} sesiones asignadas."
                )


# ---------------------------------------------------------------------------
# Funciones de servicio públicas
# ---------------------------------------------------------------------------

def generar_horario(curso_academico_id: str, grado_id: str, curso: int) -> dict:
    """
    Genera un horario para el grado/curso en el año académico indicado.

    Returns
    -------
    dict con claves: success, horario_id, mensaje, errores, advertencias
    """
    try:
        curso_academico = CursoAcademico.objects.get(id=curso_academico_id)
        grado = Grado.objects.get(id=grado_id)
    except (CursoAcademico.DoesNotExist, Grado.DoesNotExist) as e:
        return {
            'success': False,
            'mensaje': 'Datos de entrada inválidos.',
            'errores': [str(e)],
        }

    generador = GeneradorHorarios(curso_academico, grado, curso)
    horario = generador.generar()

    if horario:
        return {
            'success': True,
            'horario_id': str(horario.id),
            'mensaje': (
                f"Horario generado: {grado.nombre} — Curso {curso} "
                f"({curso_academico.año}). "
                f"{SesionHorario.objects.filter(horario=horario).count()} sesiones creadas."
            ),
            'errores': generador.errores,
            'advertencias': generador.advertencias,
        }
    else:
        return {
            'success': False,
            'mensaje': 'No se pudo generar el horario.',
            'errores': generador.errores,
        }


def validar_horario(horario_id: str) -> dict:
    """
    Valida un horario contra las reglas de negocio.

    Comprobaciones
    --------------
    - RF-02:   Colisiones de profesor en el mismo año académico.
    - RF-02.1: Todas las asignaturas del grado tienen al menos una sesión.
    - RF-08.1: Las sesiones respetan la disponibilidad del profesor.
    - Extra:   Colisiones de aula dentro del mismo año académico.

    Returns
    -------
    dict con claves: valido, errores, horas_totales, total_sesiones
    """
    try:
        horario = Horario.objects.get(id=horario_id)
    except Horario.DoesNotExist:
        return {'valido': False, 'errores': ['Horario no encontrado.'],
                'horas_totales': 0, 'total_sesiones': 0}

    sesiones = SesionHorario.objects.filter(
        horario=horario
    ).select_related('asignatura', 'profesor__user')

    errores: list[str] = []

    # ── RF-02: Colisiones de profesor ────────────────────────────────
    for sesion in sesiones:
        if not sesion.profesor:
            continue

        nombre_prof = (
            sesion.profesor.user.get_full_name()
            or sesion.profesor.user.username
        )

        # Buscar sesiones del mismo profesor, mismo día, en todo el año
        conflictos = SesionHorario.objects.filter(
            horario__curso_academico=horario.curso_academico,
            dia=sesion.dia,
            profesor=sesion.profesor,
        ).exclude(id=sesion.id)

        for c in conflictos:
            if sesion.hora_inicio < c.hora_fin and sesion.hora_fin > c.hora_inicio:
                errores.append(
                    f"Colisión de profesor: {nombre_prof} tiene sesiones solapadas "
                    f"el {sesion.get_dia_display()} "
                    f"{sesion.hora_inicio.strftime('%H:%M')}–"
                    f"{sesion.hora_fin.strftime('%H:%M')}."
                )

        # ── RF-08.1: Verificar disponibilidad ────────────────────────
        if (sesion.profesor.disponibilidad
                and sesion.dia not in sesion.profesor.disponibilidad):
            errores.append(
                f"Disponibilidad: {nombre_prof} no tiene el "
                f"{sesion.get_dia_display()} como día disponible."
            )

    # ── Colisiones de aula ───────────────────────────────────────────
    # Agrupar sesiones del año académico por (aula, dia)
    sesiones_año = SesionHorario.objects.filter(
        horario__curso_academico=horario.curso_academico
    ).order_by('aula', 'dia', 'hora_inicio')

    grupo_aula: dict = {}
    for s in sesiones_año:
        grupo_aula.setdefault((s.aula, s.dia), []).append(s)

    for (aula, dia), lista in grupo_aula.items():
        for i, s1 in enumerate(lista):
            for s2 in lista[i + 1:]:
                if s1.hora_inicio < s2.hora_fin and s1.hora_fin > s2.hora_inicio:
                    errores.append(
                        f"Colisión de aula: {aula} tiene dos sesiones solapadas "
                        f"el {s1.get_dia_display()} "
                        f"({s1.hora_inicio.strftime('%H:%M')}–"
                        f"{s1.hora_fin.strftime('%H:%M')} y "
                        f"{s2.hora_inicio.strftime('%H:%M')}–"
                        f"{s2.hora_fin.strftime('%H:%M')})."
                    )

    # ── RF-02.1: Todas las asignaturas tienen sesiones ───────────────
    for asignatura in horario.grado.asignaturas.all():
        if not sesiones.filter(asignatura=asignatura).exists():
            errores.append(
                f"Sin sesiones: la asignatura '{asignatura.nombre}' "
                f"no tiene ninguna sesión asignada."
            )

    # ── Métricas ─────────────────────────────────────────────────────
    horas_totales = sum(
        (s.hora_fin.hour + s.hora_fin.minute / 60)
        - (s.hora_inicio.hour + s.hora_inicio.minute / 60)
        for s in sesiones
    )

    return {
        'valido': len(errores) == 0,
        'errores': errores,
        'horas_totales': round(horas_totales, 1),
        'total_sesiones': sesiones.count(),
    }
