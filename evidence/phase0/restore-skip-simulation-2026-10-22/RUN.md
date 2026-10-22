# Simulación del salto tras restauración — 2026-10-22

Evidencia de apoyo para la ADR-0015 propuesta. El mantenedor pidió simular
el salto de 20 índices tras cada restauración.

Comando (semilla fija 20261022, 20 000 ensayos por celda):

```text
python3 scripts/simulate_restore_skip.py evidence/phase0/restore-skip-simulation-2026-10-22/scan-gap-20 20
python3 scripts/simulate_restore_skip.py evidence/phase0/restore-skip-simulation-2026-10-22/scan-gap-100 100
```

## Modelo

Una billetera asigna entre 1 y 200 índices; algunos se publican; el
manifiesto y los historiales llegan a la copia externa con retraso; el
dispositivo se pierde y se restaura desde la copia externa (si existe) más un
escaneo por brecha. Hay **reutilización** si el siguiente índice restaurado
no supera el último índice asignado antes de la pérdida. Políticas:

- `free`: se asigna sin esperar a la copia externa.
- `cap`: escritura anticipada externa — nunca se asigna un índice a más de S
  posiciones del máximo restaurable desde la copia externa; si se rebasaría,
  primero se sincroniza.
- `adaptive`: `cap` con S = 20 tras restaurar con manifiesto y S = 100 tras
  una restauración solo por escaneo.

Escenarios: `typical`, `poor_backups` (sincronización rara, 30 % de pérdida
del manifiesto, 30 % de historiales perdidos), `draft_bursts` (70 % de
borradores no publicados), `no_manifest_ever`, y `*_2copies` (dos copias
independientes del manifiesto).

## Resultados clave (reutilización de cualquier índice)

| Escenario | free, S=20 | cap, S=20 | adaptive, brecha 20 | adaptive, brecha 100 |
| --- | ---: | ---: | ---: | ---: |
| typical | 0,070 % | 0 | 0 | 0 |
| poor_backups | 31,58 % | 1,02 % | 0 | 0 |
| draft_bursts | 1,00–1,83 % | 0,30–1,04 % | 0,27 % | **0** |
| no_manifest_ever | 0,050 % | 0,020 % | 0 | 0 |
| poor_backups_2copies | 31,61 % | 0,30 % | 0 | 0 |
| draft_bursts_2copies | 0,83–1,00 % | 0,05–0,28 % | 0,03 % | **0** |

Cuando una celda muestra un rango, el primer valor es con brecha de escaneo 100 y el segundo con brecha 20.

Tablas completas: `scan-gap-20/table.md`, `scan-gap-100/table.md`;
datos: `results.json` en cada carpeta.

## Lectura

1. Un salto fijo de 20 sin regla de escritura anticipada **no basta**: con
   copias de seguridad pobres se reutiliza un índice en ~32 % de las
   restauraciones.
2. La escritura anticipada externa (`cap`) es la palanca principal: con S=20
   deja el riesgo en 0–1 %, y en cero siempre que el manifiesto exista,
   porque entonces el manifiesto cubre hasta S índices antes del último.
3. El riesgo residual aparece solo en restauraciones sin manifiesto con
   muchos borradores invisibles al escaneo. Lo eliminan un salto de 100 y
   una brecha de escaneo de 100 en ese caso.
4. **Combinación recomendada:** escritura anticipada externa con tope 20,
   salto 20 tras restaurar con manifiesto, brecha de escaneo 100 y salto 100
   tras restaurar solo por escaneo, y dos copias del manifiesto. Resultado:
   0 reutilizaciones en 120 000 ensayos (6 escenarios), con un desperdicio
   medio de 19–36 índices (≈97 solo si no hay manifiesto). El espacio de
   índices es de 2^31, así que el desperdicio es irrelevante.

Limitaciones: modelo sintético; supone que una sincronización externa es
atómica y que la derivación de claves para el escaneo es barata (lo es en
código nativo).
