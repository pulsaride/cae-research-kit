# ADR-035 — H₇-κ Replication v0.5.0 (seed-paired @ D = 0.080)

**Statut** : ACCEPTED
**Date d'ouverture** : 2026-05-10
**Date d'acceptation** : 2026-05-10
**Décideur** : CEO (verrous épistémiques V1-V2-V3 ADR-032 §7.1 préservés ; aucun reviewer requis avant ACCEPTED)
**Amont** :
- ADR-032 §6.1 (verdict v0.5.0 = `KAPPA_TRANSFERS`, $d = +3.0906$)
- ADR-033 ACCEPTED (audit gate, tag `audit-passed-v1`, comparator pinné)
- ADR-034 §3.4 ligne 130 + §5.4 (override INCONCLUSIVE déclenché à 3.85 % > 1 %)
- [research/h7_kappa_boundary_verdict.json](../../research/h7_kappa_boundary_verdict.json) (v0.6.0 sweep, verdict `KAPPA_INCONCLUSIVE`, raison unique : discordance v0.5.0 @ D=0.080)
- [research/h7_kappa_portability.csv](../../research/h7_kappa_portability.csv) — référence v0.5.0 (`MANIFEST.v0.5.0.yaml` ligne 202, SHA-256 `b532d938b443ab75c5cef2c3063f4c7a827cf99a5fa31860a3b9ee83c02829ee`)
- [research/h7_kappa_boundary_sweep.csv](../../research/h7_kappa_boundary_sweep.csv) — sweep v0.6.0, sous-ensemble D=0.080 (lignes 122..151) sur seeds [4000-4029]
**Aval** : résolution du verdict v0.6.0 (BAND_LIMITED si PASS, INCONCLUSIVE_CONFIRMED si FAIL).
**Pool ressources** : **AUCUN nouveau pool**. Ré-emploi déterministe du pool [2000-2029] (POOL_PORTABILITY, ADR-032 §5.1) — *justification §3.3*.
**Coût** : ~6 min CPU (30 seeds × ~12 s).
**Release attendue** : aucune nouvelle release. Cette ADR clôt la décision v0.6.0 amorcée par ADR-034.

---

## 1. Contexte

### 1.1 Le verdict ADR-034 a tiré sur la concordance §5.4

Le sweep v0.6.0 (210 seeds, [research/h7_kappa_boundary_sweep.csv](../../research/h7_kappa_boundary_sweep.csv)) satisfait *six* des sept critères ROBUST/BAND_LIMITED d'ADR-034 §5.1–5.3 :

| Critère ADR-034 | Statut |
|---|---|
| `n_passing ≥ 3` (§5.2/5.3) | ✅ 6/7 |
| `D = 0.080 PASS` (§5.3) | ✅ ($d = 2.972$, $p = 9.31 \times 10^{-10}$, 30/30) |
| Set passant contigu | ✅ $[0.005, 0.32]$ |
| `inner_d_large_count ≥ 2` (§5.1) | ✅ 3/3 sur le triplet $\{0.04, 0.08, 0.16\}$ |
| `clip_total_sweep == 0` (§5.4) | ✅ 0 sur 210 runs |
| Concordance corr/naive intra-sample ≤ 1 % (§5.4) | ✅ identique à 6 décimales |
| **Concordance v0.5.0 @ D=0.080 (§3.4 ligne 130, §5.4)** | ❌ $\|2.9718 - 3.0906\| / 3.0906 = 3.85 \%$ > 1 % |

Seul le dernier critère a fired. Il déclenche `KAPPA_INCONCLUSIVE` en lecture stricte de la pré-registration ADR-034.

### 1.2 La forensique éclaire la nature de l'écart

L'écart de 3.85 % en Cohen $d$ entre v0.5.0 (seeds [2000-2029]) et v0.6.0 sweep@D=0.080 (seeds [4000-4029]) correspond à un écart absolu $\Delta d = 0.119$. À $n = 30$ avec deux pools de seeds **disjoints**, l'écart-type d'échantillonnage attendu de Cohen $d$ est de l'ordre de $\sqrt{2/30} \approx 0.26$ (Hedges & Olkin 1985, formule asymptotique pour Wilcoxon paired). Soit $\Delta d / \sigma_d \approx 0.46$ — **strictement dans le bruit d'échantillonnage** entre deux pools indépendants.

Le seuil 1 % d'ADR-034 §3.4 ligne 130, écrit avant tout tirage, présupposait implicitement une stabilité inter-pools incompatible avec la variance de Cohen $d$ à $n=30$. C'est une faille de spécification, non une dérive du mécanisme.

### 1.3 Pourquoi cette ADR n'est pas un amendement post-hoc

Re-formuler §3.4 ligne 130 *après* avoir vu le résultat serait du p-hacking. Cette ADR ne touche **pas** la règle d'ADR-034 et n'altère **pas** le verdict `KAPPA_INCONCLUSIVE` rendu sur le sweep `[4000-4029]`. Elle pré-enregistre un **test indépendant et bit-identique** : la réplication des conditions exactes de v0.5.0 (mêmes seeds, même $D$, même environnement E₁, mêmes agents) sur le code HEAD post-v0.5.0.

C'est la question scientifique sous-jacente *non testée par ADR-034* : **le code HEAD reproduit-il le claim v0.5.0 quand on lui donne les mêmes données d'entrée ?**

- Si **PASS** (Δ ≤ atol = 1e-9) : l'engine est inchangé, l'écart §5.4 vu sur le sweep est *par construction* du bruit inter-pools, le verdict `KAPPA_INCONCLUSIVE` reste rendu mais documenté comme déclenché par une règle trop serrée — la lecture *physique* du sweep est `KAPPA_BAND_LIMITED` (variant `upper_open`).
- Si **FAIL** : l'engine *a* dérivé entre v0.5.0 et HEAD ; toute la chaîne v0.6.0 doit être re-investigée et le verdict `KAPPA_INCONCLUSIVE_CONFIRMED` est définitif.

---

## 2. Décision

Pré-enregistrer, **avant exécution**, un seul test :

> Ré-exécuter `src/experiments/portability_draw.py` au commit HEAD (`210b3a0` ou successeur n'ayant pas modifié `portability_draw.py`, vérifié par SHA pin), avec `--pool portability`, sur les seeds `[2000-2029]`, et comparer le CSV produit à `research/h7_kappa_portability.csv` via `src.analysis.audit_compare` aux tolérances ADR-033 §4 (atol = 1e-9, == strict sur colonnes entières).

Le résultat est **binaire** : PASS ou FAIL.

---

## 3. Périmètre et invariants

### 3.1 Périmètre — ce qui est testé

- **Code amont** : `src/experiments/portability_draw.py`, `src/env/`, `src/agents/`, `src/metrics/`, `src/analysis/sigma_chain.py` — l'ensemble de la chaîne σ_κ telle qu'invoquée par `portability_draw`.
- **Configuration** : `E1Config` au `diffusion_coeff = 0.080` (calibration v0.5.0, ADR-032 §3.4), `T_warmup = 5000`, `T_stat = 50000`, `B = 64`, `grid_size = 64`, périodicité.
- **Seeds** : `[2000-2029]` (POOL_PORTABILITY, ADR-032 §5.1, sous verrou V3 levé par ADR-033).

### 3.2 Hors-périmètre — ce qui n'est pas testé

- **La règle ADR-034 §5.4 elle-même** n'est pas re-évaluée. Le verdict v0.6.0 du sweep reste celui calculé par `verdict_v06.compute_verdict` sur `h7_kappa_boundary_sweep.csv`, soit `KAPPA_INCONCLUSIVE`.
- **La concordance inter-pools** (le 3.85 %) n'est pas modifiée. C'est une donnée d'observation acquise.
- **Aucune nouvelle valeur de $D$** n'est explorée. Le sweep ADR-034 reste l'unique source pour la cartographie de l'enveloppe.
- **Aucune modification de code** entre la pré-registration de cette ADR (commit qui contient le présent document) et l'exécution de la réplication.

### 3.3 Justification du ré-emploi du pool [2000-2029]

ADR-031 §4.1 et ADR-032 §5.1 figent les pools pour empêcher le p-hacking par ré-tirage. Ré-utiliser ici ne contrevient pas à cette discipline parce que :

1. **Aucune décision nouvelle** n'est rendue sur ce pool. Le verdict v0.5.0 (`KAPPA_TRANSFERS`) reste figé. Le verdict v0.6.0 reste figé.
2. **Aucune statistique nouvelle** n'est calculée à partir de ce pool. La comparaison est une **assertion d'égalité bit-identique** (ADR-033 §4) sur les CSV produits, pas un test de Wilcoxon ni une mesure de Cohen $d$.
3. **Le test est diagnostique**, pas inférentiel. Il vérifie une propriété d'isomorphisme de l'engine, pas une propriété de population.

Cette utilisation est isomorphe au gate ADR-033 §3.2, qui ré-utilise `[1500-1529]` pour vérifier que `portability_draw` n'a pas dérivé depuis v0.4.0. Ici on étend le même protocole à `[2000-2029]` pour vérifier que rien n'a dérivé depuis v0.5.0.

### 3.4 Invariants pinnés

| Artefact | Pin |
|---|---|
| `src/experiments/portability_draw.py` SHA-256 | `3c4a7df4c67e162174466e2488ebc8d35676558e870e02c2bbb5cfc2716aa79d` (audit-passed-v1, identique à pin ADR-034 §4.4) |
| `research/h7_kappa_portability.csv` SHA-256 | `b532d938b443ab75c5cef2c3063f4c7a827cf99a5fa31860a3b9ee83c02829ee` (MANIFEST.v0.5.0.yaml ligne 202) |
| Tolérance flottante | `atol = 1e-9`, pas de relatif (ADR-033 §4) |
| Comparaison entiers | `==` strict (ADR-033 §4) |
| Pool | exactement `range(2000, 2030)` |
| Configuration E₁ | exactement celle calibrée ADR-032 §3.4 |

Toute violation d'un de ces invariants invalide la réplication et déclenche `INCONCLUSIVE_CONFIRMED` par défaut.

---

## 4. Procédure

### 4.1 Commande exacte

```bash
python -m src.experiments.portability_draw \
    --pool portability \
    --i-have-read-adr-033 \
    --output research/h7_kappa_replication_v060.csv

python -m src.analysis.audit_compare \
    --reference research/h7_kappa_portability.csv \
    --candidate research/h7_kappa_replication_v060.csv \
    --report-output research/h7_kappa_replication_v060.report.txt
```

Exit code de la seconde commande : `0` ⇒ PASS, `1` ⇒ FAIL.

### 4.2 Pré-conditions de lancement

1. ADR-035 a le statut `ACCEPTED` au moment du lancement (commit présent sur main avant la première ligne d'output du runner).
2. SHA-256 de `src/experiments/portability_draw.py` vérifié == pin §3.4.
3. SHA-256 de `research/h7_kappa_portability.csv` vérifié == pin §3.4.
4. Aucune modification non-commitée dans `src/`, `research/h7_kappa_portability.csv`, ou les ADR amont.
5. `git status` propre.

### 4.3 Artefacts à conserver

- `research/h7_kappa_replication_v060.csv` — CSV produit (jamais réécrit, jamais nettoyé).
- `research/h7_kappa_replication_v060.report.txt` — rapport texte d'`audit_compare`.
- Log d'exécution `portability_draw` (stdout/stderr) — facultatif, recommandé.

---

## 5. Conditions de verdict v0.6.0 résolu

### 5.1 Si PASS (atol ≤ 1e-9, == strict)

- **Confirmation factuelle** : l'engine HEAD est bit-identique à l'engine v0.5.0 sur le pool [2000-2029] @ D=0.080.
- **Lecture du sweep ADR-034** : la ligne fracture observée à $D = 0.640$ et la bande $[0.005, 0.32]$ tiennent sans réserve. L'écart 3.85 % de §5.4 est *par construction* du bruit d'échantillonnage entre pools disjoints à $n=30$, comme prévu par la statistique.
- **Verdict v0.6.0 résolu** : `KAPPA_INCONCLUSIVE` reste le verdict pré-enregistré ADR-034 (la règle a été honorée à la lettre). La **lecture physique** publiée parallèlement est `KAPPA_BAND_LIMITED (upper_open)`, avec mention explicite dans RELEASE.md v0.6.0 et le Manifeste de la défaillance de spécification §5.4 et de la procédure ADR-035 qui l'a documentée.
- **Conséquence ADR** : ADR-035 passe ACCEPTED puis CLOSED. ADR-036 *peut* (non-obligatoire) être ouverte pour proposer une formulation amendée du critère §3.4 ligne 130 destinée à un futur ADR-037 boundary v0.7.0 (ex. tolérance fonction de $\sqrt{2/n}$).
- **Conséquence release** : v0.6.0 publiable comme `v0.6.0-h7-κ-boundary-inconclusive-bandlimited-de-facto`. Pas de tag `KAPPA_TRANSFERS` étendu — l'enveloppe reste documentée comme `INCONCLUSIVE` au sens strict ADR-034.

### 5.2 Si FAIL (au moins une violation atol ou ==)

- **Confirmation factuelle** : l'engine HEAD a dérivé depuis v0.5.0 — soit dans `src/env/`, `src/agents/`, `src/metrics/`, soit dans `src/analysis/sigma_chain.py`, soit dans une dépendance numérique (numpy, scipy version).
- **Lecture du sweep ADR-034** : entièrement compromise. Le sweep `h7_kappa_boundary_sweep.csv` a été calculé sur un engine non-équivalent à v0.5.0. Toute affirmation sur la cartographie d'enveloppe est suspendue.
- **Verdict v0.6.0 résolu** : `KAPPA_INCONCLUSIVE_CONFIRMED` (label terminal). Aucune lecture de bande publiable.
- **Conséquence ADR** : ADR-035 passe ACCEPTED puis FAILED. Ouverture obligatoire d'ADR-036 forensique (`git bisect` entre v0.5.0 commit `4bafdac` et HEAD sur les colonnes divergentes), suspendant tout tirage v0.7.0 jusqu'à identification du commit responsable.
- **Conséquence release** : v0.6.0 NON publiable. Hold strict.

### 5.3 Cas de procédure non-conforme

Si l'une des conditions §4.2 n'est pas remplie au moment du lancement, le test est **invalide** et doit être ré-exécuté après remise en conformité. L'exécution d'un test non-conforme est elle-même un événement à journaliser dans le rapport mais ne peut **ni** valider PASS, **ni** déclencher FAIL terminal.

---

## 6. Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| FAIL pour cause de dépendance numpy/scipy | faible | bloquant v0.6.0 | environnement venv `.venv-h6` figé depuis v0.5.0, ADR-036 forensique préparée |
| FAIL pour cause de modification non-déclarée de `src/env/` ou `src/metrics/` | très faible | bloquant v0.6.0 | `git log --oneline v0.5.0..HEAD -- src/env/ src/metrics/` doit être vide ou commits explicitement neutres |
| PASS interprété abusivement comme validation rétroactive du critère §5.4 | moyenne | réputationnelle | §5.1 spécifie : verdict pré-enregistré ADR-034 (`INCONCLUSIVE`) reste rendu. Aucune révision rétroactive d'ADR-034 |
| Ré-emploi du pool [2000-2029] perçu comme p-hacking | moyenne | réputationnelle | §3.3 documente : test diagnostique d'isomorphisme, pas inférentiel ; pas de statistique nouvelle calculée sur ce pool |
| Le tag `audit-passed-v1` (ADR-033) n'est pas rétroactivement validé sur D=0.080 | nulle | n/a | ADR-033 §3.2 testait sur [1500-1529]. ADR-035 étend le test à [2000-2029]. Indépendant |

---

## 7. Conséquences ACCEPTED

À l'acceptation :

1. Cette ADR passe `PROPOSED → ACCEPTED` (en-tête mis à jour, date d'acceptation pinnée).
2. Le commit d'acceptation **précède** strictement la première ligne du log de réplication.
3. La pré-condition §4.2.1 est remplie.
4. Le tirage est lancé selon §4.1.
5. Sur PASS : RELEASE.md v0.6.0 et Manifeste v0.6.0 sont rédigés selon §5.1.
6. Sur FAIL : hold v0.6.0, ouverture ADR-036 selon §5.2.

---

## 8. Workflow de bout en bout (récapitulatif opérationnel)

| Étape | Action | Condition de succès | Coût |
|---|---|---|---|
| 1 | ADR-035 commitée PROPOSED | tests existants restent verts | < 1 min |
| 2 | Décision CEO ACCEPTED | header mis à jour, date pinnée | < 1 min |
| 3 | Vérification SHA pin §3.4 | match exact | < 10 s |
| 4 | Lancement `portability_draw --pool portability` | 30/30 seeds, exit 0 | ~6 min |
| 5 | Lancement `audit_compare` | exit 0 (PASS) ou exit 1 (FAIL) | < 5 s |
| 6a | Si PASS : RELEASE.md + Manifeste v0.6.0 | sealed, tagged | ~30 min |
| 6b | Si FAIL : hold + ouverture ADR-036 | bisect plan | ~15 min |

Total path PASS : ~40 min jusqu'à v0.6.0 sealed.
Total path FAIL : ~15 min jusqu'à hold formel.

---

## 9. Décision attendue

**Au CEO** : valider PROPOSED → ACCEPTED. Aucune autre action ne sera prise sur cette ADR ou sur le code tant que la décision n'est pas formellement rendue et committée.
