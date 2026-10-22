# Evaluación de derivación de claves Nostr — 2026-10-22

Evidencia de apoyo para la ADR-0016 propuesta. Solo usa material de prueba
publicado (semilla insegura de Route B y vectores de NIP-06).

Comando: `python3 scripts/evaluate_nostr_derivation.py evidence/phase0/nostr-derivation-evaluation-2026-10-22`
(salida en `results.json`, código de salida 0).

## Resultados

| Comprobación | Resultado |
| --- | --- |
| Vectores 1 y 2 de NIP-06 (clave privada, pública, `nsec`, `npub`) reproducidos con el código BIP39/BIP32 del repositorio | 8/8 |
| Claves de rol 3' (2 redes × 10 entidades × 3 índices = 60) que coinciden con cuentas NIP-06 0–999 | 0 |
| Opción B (cuenta = entidad): la entidad 0 es la cuenta 0 por defecto de NIP-06 | sí (confusión con la identidad personal) |
| xpub de cuenta NIP-06 + clave hoja `/0/0` filtrada → clave privada de la cuenta | recuperada; también expone la hermana `/0/1` |
| Ruta de rol 3' totalmente endurecida (no aplica esa escalada) | sí |

## Opciones

| Criterio | A: rol 3' + exportación | B: NIP-06, cuenta = entidad | C: NIP-06, cuenta alta reservada |
| --- | --- | --- | --- |
| Conflicto con la cuenta personal 0 | no | **sí** | no |
| Restauración desde mnemónico en un cliente genérico | no (importar `nsec`/`ncryptsec` o firmante NIP-46) | solo entidad 0 | no |
| Rotación de clave Nostr | sí (`index'`) | no (`/0/0` fijo) | no |
| Separada del árbol maestro de Bitcoin (hijo BIP85) | sí | no | no |
| Escalada xpub + hoja | no | sí | sí |
| Restauración O2A | ADR-0015 | requiere segundo esquema | requiere segundo esquema |

Estado del ecosistema (consultado 2026-10-22): NIP-06 figura como
`draft`/`unrecommended` con la nota "prefer a single nsec"; NIP-49
(`ncryptsec`, scrypt + XChaCha20-Poly1305) y NIP-46 (firma remota, la clave
no sale del firmante) son las vías portables.

**Decisión recomendada: A.** Mantener el rol 3' y ofrecer exportación NIP-19
/ NIP-49 o firma NIP-46; no adoptar NIP-06 en v0.1.

Fuentes: nostr-protocol/nips 06.md, 46.md, 49.md (rama `master`).
