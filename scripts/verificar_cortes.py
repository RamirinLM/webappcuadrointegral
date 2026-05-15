"""
Verificación manual de cálculos de ProjectCut.
Ejecutar: env/Scripts/python.exe scripts/verificar_cortes.py
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

os.environ['DJANGO_SETTINGS_MODULE'] = 'cmi_project.settings'
os.environ['DJANGO_SECRET_KEY'] = 'test-key-for-verification'
import django
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from projects.models import Project, ProjectCut, Activity, Seguimiento
from projects.services import generate_project_cuts

today = date.today()

def fmt(val):
    """Formatea un valor Decimal o numérico para mostrar."""
    if val is None:
        return "N/A"
    return f"${float(val):,.2f}"

def check(label, actual, expected):
    """Verifica un valor y reporta OK o ERROR."""
    ok = actual == expected
    status = "OK" if ok else "ERROR"
    print(f"    [{status}] {label}: obtenido={actual}, esperado={expected}")
    return ok

print("=" * 70)
print(f" VERIFICACION DE CALCULOS DE CORTES DEL PROYECTO")
print(f" Fecha de referencia: {today}")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════════════
# PROYECTO A
# ═══════════════════════════════════════════════════════════════════════════
p1 = Project.objects.get(name__startswith='Proyecto de Prueba CMI')
print(f"\n{'─'*70}")
print(f" PROYECTO A: {p1.name}")
print(f" Periodo: {p1.start_date} → {p1.end_date}  ({(p1.end_date-p1.start_date).days} dias)")
print(f"{'─'*70}")

# Mostrar actividades con datos crudos
print(f"\n  Datos crudos de actividades:\n")
print(f"  {'#':2s} {'Nombre':28s} {'Ini Plan':12s} {'Fin Plan':12s} {'Costo':8s} {'Estado':14s} {'Ini Real':12s} {'Fin Real':12s} {'Costo R':8s}")
print(f"  {'-'*110}")
for i, a in enumerate(p1.activity_set.all().order_by('start_date'), 1):
    print(f"  {i:2d} {a.name:28s} {str(a.start_date):12s} {str(a.end_date):12s} {str(a.cost or 0):>8s} {a.status:14s} {str(a.actual_start_date or '-'):12s} {str(a.actual_end_date or '-'):12s} {str(a.actual_cost or '-'):>8s}")

# Generar cortes
p1.cuts.all().delete()
cuts = generate_project_cuts(p1, interval_days=90)

print(f"\n  Cortes generados: {len(cuts)} periodos de 90 dias")
print()

failed_checks = 0
for c_idx, c in enumerate(cuts, 1):
    acts = list(c.activities_in_period.order_by('start_date'))
    print(f"  ┌─ CORTE {c_idx}: {c.name} ({c.start_date} → {c.end_date})")
    print(f"  │")
    print(f"  │  Actividades en el periodo (end_date entre {c.start_date} y {c.end_date}):")
    
    # Verificar cada actividad que está en el periodo
    for a in acts:
        in_range = c.start_date <= a.end_date <= c.end_date
        assert in_range, f"ERROR: {a.name} end_date={a.end_date} NO esta en el rango!"
        comp = "COMPLETADA" if a.status == 'completed' else a.status
        print(f"  │    • {a.name:28s} end_plan={a.end_date} | costo_plan={a.cost} | estado={comp} | actual_end={a.actual_end_date}")
    
    print(f"  │")
    
    # ── VERIFICACION 1: planned_count ──
    expected_planned_count = len(acts)
    ok1 = check("planned_count", c.planned_count, expected_planned_count)
    if not ok1: failed_checks += 1
    
    # ── VERIFICACION 2: planned_cost (PV) ──
    expected_planned_cost = sum((a.cost or 0) for a in acts)
    ok2 = check("planned_cost (PV)", c.planned_cost, Decimal(str(expected_planned_cost)))
    if not ok2: failed_checks += 1
    
    # ── VERIFICACION 3: completed_count ──
    expected_completed = sum(1 for a in acts if a.status == 'completed')
    ok3 = check("completed_count", c.completed_count, expected_completed)
    if not ok3: failed_checks += 1
    
    # ── VERIFICACION 4: EV ──
    expected_ev = sum((a.cost or 0) for a in acts if a.status == 'completed')
    ok4 = check("EV (costo planif. de completes)", c.ev, Decimal(str(expected_ev)))
    if not ok4: failed_checks += 1
    
    # ── VERIFICACION 5: AC ──
    from decimal import Decimal as D
    expected_ac = sum(D(str(a.actual_cost)) for a in acts if a.status == 'completed' and a.actual_cost is not None)
    ok5 = check("AC (costo real de completes)", c.ac, expected_ac)
    if not ok5: failed_checks += 1
    
    # ── VERIFICACION 6: SV ──
    expected_sv = c.ev - c.pv
    ok6 = check("SV (EV-PV)", c.sv, expected_sv)
    if not ok6: failed_checks += 1
    
    # ── VERIFICACION 7: CV ──
    expected_cv = c.ev - c.ac
    ok7 = check("CV (EV-AC)", c.cv, expected_cv)
    if not ok7: failed_checks += 1
    
    # ── VERIFICACION 8: SPI ──
    if c.pv > 0:
        expected_spi = c.ev / c.pv
    else:
        expected_spi = D('0')
    ok8 = check("SPI (EV/PV)", c.spi, expected_spi)
    if not ok8: failed_checks += 1
    
    # ── VERIFICACION 9: CPI ──
    if c.ac > 0:
        expected_cpi = c.ev / c.ac
    else:
        expected_cpi = D('0')
    ok9 = check("CPI (EV/AC)", c.cpi, expected_cpi)
    if not ok9: failed_checks += 1
    
    # ── VERIFICACION 10: schedule_variance_count ──
    expected_svc = c.completed_count - c.planned_count
    ok10 = check("schedule_variance_count (completa-planif)", c.schedule_variance_count, expected_svc)
    if not ok10: failed_checks += 1
    
    # ── VERIFICACION 11: progress_percentage ──
    if c.planned_count > 0:
        expected_progress = round((c.completed_count / c.planned_count) * 100, 1)
    else:
        expected_progress = 0.0
    ok11 = check("progress_percentage", c.progress_percentage, expected_progress)
    if not ok11: failed_checks += 1
    
    # ── VERIFICACION 12: status (semaforo) ──
    spi_val = float(c.spi)
    cpi_val = float(c.cpi)
    if c.planned_count == 0:
        expected_status = 'no_data'
    elif c.completed_count == 0:
        expected_status = 'no_data'
    elif spi_val >= 0.95 and cpi_val >= 0.95:
        expected_status = 'green'
    elif spi_val >= 0.85 and cpi_val >= 0.85:
        expected_status = 'yellow'
    else:
        expected_status = 'red'
    ok12 = check("status (semaforo)", c.status, expected_status)
    if not ok12: failed_checks += 1
    
    print(f"  │")
    print(f"  └─ CONCLUSION: {c.name}")
    print(f"      {c.planned_count} actividades planif. | {c.completed_count} completes | {c.progress_percentage}%")
    print(f"      PV=${c.pv}  EV=${c.ev}  AC=${c.ac}  SV=${c.sv}  CV=${c.cv}")
    print(f"      SPI={float(c.spi):.4f}  CPI={float(c.cpi):.4f}  Estado={c.status_label} ({c.status})")
    print()

# ═══════════════════════════════════════════════════════════════════════════
# PROYECTO B
# ═══════════════════════════════════════════════════════════════════════════
p2 = Project.objects.get(name__startswith='Proyecto de Planificacion')
print(f"{'─'*70}")
print(f" PROYECTO B: {p2.name}")
print(f" Periodo: {p2.start_date} → {p2.end_date}  ({(p2.end_date-p2.start_date).days} dias)")
print(f" Estado: {p2.status} (aun no iniciado)")
print(f"{'─'*70}")

print(f"\n  Datos crudos:\n")
for i, a in enumerate(p2.activity_set.all().order_by('start_date'), 1):
    print(f"  {i:2d} {a.name:30s} plan_end={a.end_date} costo={a.cost} estado={a.status}")

p2.cuts.all().delete()
cuts2 = generate_project_cuts(p2, interval_days=90)
print(f"\n  Cortes generados: {len(cuts2)}\n")

for c in cuts2:
    acts2 = list(c.activities_in_period.order_by('start_date'))
    print(f"  ┌─ {c.name}: {c.start_date} → {c.end_date}")
    for a in acts2:
        print(f"  │  • {a.name:30s} end={a.end_date} costo={a.cost} (pendiente)")
    print(f"  ├─ planned_count={c.planned_count} completed_count={c.completed_count}")
    print(f"  ├─ PV={c.pv} EV={c.ev} AC={c.ac} SV={c.sv} CV={c.cv}")
    print(f"  ├─ SPI={float(c.spi):.2f} CPI={float(c.cpi):.2f}")
    print(f"  └─ ESTADO={c.status_label} ({c.status})")
    print()
    
    # Verificacion: todo debe ser 0 o valores esperados
    errs = 0
    for a in acts2:
        assert a.status == 'pending', f"{a.name} deberia estar pending pero es {a.status}"
    assert c.completed_count == 0, f"completed_count deberia ser 0"
    assert c.ev == 0, f"EV deberia ser 0"
    assert c.ac == 0, f"AC deberia ser 0"
    assert c.status == 'no_data', f"status deberia ser 'no_data' pero es '{c.status}'"
    print(f"     Verificacion: Todos los valores correctos (proyecto no iniciado) ✓")

# ═══════════════════════════════════════════════════════════════════════════
# VERIFICAR SEGUIMIENTOS vs CORTES
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
print(" VERIFICACION ADICIONAL: Seguimientos EVM existentes")
print(f"{'═'*70}")

segs = Seguimiento.objects.filter(proyecto=p1).order_by('fecha')
for s in segs:
    print(f"\n  Seguimiento del {s.fecha}:")
    print(f"    PV={s.pv} EV={s.ev} AC={s.ac} SV={s.sv} CV={s.cv} SPI={float(s.spi):.4f} CPI={float(s.cpi):.4f}")
    
    # Verificar manualmente PV de este seguimiento
    acts_up_to_date = p1.activity_set.filter(end_date__lte=s.fecha)
    manual_pv = sum(a.cost or 0 for a in acts_up_to_date)
    pv_ok = manual_pv == s.pv
    print(f"    PV manual (actividades con end_date <= {s.fecha}): {manual_pv} {'✓' if pv_ok else '✗ ERROR'}")
    if not pv_ok:
        failed_checks += 1
    
    # Verificar EV
    ev_activities = p1.activity_set.filter(status='completed', actual_end_date__lte=s.fecha)
    manual_ev = sum(a.cost or 0 for a in ev_activities)
    ev_ok = manual_ev == s.ev
    print(f"    EV manual (completadas con actual_end <= {s.fecha}): {manual_ev} {'✓' if ev_ok else '✗ ERROR'}")
    if not ev_ok:
        failed_checks += 1

# ═══════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
if failed_checks == 0:
    print("  RESULTADO: TODAS LAS VERIFICACIONES PASARON ✓")
    print("  Todos los calculos de ProjectCut son correctos.")
else:
    print(f"  RESULTADO: {failed_checks} VERIFICACION(ES) FALLARON ✗")
print(f"{'═'*70}")
