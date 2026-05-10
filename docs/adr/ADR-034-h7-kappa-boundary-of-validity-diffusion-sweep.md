# ADR-034 — H₇-κ Boundary of Validity (diffusion sweep on E₁)

**Statut** : ACCEPTED
**Date d'ouverture** : 2026-05-10
**Date d'acceptation** : 2026-05-10
**Décideur** : CEO (verrous épistémiques V1-V2-V3 ADR-032 §7.1 ; aucun reviewer requis avant ACCEPTED)
**Amont** : ADR-032 §1 (déclencheur nominal), ADR-032 §6.1 (verdict v0.5.0 = `KAPPA_TRANSFERS`), ADR-033 ACCEPTED (audit gate hérité), [RELEASE.md v0.5.0 §6](../../RELEASE.md) "Portability beyond E₁" (question ouverte)
**Aval** : ADR-035 (CAE-Cert v0.1, déclenché *si* v0.6.0 = `KAPPA_ROBUST_PORTABILITY`), ADR de remédiation seulement *si* v0.6.0 = `KAPPA_FRAGILE`
**Pool ressources** : nouveau pool `[4000-4029]` (sweep partagé sur K valeurs de diffusion). **Aucun chevauchement avec pools κ existants** (`[1500-1599]` consommés/réservés ADR-030/031, `[2000-2099]` consommés/réservés ADR-032).
**Release attendue** : `v0.6.0-h7-κ-boundary` (verdict `KAPPA_ROBUST_PORTABILITY` / `KAPPA_BAND_LIMITED` / `KAPPA_FRAGILE`), deadline 2026-06-30.

---

## 1. Contexte

### 1.1 Situation post-v0.5.0

ADR-032 §1 prévoyait initialement deux déclencheurs aval mutuellement exclusifs :

- *si* v0.5.0 = `KAPPA_FAILS_TRANSFER` → ADR-034 (boundary-of-validity) en priorité absolue
- *si* v0.5.0 = `KAPPA_TRANSFERS` → ADR-035 (CAE-Cert v0.1)

Le verdict v0.5.0 publié (DOI [10.5281/zenodo.20107855](https://doi.org/10.5281/zenodo.20107855), commit `4bafdac`) est `KAPPA_TRANSFERS`. La condition nominale de déclenchement d'ADR-034 n'est donc *pas* remplie.

Cette ADR ré-oriente néanmoins ADR-034 vers son objet sous-jacent — *caractériser la frontière de validité du résultat κ sur E₁* — en partant de l'autre côté : non plus pour expliquer un échec (FAILS_TRANSFER) mais pour borner par le haut une réussite (TRANSFERS). Le scope reste identique : **sous quelles conditions de E₁ la signature κ tient-elle, et où s'effondre-t-elle ?**

### 1.2 Question scientifique

`E1Config.diffusion_coeff` était calibré une seule fois (ADR-032 §3.4) pour satisfaire $\bar\sigma^{E_1}(D) \in [0.5, 0.8] \times \bar\sigma^{E_0}$. La valeur retenue $D = 0.080$ a produit `KAPPA_TRANSFERS` avec Cohen $d = +3.09$, $p_{>} = 9.31 \times 10^{-10}$, 30/30 seeds positifs.

**Question** : la signature κ tient-elle sur une *bande* de valeurs de $D$, ou est-elle un artefact ponctuel de la valeur calibrée ? Existe-t-il un $D^* > 0.080$ au-delà duquel le signal s'effondre (régime fortement diffusif où la prédiction locale devient impossible) ? Existe-t-il un $D^\dagger < 0.080$ en-deçà duquel on retrouve E₀ et donc le résultat v0.4.0 (Cohen $d = +2.66$) ?

### 1.3 Pourquoi cela compte

Trois lectures distinctes sont possibles selon le résultat :

- **Bande large** ($D^\dagger < 0.04 \le D \le 0.32 < D^*$) : la signature κ est *robuste* à l'intensité du couplage spatial. Le mécanisme — différenciation temporelle locale — n'est pas calibration-dépendant. Renforce le claim v0.5.0 d'un facteur substantiel.
- **Bande étroite** (signal présent uniquement sur $D \in [0.04, 0.16]$) : v0.5.0 a tiré dans une *fenêtre* de validité. Le résultat reste vrai mais son scope public doit être restreint.
- **Effondrement précoce** (signal disparaît dès $D \ge 0.16$) : κ dépend d'un régime de diffusion *modéré*. L'instrument n'est pas portable à des E₁ plus diffusifs. v0.5.0 reste valide à $D = 0.080$, mais l'extrapolation à un E_n générique est interdite.

Dans tous les cas, le résultat est *informatif* : il borne explicitement l'enveloppe de validité du claim v0.5.0, ce qui est précisément ce que demande RELEASE.md v0.5.0 §6 ("Portability beyond E₁").

---

## 2. Décision

Pré-enregistrer un balayage paramétrique de `E1Config.diffusion_coeff` sur une grille de 7 valeurs, mesuré sur un pool unique partagé `[4000-4029]` (30 seeds), avec la chaîne statistique ADR-027 appliquée *indépendamment* à chaque valeur de la grille. Le verdict global est rendu par la conjonction des verdicts par grille-point selon §6.

**Hors-scope explicite** :
- Aucune modification de la topologie de E₁ (Laplacien sur anneau périodique reste fixé) — c'est ADR-035+ qui couvrirait des E₂... (axes structurels alternatifs).
- Aucune modification de M_κ (bit-identique ADR-030).
- Aucune modification du runner public `src/experiments/portability_draw.py` audité par ADR-033 — voir §4 pour le mécanisme d'extension propre.
- Aucune perturbation de la *observation map* (variante 2c écartée — sortirait du cadre dynamique).

---

## 3. Spécification

### 3.1 Grille de diffusion

Grille géométrique 7 points, ancrée sur la valeur calibrée v0.5.0 :

| $D$ | Statut vis-à-vis de la calibration v0.5.0 (ADR-032 §3.4) | Régime attendu |
|---:|---|---|
| `0.005` | sous-bande inférieure ($\bar\sigma^{E_1}/\bar\sigma^{E_0} \approx 0.98$, mesuré) | quasi-E₀ |
| `0.020` | sous-bande inférieure ($\approx 0.93$) | faiblement diffusif |
| `0.040` | sous-bande inférieure ($\approx 0.88$) | diffusif modéré |
| **`0.080`** | **valeur calibrée v0.5.0** ($\le 0.80$, dans la cible) | **référence** |
| `0.160` | hors-bande supérieure (extrapolation × 2) | diffusif fort |
| `0.320` | hors-bande supérieure (extrapolation × 4) | diffusif intense |
| `0.640` | hors-bande supérieure (extrapolation × 8) | régime quasi-homogène |

Justification du choix :
- 4 points sous ou égaux à la calibration v0.5.0 → on cherche $D^\dagger$ et on vérifie la convergence asymptotique vers le régime E₀ (où la signature κ est connue, $d = +2.66$ ADR-030).
- 3 points strictement au-dessus → on cherche $D^*$ et on caractérise la décroissance de l'effet quand le couplage s'intensifie.
- Échelle géométrique (× 2 entre points) → résolution log-uniforme sur 2,1 décades, suffisante pour distinguer effondrement abrupt vs décroissance graduelle.
- Le point `0.080` est inclus *non* comme test mais comme **contrôle de cohérence** : il doit reproduire le résultat v0.5.0 à tolérance ADR-033 près. Discordance = anomalie protocolaire bloquant le verdict v0.6.0.

**Grille figée** : aucun ajout, aucune suppression, aucune ré-échelle après ACCEPTED. Toute modification = nouvelle ADR.

### 3.2 Pool de seeds

| Pool | Usage | Statut |
|---|---|---|
| `[4000-4029]` | Sweep diffusion partagé (30 seeds × 7 valeurs = 210 runs) | **GELÉ** jusqu'à ACCEPTED + implémentation passée |

Justification "pool unique partagé" (vs pool dédié par valeur) : les 7 tests sont *appariés sur les mêmes seeds*. Ce design (i) économise 6 × 30 = 180 seeds par rapport à pools disjoints ; (ii) permet en post-hoc des tests appariés *entre* valeurs de $D$ (test exploratoire, non-décisionnel) ; (iii) élimine la confusion seeds × diffusion. La contrepartie est une corrélation entre les 7 statistiques, qui n'invalide pas la conjonction §6 (chaque verdict par-grille-point est rendu sur sa propre statistique conditionnelle aux seeds).

**Pools antérieurs** restent figés conformément à ADR-031 §4.1, ADR-032 §5.1, RELEASE.md v0.5.0 §6 :
- `[1500-1529]` consommé v0.4.0, `[1530-1599]` réserve κ tail (frozen).
- `[2000-2029]` consommé v0.5.0, `[2030-2099]` réserve E₁ tail (frozen).
- `[2100-2129]` réservé E₂ ADR-032 §4 (frozen).
- `[3000-3009]` calibration E₁ (utilisable mais non re-utilisé ici).

Aucune mesure préliminaire de M_κ sur le pool `[4000-4029]` n'a lieu avant l'ACCEPTED de cette ADR (C5 ADR-032 §2.5).

### 3.3 Conditions appariées par grille-point

Pour chaque $D \in \{0.005, 0.020, 0.040, 0.080, 0.160, 0.320, 0.640\}$ et chaque seed $s \in [4000, 4029]$ :

- Run R (réactif sans mémoire, identique ADR-026 v2.1)
- Run M_κ (memory-1 sur pression locale, identique ADR-030)
- Run S (obs-shuffled control, identique ADR-024 + ADR-033 §11.2 BLAKE2b convention)
- Run M baseline (Markov, identique chaîne σ ADR-027)

Tous les agents sont **bit-identiques** à ceux audités sous tag `audit-passed-v1` (commit `7bf0d9e`). M_κ ne reçoit jamais le paramètre `D` — il observe `O_t` et n'a pas connaissance de la dynamique du champ.

Pour chaque triple $(D, s)$ : calcul de $\delta_\sigma^{R}(s; D)$, $\delta_\sigma^{M_\kappa}(s; D)$, $\delta_\sigma^{S}(s; D)$ (Wasserstein contre M baseline), double reporting Miller-Madow + plug-in (ADR-027). Statistique principale par grille-point :

$$\Delta_s(D) = \delta_\sigma^{M_\kappa}(s; D) - \delta_\sigma^{R}(s; D)$$

### 3.4 Statistique d'inférence par grille-point

Réutilisation **bit-identique** de la chaîne ADR-027, appliquée *indépendamment* à chaque $D$ :
- Wilcoxon apparié $\Delta_s(D)$ vs zéro, branche `greater`
- Cohen $d(D)$ (moyenne / écart-type apparié)
- Double branche entropie (concordance Miller-Madow ↔ plug-in)
- Override `INCONCLUSIVE` par grille-point si une seule branche est positive significativement

Aucune correction de multiplicité (Bonferroni, Holm, BH) n'est appliquée *au niveau du verdict global*. Justification : le verdict global §6 est défini par **conjonction** de verdicts indépendants — $\Pr(\text{tous passent} \mid H_0) \le \alpha^k$ pour $k$ passages indépendants, donc la conjonction est *strictement plus stricte* que chacun des tests pris isolément. Aucune inflation de FWER à corriger. Les verdicts par-grille-point individuels conservent leur seuil ADR-027 ($\alpha = 0.005$, $d \ge 0.5$).

### 3.5 Diagnostics secondaires (informatifs, non-décisionnels)

Reportés dans le verdict JSON v0.6.0 mais ne contribuent pas à la décision §6 :

- **Profil $d(D)$** : courbe de Cohen $d$ vs $\log D$. Forme attendue sous l'hypothèse "bande large" : plateau autour de $D \in [0.02, 0.32]$ avec décroissance aux extrêmes. Forme attendue sous "fenêtre étroite" : pic en $D = 0.080$ avec décroissance rapide.
- **Profil $K_{M_\kappa}(D) - K_R(D)$** : recouvrement de répertoire d'action (diagnostic v0.4.0/v0.5.0 = +23 / +22 cellules). Une décroissance corrélée à celle de $d(D)$ confirmerait que κ et l'expansion d'action sont co-portés ou co-effondrés.
- **Profil $\bar\sigma^{E_1}(D)$ mesuré sur le tirage** : reproductibilité empirique de la calibration ADR-032 §3.4 sur le nouveau pool. Sert d'audit secondaire (différence > 5 % vs `research/calibration_e1.json` = anomalie à investiguer).
- **Test exploratoire de monotonie** : régression de Spearman entre $\log D$ et $d(D)$. Reporté avec son p-value. Aucun seuil décisionnel.
- **Concordance v0.5.0 au point de référence** : $|d(D=0.080)_{v0.6.0} - d_{v0.5.0}| / d_{v0.5.0}$. Reporté. Une discordance > 1 % déclenche l'override INCONCLUSIVE §6.4.

---

## 4. Audit gate hérité (extension propre du runner v0.5.0)

### 4.1 Principe

Le runner public `src/experiments/portability_draw.py` est figé par ADR-033 (tag `audit-passed-v1` sur commit `7bf0d9e`, audit PASS sur commit `c15f313` puis stabilisé sur `49eaf63`/`4bafdac`). **Toute modification de ce runner invalide l'audit gate ADR-033.** Le sweep §3 ne peut donc *pas* se faire en patchant `portability_draw.py` pour exposer un flag `--diffusion-coeff`.

### 4.2 Mécanisme : nouveau script séparé `src/experiments/diffusion_sweep.py`

Un nouveau script est créé qui :

1. **Importe** les briques internes du runner v0.5.0 (`_run_action_sequence`, `_obs_shuffle_seed`, instanciation des agents R / M_κ / S / M, calcul KL/Wasserstein) — *par référence Python*, sans copie de code.
2. **Boucle** sur les 7 valeurs de $D$ et instancie `E1Config(diffusion_coeff=D, ...)` au lieu de la valeur par défaut.
3. **Écrit** un CSV unique `research/h7_kappa_boundary_sweep.csv` avec les 30 × 7 = 210 lignes, colonnes étendues : header v0.5.0 + colonne `diffusion_coeff` ajoutée en première position.
4. **N'altère pas** `portability_draw.py` ni aucun fichier sous `src/agents/` ou `src/analysis/`.

Cette architecture garantit que :
- L'audit gate ADR-033 reste valide *littéralement* sur la même CLI publique.
- Tout auditeur peut re-exécuter `python -m src.experiments.portability_draw --pool audit ...` et retrouver `max |Δ| ≤ 4.5e-11` contre la référence v0.4.0 *même après* publication de v0.6.0.
- Les briques internes étant importées sans copie, toute dérive bit-level entre v0.5.0 et v0.6.0 sur les mêmes briques serait détectée par les ADTs existants (`test_obs_shuffled_agent`, `test_sigma_chain`, `test_portability_draw`).

### 4.3 Audit secondaire obligatoire avant tirage v0.6.0

Avant le tirage `[4000-4029]` du sweep, deux contrôles bloquants :

- **Contrôle de cohérence v0.5.0** : `diffusion_sweep.py` est exécuté en mode `--smoke-test` qui lance UNIQUEMENT le seed 2000 à $D = 0.080$ et compare ligne-à-ligne au CSV `research/h7_kappa_portability.csv` (seed 2000). Tolérances ADR-033 §4 : `atol = 1e-9`, `rtol = 0`, `==` strict sur les colonnes entières. Un écart au-delà de la tolérance bloque le tirage.
- **Audit gate ADR-033 re-confirmé** : `python -m src.experiments.portability_draw --pool audit ...` puis `python -m src.analysis.audit_compare ...` retournent EXIT 0. Confirme que la branche `main` HEAD n'a pas dérivé du tag `audit-passed-v1` sur les briques partagées.

Les deux contrôles sont enregistrés dans le manifest v0.6.0 sous `audit_gate_inheritance_adr_034` avec leurs SHA-256.

### 4.4 ADTs requis pour `diffusion_sweep.py` avant tirage

Les tests adversariaux suivants doivent passer en CI sur le nouveau script :

- `test_diffusion_sweep_smoke_seed_2000` : reproduit le seed 2000 v0.5.0 à $D = 0.080$ sous tolérances ADR-033.
- `test_diffusion_sweep_grid_frozen` : importation de la liste `DIFFUSION_GRID` depuis le module retourne exactement `[0.005, 0.020, 0.040, 0.080, 0.160, 0.320, 0.640]`. Aucune autre valeur acceptée.
- `test_diffusion_sweep_pool_frozen` : la liste `SEED_POOL` retourne `list(range(4000, 4030))`. Aucune intersection avec pools antérieurs.
- `test_diffusion_sweep_no_runner_modification` : `hashlib.sha256(open('src/experiments/portability_draw.py').read()).hexdigest()` == `3c4a7df4c67e162174466e2488ebc8d35676558e870e02c2bbb5cfc2716aa79d` (SHA-256 v0.5.0 figé).
- `test_diffusion_sweep_csv_header` : le CSV de sortie a pour première colonne `diffusion_coeff` puis le header `audit_compare.EXPECTED_HEADER` v0.5.0 *à l'identique*.
- `test_diffusion_sweep_guard_flag` : `diffusion_sweep.py` refuse d'exécuter le tirage complet sans flag `--i-have-read-adr-034`. (Symétrique de la garde ADR-033 sur `portability_draw.py --pool portability`.)

---

## 5. Définition des verdicts

Le verdict v0.6.0 est rendu *uniquement* sur les chiffres pré-enregistrés du sweep `[4000-4029] × {0.005, 0.020, 0.040, 0.080, 0.160, 0.320, 0.640}`, double branche concordante.

Définition d'un **grille-point passant** : $\text{Cohen } d(D) \ge 0.5$ ET $p_{>}(D) < 0.005$ sur les **deux** branches (Miller-Madow corrigé + plug-in naïf), ET $\ge 25/30$ seeds avec $\Delta_s(D) > 0$, ET 0 clip event sur les 30 runs M_κ à $D$.

### 5.1 `KAPPA_ROBUST_PORTABILITY`

**Conditions conjointes** :
- 7/7 grille-points passent (au sens ci-dessus)
- Le profil $d(D)$ est non-trivial (au moins 2 valeurs avec $d \ge 1.0$ sur la grille intérieure $\{0.04, 0.08, 0.16\}$)
- Concordance v0.5.0 au point de référence $D = 0.080$ : $|d_{v0.6.0} - d_{v0.5.0}| / d_{v0.5.0} \le 0.01$

Conséquence : v0.5.0 est confirmée *au-delà* de son point calibré. Déclenche ADR-035 (CAE-Cert v0.1) avec scope élargi à la bande $[0.005, 0.640]$.

### 5.2 `KAPPA_BAND_LIMITED`

**Conditions** : un sous-ensemble **contigu** de grille-points passe, contenant nécessairement $D = 0.080$, mais < 7 au total.

Variantes reportées dans le verdict JSON :
- `band_lower_open` : 0.080 inclus, plus petite valeur passant ≥ 0.040 (signal absent dans le quasi-E₀).
- `band_upper_open` : 0.080 inclus, plus grande valeur passant ≤ 0.160 (signal s'effondre en régime fortement diffusif).
- `band_both_open` : sous-ensemble fermé strictement à l'intérieur (le plus probable a priori sous une hypothèse de fenêtre).

Conséquence : v0.5.0 reste valide. Le scope public κ est borné publiquement à la bande caractérisée. Aucun déclenchement ADR-035 sans nouvelle ADR explicitant la portée certifiable.

### 5.3 `KAPPA_FRAGILE`

**Conditions** : < 3 grille-points passent, **ou** $D = 0.080$ ne passe pas (ce qui invaliderait la cohérence v0.5.0 et déclenche §5.4 INCONCLUSIVE en priorité), **ou** les grille-points passants ne forment pas un ensemble contigu.

Conséquence : la signature κ est calibration-spécifique. v0.5.0 reste publiée mais son scope public est restreint à $D = 0.080 \pm \epsilon$ par amendement de RELEASE.md v0.5.0 §6. Bloque ADR-035. Déclenche ADR de remédiation pour comprendre l'absence de robustesse.

### 5.4 Override INCONCLUSIVE

Prime sur §5.1-§5.3 :

- Total clip events > 0 sur l'ensemble du sweep (210 × 4 agents = 840 runs).
- Discordance Miller-Madow vs plug-in > 1 ordre de grandeur sur Cohen $d$ pour au moins un grille-point.
- Échec d'un ADT §4.4 sur le tirage.
- Discordance > 1 % au point de référence $D = 0.080$ vs v0.5.0 (déclenche audit forensique avant toute interprétation).
- Échec du contrôle de cohérence v0.5.0 §4.3.

Un re-tirage sur pool de réserve (à allouer par ADR de remédiation) est autorisé après publication du diagnostic. **Aucun re-tirage silencieux.**

---

## 6. Contraintes héritées

- **Lexique ADR-020 §3** : aucun terme interdit (intelligence, conscience, cognition, cerveau, révolutionnaire, pensée, émergence, agentivité) dans le code, les ADTs, le manifest, ou la release notes v0.6.0. Les clauses de négation explicites (héritées RELEASE.md v0.5.0 §4 verbatim) restent autorisées.
- **Tolérances ADR-033 §4** : `atol = 1e-9`, `rtol = 0`, `==` strict sur les colonnes entières. Inchangées. S'appliquent au contrôle de cohérence §4.3 et à tout audit comparatif futur impliquant le sweep.
- **Statistique ADR-027** : Wilcoxon apparié, branches `greater` et `less`, $\alpha = 0.005$, $d \ge 0.5$, double reporting Miller-Madow + plug-in. Inchangée. Appliquée *par grille-point*.
- **M_κ ADR-030** : bit-identique. Aucune variante. (Le sweep teste la portabilité de la *signature* sous variation environnementale, pas la robustesse de l'agent à des variantes.)
- **E₁ ADR-032 §3** : structure topologique fixe (Laplacien sur anneau périodique, action kernel non-modulaire). Seul `diffusion_coeff` varie selon §3.1.
- **Pool tail [2030-2099]** : reste FROZEN. Ne peut pas être ouvert sans nouvelle ADR.

---

## 7. Conditions de release v0.6.0

Une release v0.6.0 est admissible *si et seulement si* :

1. ADR-034 = ACCEPTED.
2. `src/experiments/diffusion_sweep.py` ajouté + ADTs §4.4 PASS.
3. Audit gate §4.3 PASS (les deux contrôles).
4. Tirage `[4000-4029] × 7 D` exécuté en une fois, sans interruption manuelle.
5. Verdict v0.6.0 calculé par un nouveau module `src/analysis/verdict_v06.py` (à créer, ne réutilise pas `verdict_v05.py` car la structure est différente : 7 sous-verdicts + verdict global).
6. Manifest `research/MANIFEST.v0.6.0.yaml` scellé avec : SHA-256 du sweep CSV, des 7 sous-verdicts, du verdict global, du nouveau script, des nouveaux ADTs, de l'ADR-034 elle-même, et back-référence aux SHA-256 v0.5.0 inchangés.
7. RELEASE.md mis à jour avec section v0.6.0 selon format hérité v0.5.0 (6 sections).
8. Tag annoté `v0.6.0-h7-κ-boundary` sur le commit du manifest scellé.
9. Push GitHub + GitHub Release + dépôt Zenodo + back-référence DOI dans manifest.

Aucune des étapes 2-9 ne peut être engagée avant que cette ADR-034 ne soit ACCEPTED.

---

## 8. Statut workflow

- **PROPOSED** : 2026-05-10 (commit `3a6d7fd`).
- **ACCEPTED** : 2026-05-10 par décision CEO (V1 ADR-032 §7.1, aucun reviewer requis). Pré-registration figée : grille §3.1, pool §3.2, verdicts §5, conditions §7 ne peuvent plus être modifiés sans nouvelle ADR.
- **TIRAGE AUTORISÉ** : après ADTs §4.4 PASS + audit secondaire §4.3 PASS sur la branche `main` HEAD.
- **VERDICT RENDU** : par exécution déterministe de `verdict_v06.py` sur le CSV produit par `diffusion_sweep.py`. Aucune intervention humaine entre le tirage et le verdict.
- **RELEASE v0.6.0** : conditionnée à §7.

---

## 9. Empreintes (à figer après ACCEPTED + tirage)

| Artefact | SHA-256 |
|---|---|
| `src/experiments/diffusion_sweep.py` | (à figer) |
| `src/analysis/verdict_v06.py` | (à figer) |
| `tests/adt/test_diffusion_sweep.py` | (à figer) |
| `research/h7_kappa_boundary_sweep.csv` | (à figer post-tirage) |
| `research/h7_kappa_boundary_verdict.json` | (à figer post-tirage) |
| `research/MANIFEST.v0.6.0.yaml` | (à figer pre-release) |

ADR-034 elle-même sera versionnée par son SHA git (commit ACCEPTED) et incluse dans `frozen_adr_sha256` du manifest v0.6.0.
