"""
Motor de Generación de Horarios — v3

RF-02:   Hard constraint — ningún profesor en dos aulas simultáneas.
RF-02.1: Auditoría de horas lectivas totales antes de aprobar.
RF-05:   Marco temporal académico configurable (franjas dinámicas).
RF-08.1: Soft constraint — respetar disponibilidad declarada del profesorado.
"""

from django.db import transaction
from datetime import time, datetime, timedelta

from apps.core.models import Grado, Asignatura, CursoAcademico, Horario, SesionHorario
from apps.authy.models import Profesor


# ---------------------------------------------------------------------------
# Utilidades de tiempo
# ---------------------------------------------------------------------------

def _calcular_franjas(hora_inicio: str, duracion_min: int, num_franjas: int) -> list[tuple[str, str]]:
    """
    Calcula una lista de (hora_inicio, hora_fin) a partir de los parámetros
    definidos por el decano.
    """
    base = datetime.strptime(hora_inicio, '%H:%M')
    franjas = []
    for _ in range(num_franjas):
        fin = base + timedelta(minutes=duracion_min)
        franjas.append((base.strftime('%H:%M'), fin.strftime('%H:%M')))
        base = fin
    return franjas


# ---------------------------------------------------------------------------
# Motor principal
# ---------------------------------------------------------------------------

class GeneradorHorarios:
    """
    Genera un horario semanal de plantilla para un grado/curso/semestre dado.

    Parámetros configurables por el decano
    ---------------------------------------
    hora_inicio     : Hora de inicio del bloque lectivo (ej. '09:00').
                      Para el último curso se usa '15:00' automáticamente.
    duracion_min    : Duración de cada sesión en minutos (ej. 90).
    num_franjas     : Número de franjas horarias por día (ej. 6).
    semestre        : '1', '2' — filtra las asignaturas del semestre elegido
                      más las anuales.

    Constraints implementados
    -------------------------
    Hard (RF-02):
      - Un mismo (profesor, día, franja) no puede aparecer en dos sesiones.
      - Un mismo (aula, día, franja) no puede aparecer en dos sesiones.
      - Un mismo (horario, día, franja) solo puede tener una sesión.

    Soft (RF-08.1):
      - Se excluyen los profesores que no tienen el día marcado como
        disponible. Si no hay ningún profesor disponible, la sesión se
        crea sin profesor y se emite una advertencia.
    """

    DIAS_SEMANA: list[str] = ['l', 'm', 'x', 'j', 'v']

    AULAS: list[str] = [
        'Aula A-1', 'Aula A-2', 'Aula A-3', 'Aula A-4',
        'Aula B-1', 'Aula B-2', 'Aula B-3',
        'Laboratorio 1', 'Laboratorio 2',
        'Sala de Conferencias',
    ]

    def __init__(
        self,
        curso_academico: CursoAcademico,
        grado: Grado,
        curso: int,
        semestre: str = '1',
        hora_inicio: str = '09:00',
        duracion_min: int = 90,
        num_franjas: int = 6,
    ):
        self.curso_academico = curso_academico
        self.grado = grado
        self.curso = curso
        self.semestre = semestre
        self.errores: list[str] = []
        self.advertencias: list[str] = []

        # El último curso siempre en horario de tarde
        hora_efectiva = '15:00' if curso == grado.duracion else hora_inicio
        self.FRANJAS_HORARIAS = _calcular_franjas(hora_efectiva, duracion_min, num_franjas)

        # ── Estructuras de seguimiento de ocupación ──────────────────────
        self._slots_horario: set = set()
        self._slots_profesor: dict = {}
        self._slots_aula: dict = {}
        self._carga_dia: dict = {d: 0 for d in self.DIAS_SEMANA}

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generar(self) -> Horario | None:
        if not self._validar_entrada():
            return None

        asignaturas = self._asignaturas_del_semestre()
        if not asignaturas:
            self.errores.append(
                f"El grado no tiene asignaturas en el {self.semestre}º semestre (ni anuales)."
            )
            return None

        self._cargar_ocupacion_existente()

        with transaction.atomic():
            horario = Horario.objects.create(
                curso_academico=self.curso_academico,
                grado=self.grado,
                curso=self.curso,
                semestre=self.semestre,
                estado='borrador',
            )
            self._generar_sesiones(horario, asignaturas)
            return horario

    # ------------------------------------------------------------------
    # Filtro de asignaturas por semestre
    # ------------------------------------------------------------------

    def _asignaturas_del_semestre(self):
        """Devuelve asignaturas del semestre elegido más las anuales."""
        return Asignatura.objects.filter(
            grados=self.grado,
            semestre__in=[self.semestre, 'a'],
        )

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
        if self.semestre not in ('1', '2'):
            self.errores.append("El semestre debe ser 1 o 2.")
        return len(self.errores) == 0

    # ------------------------------------------------------------------
    # Carga de ocupación existente (cross-horario)
    # ------------------------------------------------------------------

    def _cargar_ocupacion_existente(self) -> None:
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
        hora_str = hora_inicio.strftime('%H:%M')
        for idx, (inicio, _) in enumerate(self.FRANJAS_HORARIAS):
            if inicio == hora_str:
                return idx
        return None

    # ------------------------------------------------------------------
    # Sesiones semanales: regla fija
    # ------------------------------------------------------------------

    SESIONES_POR_ASIGNATURA = 2  # siempre 2 sesiones semanales por asignatura

    # ------------------------------------------------------------------
    # Selección de profesor disponible
    # ------------------------------------------------------------------

    def _profesores_validos(self, asignatura, dia: str, franja_idx: int) -> list:
        """
        Devuelve profesores que:
          1. Imparten la asignatura concreta (M2M).
          2. Tienen el día disponible (RF-08.1).
          3. No están ocupados en ese slot (RF-02).
        Si nadie imparte la asignatura, se devuelven todos los disponibles
        como fallback y se emite advertencia.
        """
        candidatos = Profesor.objects.filter(asignaturas=asignatura)
        if not candidatos.exists():
            candidatos = Profesor.objects.all()
            self.advertencias.append(
                f"'{asignatura.nombre}' no tiene ningún profesor asignado. "
                f"Se usará cualquier profesor disponible."
            )

        validos = []
        for profesor in candidatos:
            if profesor.disponibilidad and dia not in profesor.disponibilidad:
                continue
            if (dia, franja_idx) in self._slots_profesor.get(profesor.id, set()):
                continue
            validos.append(profesor)
        return validos

    # ------------------------------------------------------------------
    # Selección de aula libre
    # ------------------------------------------------------------------

    def _aula_libre(self, dia: str, franja_idx: int) -> str | None:
        for aula in self.AULAS:
            if (dia, franja_idx) not in self._slots_aula.get(aula, set()):
                return aula
        return None

    # ------------------------------------------------------------------
    # Búsqueda de slot válido
    # ------------------------------------------------------------------

    def _buscar_slot(self, asignatura, dias_excluidos: set) -> tuple | None:
        dias_candidatos = sorted(
            (d for d in self.DIAS_SEMANA if d not in dias_excluidos),
            key=lambda d: self._carga_dia[d],
        )
        for dia in dias_candidatos:
            for franja_idx in range(len(self.FRANJAS_HORARIAS)):
                if (dia, franja_idx) in self._slots_horario:
                    continue
                aula = self._aula_libre(dia, franja_idx)
                if not aula:
                    continue
                disponibles = self._profesores_validos(asignatura, dia, franja_idx)
                profesor = (
                    min(disponibles, key=lambda p: len(self._slots_profesor.get(p.id, set())))
                    if disponibles else None
                )
                return dia, franja_idx, profesor, aula
        return None

    # ------------------------------------------------------------------
    # Registro de ocupación
    # ------------------------------------------------------------------

    def _registrar_slot(self, dia: str, franja_idx: int, profesor, aula: str) -> None:
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
        for asignatura in asignaturas:
            num = self.SESIONES_POR_ASIGNATURA
            dias_usados: set = set()
            asignadas = 0

            for n in range(num):
                resultado = self._buscar_slot(asignatura, dias_usados)
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
                        f"'{asignatura.nombre}' — {dia} {inicio_str}: sin profesor disponible."
                    )

            if asignadas < num:
                self.advertencias.append(
                    f"'{asignatura.nombre}': {asignadas}/{num} sesiones asignadas."
                )


# ---------------------------------------------------------------------------
# Funciones de servicio públicas
# ---------------------------------------------------------------------------

def generar_horario(
    curso_academico_id: str,
    grado_id: str,
    curso: int,
    semestre: str = '1',
    hora_inicio: str = '09:00',
    duracion_min: int = 90,
    num_franjas: int = 6,
) -> dict:
    try:
        curso_academico = CursoAcademico.objects.get(id=curso_academico_id)
        grado = Grado.objects.get(id=grado_id)
    except (CursoAcademico.DoesNotExist, Grado.DoesNotExist) as e:
        return {'success': False, 'mensaje': 'Datos de entrada inválidos.', 'errores': [str(e)]}

    generador = GeneradorHorarios(
        curso_academico, grado, curso,
        semestre=semestre,
        hora_inicio=hora_inicio,
        duracion_min=duracion_min,
        num_franjas=num_franjas,
    )
    horario = generador.generar()

    if horario:
        return {
            'success': True,
            'horario_id': str(horario.id),
            'mensaje': (
                f"Horario generado: {grado.nombre} — Curso {curso} "
                f"({curso_academico.año}), {horario.get_semestre_display()}. "
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
    try:
        horario = Horario.objects.get(id=horario_id)
    except Horario.DoesNotExist:
        return {'valido': False, 'errores': ['Horario no encontrado.'],
                'horas_totales': 0, 'total_sesiones': 0}

    sesiones = SesionHorario.objects.filter(
        horario=horario
    ).select_related('asignatura', 'profesor__user')

    errores: list[str] = []

    for sesion in sesiones:
        if not sesion.profesor:
            continue
        nombre_prof = sesion.profesor.user.get_full_name() or sesion.profesor.user.username

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
                    f"{sesion.hora_inicio.strftime('%H:%M')}–{sesion.hora_fin.strftime('%H:%M')}."
                )

        if (sesion.profesor.disponibilidad
                and sesion.dia not in sesion.profesor.disponibilidad):
            errores.append(
                f"Disponibilidad: {nombre_prof} no tiene el "
                f"{sesion.get_dia_display()} como día disponible."
            )

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
                        f"({s1.hora_inicio.strftime('%H:%M')}–{s1.hora_fin.strftime('%H:%M')} y "
                        f"{s2.hora_inicio.strftime('%H:%M')}–{s2.hora_fin.strftime('%H:%M')})."
                    )

    asignaturas_semestre = Asignatura.objects.filter(
        grados=horario.grado,
        semestre__in=[horario.semestre, 'a'],
    )
    for asignatura in asignaturas_semestre:
        count = sesiones.filter(asignatura=asignatura).count()
        if count == 0:
            errores.append(
                f"Sin sesiones: '{asignatura.nombre}' no tiene ninguna sesión asignada."
            )
        elif count != 2:
            errores.append(
                f"Sesiones incorrectas: '{asignatura.nombre}' tiene {count} sesión(es) "
                f"(se esperan exactamente 2)."
            )

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
