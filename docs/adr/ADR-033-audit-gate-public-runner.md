# ADR-033 — Audit gate du runner public de la chaîne σ_κ

**Statut** : PROPOSED
**Date d'ouverture** : 2026-05-10
**Décideur** : CEO
**Amont** : ADR-026 v2.1 (chaîne σ_κ, sample_markov), ADR-027 (chaîne statistique), ADR-030 (pré-reg κ ACCEPTED), ADR-031 (B-first), ADR-032 (pré-reg E₁, V3 §7.1), [research/MANIFEST.v0.4.0.yaml](../../research/MANIFEST.v0.4.0.yaml), [research/h7_kappa_run_results.csv](../../research/h7_kappa_run_results.csv)
**Aval** : déclenche, *si ACCEPTED*, le tag `audit-passed-v1`, la levée du verrou V3 (ADR-032 §7.1), la création de [research/MANIFEST.v0.5.0.yaml](../../research/MANIFEST.v0.5.0.yaml) et le tirage portabilité sur le pool `[2000-2029]` (E₁).
**Pool ressources** : pool d'audit `[1500-1529]` (re-jeu strict du tirage v0.4.0 ; **aucun nouveau seed consommé**). Pool portabilité `[2000-2029]` reste **GELÉ** jusqu'à acceptation de la présente ADR.
**Release attendue** : aucune. Cette ADR conditionne `v0.5.0-portability` ; elle n'en produit pas.

---

## 1. Contexte

Le verdict v0.4.0 (`KAPPA_REVERSES`, $d_{>} = +2.66$, $p_{>} = 9.31 \times 10^{-10}$, 30/30 seeds) a été produit par un runner privé, non versionné dans `src/`. La chaîne σ_κ a depuis été ré-implémentée publiquement et bit-pour-bit dans :

- [src/analysis/sigma_chain.py](../../src/analysis/sigma_chain.py) (commit `c901192`) — KL Miller-Madow corrigée, Laplace asymétrique, `fit_markov_transition`, `sample_markov`, Wilcoxon apparié, Cohen $d$ apparié.
- [src/agents/obs_shuffled_agent.py](../../src/agents/obs_shuffled_agent.py) (commit `c547a28`) — témoin S, BLAKE2b 8-octets little-endian.
- [src/analysis/verdict_v05.py](../../src/analysis/verdict_v05.py) (commit `597c9d0`) — verdict mécanique, seuils figés, surcharge INCONCLUSIVE.
- [src/experiments/portability_draw.py](../../src/experiments/portability_draw.py) (commit `f0501ba`) — runner public bout-en-bout.

Avant d'autoriser quelque tirage que ce soit sur le pool E₁ `[2000-2029]` (ADR-032 §7.1, verrou V3), nous devons **prouver publiquement** que ce runner reproduit le verdict v0.4.0 à la précision exigée. Sans cette preuve, un verdict v0.5.0 favorable serait indistinguable d'un effet d'implémentation, et un verdict défavorable serait imputable au runner plutôt qu'à E₁.

Cette ADR fige le **gate d'audit** : protocole, tolérances, critère binaire d'acceptation, procédure de divergence.

## 2. Décision

Une **session d'audit unique** est exécutée sur le pool `[1500-1529]` (E₀, 30 seeds, identiques à ceux du runner privé v0.4.0). Le CSV produit par [src/experiments/portability_draw.py](../../src/experiments/portability_draw.py) est comparé colonne par colonne, ligne par ligne, à [research/h7_kappa_run_results.csv](../../research/h7_kappa_run_results.csv) selon les tolérances figées en §4. Le résultat de la comparaison est **binaire** :

- **PASS** : la présente ADR passe en `ACCEPTED`, le tag `audit-passed-v1` est posé, le verrou V3 est levé, [src/experiments/portability_draw.py](../../src/experiments/portability_draw.py) devient le runner de référence pour `v0.5.0-portability`.
- **FAIL** : la présente ADR reste en `PROPOSED`, le verrou V3 reste actif, la procédure §6 (divergence) est exécutée publiquement, le CSV d'audit divergent est conservé tel quel et signé.

Aucun amendement de seuils n'est admissible *a posteriori*. Toute modification de §4 invalide une éventuelle session d'audit précédente.

## 3. Protocole opératoire

### 3.1 Pré-conditions (vérifiables binairement)

- HEAD du dépôt contient les commits `c901192`, `c547a28`, `597c9d0`, `f0501ba` (chaîne complète).
- `python -m pytest tests/adt/` passe avec ≥ 127/127 (état au commit `f0501ba`, hors POT).
- `git diff HEAD -- src/analysis/sigma_chain.py src/agents/obs_shuffled_agent.py src/experiments/portability_draw.py src/agents/memory1_agent.py src/agents/adaptive_agent.py src/env/e0.py` est **vide**.
- [research/h7_kappa_run_results.csv](../../research/h7_kappa_run_results.csv) est inchangé depuis [research/MANIFEST.v0.4.0.yaml](../../research/MANIFEST.v0.4.0.yaml) (vérification SHA-256).

### 3.2 Commande exacte

```bash
python -m src.experiments.portability_draw \
    --pool audit \
    --output research/h7_kappa_audit_v04.csv
```

(Pas de `--i-have-read-adr-033` requis pour le pool d'audit ; ce drapeau ne dérouille que le pool de portabilité E₁.)

### 3.3 Comparaison

Un script de comparaison `src/analysis/audit_compare.py` est rédigé en même temps que la présente ADR. Il charge les deux CSV, vérifie l'identité de l'en-tête (ordre et noms des 29 colonnes), du nombre de lignes (30) et de la colonne `seed` (ensemble identique, ordre préservé), puis applique les tolérances §4 colonne par colonne. Sortie : code de retour `0` (PASS) ou `1` (FAIL) + rapport détaillé sur stdout (max divergence par colonne, indice du seed pivot le cas échéant).

### 3.4 Artefacts conservés

Quel que soit le verdict :

- [research/h7_kappa_audit_v04.csv](../../research/h7_kappa_audit_v04.csv) — sortie du runner public (jamais réécrit, jamais nettoyé).
- `research/h7_kappa_audit_v04.report.txt` — sortie textuelle de `audit_compare.py`.
- Commit signé `audit: ADR-033 dry-run sur [1500-1529]` portant ces deux fichiers, **avant** tout tag de PASS ou amendement de cette ADR.

## 4. Tolérances (arbitrage CEO, immuables)

Les colonnes du CSV v0.4.0 sont classées en deux familles. La classification est figée ici et **fait foi** ; toute ambiguïté future se résout en faveur de la classe la plus stricte (entier).

### 4.1 Colonnes entières — égalité stricte (`==`)

| # | Colonne | Justification |
|---|---|---|
| 1 | `seed` | Identifiant pool. |
| 2 | `T_warmup` | Constante d'horizon (5000). |
| 3 | `T_stat` | Constante d'horizon (50000). |
| 4 | `B` | Nombre de bins histogramme (64). |
| 19 | `K_R_nonempty` | Cardinal de support, entier par construction. |
| 20 | `K_S_nonempty` | Idem. |
| 21 | `K_M_nonempty` | Idem. |
| 22 | `K_Mk_nonempty` | Idem. |
| 23 | `laplace_bins_R` | Cardinal de bins Laplacés, entier par construction. |
| 24 | `laplace_bins_S` | Idem. |
| 25 | `laplace_bins_Mk` | Idem. |
| 26 | `clip_events_R` | Compteur d'événements `np.clip`, entier. |
| 27 | `clip_events_S` | Idem. |
| 28 | `clip_events_M` | Idem. |
| 29 | `clip_events_Mk` | Idem. |

Toute divergence d'un seul élément d'une de ces colonnes est **éliminatoire** sans appel.

### 4.2 Colonnes flottantes — `np.isclose(atol=1e-9, rtol=0)`

| # | Colonne | Famille |
|---|---|---|
| 5 | `P_min` | Bornes de quantification. |
| 6 | `P_max` | Bornes de quantification. |
| 7-9 | `KL_{R,S,Mk}_M_corr` | KL Miller-Madow corrigée. |
| 10-12 | `KL_{R,S,Mk}_M_naive` | KL plug-in. |
| 13-14 | `delta_sigma_{R,Mk}_corr` | $\delta_\sigma^X = KL_X - KL_S$ (corrigé). |
| 15-16 | `delta_sigma_{R,Mk}_naive` | Idem (naïf). |
| 17 | `Delta_kappa_corr` | $\Delta_\kappa = \delta_\sigma^{M_\kappa} - \delta_\sigma^R$ (corrigé). |
| 18 | `Delta_kappa_naive` | Idem (naïf). |

Tolérance absolue `1e-9` choisie pour absorber le bruit d'arrondi IEEE-754 sur des sommes de ~$3.2 \times 10^6$ termes (T_stat × grid_size = 50000 × 64), tout en restant 5 ordres de grandeur en dessous de l'effet attendu ($|\Delta_\kappa| \sim 10^{-1}$). Pas de tolérance relative : à cette échelle, une divergence relative non-nulle sur un effet borné est mieux capturée par l'absolu.

### 4.3 Justification de l'asymétrie

Les colonnes entières mesurent des **objets combinatoires** (nombre de bins occupés, nombre d'événements de clip). Une divergence d'une unité signale un changement d'algorithme (ordre de balayage, gestion des bordures, criterion d'égalité), pas un bruit numérique. L'arbitrage `atol=1e-9 / strict` n'est donc pas un compromis : c'est la traduction opératoire correcte de la nature de chaque grandeur.

## 5. Conséquences si PASS

Toutes les actions ci-dessous sont des **conséquences mécaniques** de PASS, exécutées sans nouvel arbitrage :

1. Amendement de la présente ADR : `Statut: PROPOSED` → `Statut: ACCEPTED` ; ajout d'un §11 daté listant les SHA des artefacts d'audit.
2. Pose du tag `audit-passed-v1` sur le commit qui contient `research/h7_kappa_audit_v04.csv` conforme.
3. Levée du verrou V3 (ADR-032 §7.1) : le pool `[2000-2029]` devient consommable par [src/experiments/portability_draw.py](../../src/experiments/portability_draw.py) avec le drapeau `--i-have-read-adr-033`.
4. [src/experiments/portability_draw.py](../../src/experiments/portability_draw.py) acquiert le statut de **runner de référence public** pour la chaîne σ_κ. Toute modification ultérieure exige une nouvelle ADR et un nouvel audit gate.
5. Ouverture de [research/MANIFEST.v0.5.0.yaml](../../research/MANIFEST.v0.5.0.yaml) (signé pré-tirage), puis exécution `--pool portability --i-have-read-adr-033`.

## 6. Conséquences si FAIL

Aucune des actions §5 n'est exécutée. La procédure suivante s'enclenche :

### 6.1 Conservation publique

Le CSV divergent et son rapport sont commités tels quels (cf. §3.4). Toute correction ultérieure se fera sur de nouveaux artefacts (`research/h7_kappa_audit_v04_iter2.csv`, etc.). L'historique des divergences est public.

### 6.2 Diagnostic ordonné (par ordre de probabilité décroissante)

1. **Ordre de balayage Miller-Madow** : la correction $\frac{K-1}{2N}$ dépend de l'ordre dans lequel les bins vides/non-vides sont comptés. Vérifier dans [src/analysis/sigma_chain.py](../../src/analysis/sigma_chain.py) que `K = (counts > 0).sum()` est calculé *avant* le Laplacé.
2. **Cas-bord du Laplacé asymétrique** : si la masse totale d'un côté est nulle, l'asymétrie peut basculer ; vérifier le branchement `if/else` dans `kl_corrected_and_naive`.
3. **Convention de la fenêtre statistique** : `pressure[T_WARMUP:T_TOTAL]` est-il bien fermé-ouvert (Python standard) ou fermé-fermé (convention privée) ?
4. **`init_state` de `sample_markov`** : public utilise `int(trace_R.actions[0])`. Si le runner privé utilisait `0` ou `np.argmax(stationary)`, la séquence diverge dès $t=0$.
5. **Endianness BLAKE2b** : public utilise `little`, fixé. Une divergence sur S seul (R, M, M_κ identiques) signe un désaccord ici.
6. **Convention de collecte de la pression** : public collecte `obs_t` *avant* `act/step`. Une divergence systématique sur les KL bruts (R, S, M_κ tous décalés) signe un désaccord ici.
7. **Histogramme bordure** : `np.histogram` avec `bins=64, range=(0,1)` versus `np.linspace(0, 1, 65)` versus inclusion/exclusion de la borne supérieure.

Chaque hypothèse se traite par une **PR isolée** (un seul fichier modifié, un seul commit), suivie d'une nouvelle exécution §3.2 et d'une nouvelle comparaison §3.3. La présente ADR n'est pas amendée tant qu'une exécution PASS n'a pas été obtenue.

### 6.3 Interdits absolus pendant la procédure de divergence

- **Aucune modification de [research/h7_kappa_run_results.csv](../../research/h7_kappa_run_results.csv).** Le CSV v0.4.0 fait foi.
- **Aucun ajustement des tolérances §4.** L'arbitrage CEO est figé.
- **Aucun tirage exploratoire sur le pool `[2000-2029]`.** V3 reste actif.
- **Aucune modification de [src/env/e0.py](../../src/env/e0.py).** V1 reste actif.
- **Aucune modification des paramètres §3.1-§3.3 de [src/env/e1.py](../../src/env/e1.py).** V2 reste actif.

## 7. Verrous

V1 (E₀ §3.1-§3.3, tag `freeze-e1-v1`) : préservé.
V2 (E₁ §3.1-§3.3, tag `ready-portability-v1`) : préservé.
V3 (pool `[2000-2029]` gelé jusqu'à ADR-033 ACCEPTED) : préservé. **Cette ADR est l'instrument unique de levée de V3.**

## 8. Conséquences hors-scope

Cette ADR ne dit rien sur :
- L'éventualité d'un audit sur d'autres pools historiques (non requis).
- L'intégration continue du runner public (ADR future si jugée utile).
- Les évolutions futures de la chaîne σ_κ (toute évolution post-`audit-passed-v1` exige une nouvelle ADR + nouvel audit).

## 9. Lexique

Conforme ADR-020. Aucun des termes proscrits par ADR-020 §3 n'apparaît dans la présente ADR ni dans les fichiers qu'elle gouverne. Vérification opératoire : `grep -nEi <regex_ADR-020> docs/adr/ADR-033-*.md src/analysis/audit_compare.py tests/adt/test_audit_compare.py` doit ne rien retourner.

## 10. Annexe — script de comparaison (spécification minimale)

[src/analysis/audit_compare.py](../../src/analysis/audit_compare.py) implémente la fonction publique :

```python
def compare_audit_csv(
    reference_path: str | Path,
    candidate_path: str | Path,
    *,
    int_columns: tuple[str, ...] = INT_COLUMNS,
    float_atol: float = 1e-9,
) -> AuditReport
```

avec `AuditReport` dataclass `(passed: bool, max_abs_diff_per_column: dict[str, float], strict_mismatches_per_column: dict[str, int], n_rows_reference: int, n_rows_candidate: int, header_match: bool)`. Le CLI associé renvoie `0` si `passed`, `1` sinon, et écrit le rapport sur stdout au format texte stable.

Les ADTs associées (`tests/adt/test_audit_compare.py`, ≥ 8 cas : header mismatch, row-count mismatch, int divergence d'une unité = FAIL, float divergence à `1.1e-9` = FAIL, float divergence à `9e-10` = PASS, identité parfaite = PASS, ordre seeds permuté = FAIL, fichier manquant = exception explicite) sont commitées avant exécution §3.2.

## 11. Empreintes (à compléter à l'amendement ACCEPTED)

À renseigner uniquement si PASS. Format imposé :

```
audit_csv_sha256:        <à remplir>
audit_report_sha256:     <à remplir>
audit_compare_sha256:    <à remplir>
audit_run_commit:        <à remplir>
audit_passed_v1_commit:  <à remplir>
date_acceptee:           <à remplir>
```
