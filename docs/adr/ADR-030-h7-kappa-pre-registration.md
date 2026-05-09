# ADR-030 — Pré-enregistrement H7-κ : agent à mémoire-1 sur pression locale

**Statut** : ACCEPTED
**Date d'ouverture** : 2026-05-09
**Date de gel pré-tirage** : 2026-05-09 (manifest κ v1 SHA `a0322891031ae28b70f51a4f3ec711a854061317c4682ac113d7ab7166a7d4fb`, `tir_authorized: true`, tirage autorisé sur `1500..1529`)
**Décideur** : CEO
**Amont** : ADR-026 v2.1 (chaîne σ figée), ADR-027 (chaîne statistique), ADR-028 §7
(décision Option A), ADR-029 (release v0.3.0)
**Aval** : ADR-031 *seulement si* la chaîne statistique κ diverge de ADR-027
**Pool ressources** : `[1500-1599]`, premiers 30 seeds (`1500..1529`)
**Release effectuée** : `v0.4.0-h7-κ-reverses` (verdict `KAPPA_REVERSES`,
Cohen $d = +2.66$, $p_{>} = 9.31\times 10^{-10}$, 30/30 seeds avec $\Delta_\kappa > 0$, 0 clip events)

---

## 1. Contexte

H7-σ a produit `INVERTED` (d = −0.758, p_less = 1.04e-05) avec un agent réel R
*réactif sans mémoire* (ADR-026 v2.1 §4). H7-κ doit décomposer cette inversion en
testant si **un seul tick de mémoire sur la pression locale précédente** modifie
le couplage stationnaire de R par rapport au baseline Markov M.

Sémantique opérationnelle stricte (ADR-026 v2.1 §7) :
- *mémoire* = état interne déterministe de dimension fixée, mis à jour par une règle
  sans paramètre apprenable ;
- pas de gradient, pas d'entraînement, pas d'optimisation.

## 2. Spécification de l'agent `memory1_agent` (M_κ)

### 2.1. Interface

Conforme à `src.agents.base.Agent` (mêmes signatures que `AdaptiveAgent`,
`ScriptedAgent`).

### 2.2. État

Soit $G = $ `grid_size` (64 dans E₀ par défaut). L'agent porte un unique tampon :

$$ m_t \in [0, 1]^G, \quad m_0 = \mathbf{0} $$

### 2.3. Règle de mise à jour (déterministe, sans paramètre)

Après que l'agent a observé $O_t$ et choisi $A_t$ :

$$ m_{t+1} \leftarrow O_t $$

Aucun coefficient de décroissance, aucun lissage, aucune normalisation. La mémoire
est *strictement* le dernier vecteur de pression observé.

### 2.4. Politique d'action (une ligne, vectorielle, déterministe)

$$ A_t \;=\; \arg\max_{i \in \{0,\dots,G-1\}} \; \bigl( m_t[i] - O_t[i] \bigr) $$

avec **tie-break par plus petit indice** (`int(np.argmax(...))`, comportement par
défaut NumPy, déjà utilisé dans `AdaptiveAgent`).

### 2.5. Lecture sémantique (descriptive uniquement, hors test)

Le terme $m_t - O_t$ est la *chute locale de pression* entre $t-1$ et $t$ (positive
si la pression a baissé). $\arg\max$ sélectionne la cellule où la pression a chuté
le plus fortement : l'agent "verrouille" la cellule la plus dynamiquement décroissante.
Cas limite à $t=0$ : $m_0 = 0 \Rightarrow A_0 = \arg\max(-O_0) = \arg\min(O_0)$, soit
la cellule la moins comprimée — comportement déterministe défini.

### 2.6. Cas dégénérés explicitement définis

| Cas | Définition |
|---|---|
| $m_t = O_t$ exactement | $\arg\max(\mathbf{0}) = 0$ (premier indice) |
| Plateau $\{m_t - O_t\}$ avec plusieurs maxima | premier indice (NumPy `argmax`) |
| `observe()` retourne $O_t$ hors $[0,1]$ | exception `ValueError` (interface) |

### 2.7. Ce que la politique ne fait PAS

- ne lit jamais $A_{t-1}$ (pas de mémoire d'action)
- ne lit jamais l'horizon ni le tick courant
- n'utilise pas de bruit (déterminisme bit-identique à seed donné)
- ne calcule aucun gradient ni produit scalaire pondéré
- n'a pas d'hyperparamètre (ce qui rend le pre-reg auto-suffisant)

## 3. Pré-enregistrement statistique

### 3.1. Réutilisation intégrale de la chaîne ADR-027

| Élément | Valeur |
|---|---|
| Test | `scipy.stats.wilcoxon`, `zero_method="wilcox"` |
| Branches | `alternative="greater"` ET `alternative="less"` (procéduralement two-sided, ADR-026 v2.1) |
| α | 0.005 par branche (régions disjointes ⇒ pas de Bonferroni) |
| Seuil Cohen d | $|d| \ge 0.5$ pour bins directionnels ; $|d| < 0.2$ pour `FEEDBACK_ONLY` |
| n | 30 (seeds `1500..1529`) |
| Constantes E₀ | `T_warmup = 5_000`, `T_stat = 50_000`, `B = 64`, `P ∈ [0,1]` strict |
| Entropies | Miller-Madow (primaire) + plug-in (transparence) |

### 3.2. Quantité testée

Pour chaque seed $s$, calculer :

$$ \Delta_s \;=\; \delta_\sigma^{M_\kappa}(s) - \delta_\sigma^{R}(s) $$

où $\delta_\sigma^X(s) = D_{KL}(P_X(s) \,\|\, P_M(s)) - D_{KL}(P_S(s) \,\|\, P_M(s))$
(même métrique que H7-σ, §3 ADR-027).

R, S, M sont **rejoués bit-identique aux seeds [1400-1429]** ? **Non** — R, S, M sont
*re-simulés* sur les mêmes seeds `1500..1529` que M_κ, pour garantir l'appariement
strict seed-à-seed et préserver la garantie hors-échantillon. R lui-même est figé
(SHA inscrits dans `H7_SIGMA_FREEZE_MANIFEST.json` v3, immuable).

### 3.3. Verdicts (4 bins symétriques)

| Verdict | Condition | Sémantique opérationnelle |
|---|---|---|
| `KAPPA_REINFORCES` | $d \le -0.5$ ∧ p_less < 0.005 | M_κ est *encore plus inversé* que R ⇒ la mémoire-1 amplifie le couplage stabilisateur |
| `KAPPA_REVERSES`   | $d \ge +0.5$ ∧ p_greater < 0.005 | M_κ revient vers la zone S ⇒ la mémoire-1 détruit le couplage stabilisateur |
| `KAPPA_NEUTRAL`    | $\|d\| < 0.2$ ∧ p_greater ≥ 0.005 ∧ p_less ≥ 0.005 | mémoire-1 inopérante ⇒ l'inversion σ n'est pas due à l'absence de mémoire |
| `KAPPA_INCONCLUSIVE` | autre | rerun ou refonte (pool reste 70 seeds restants pour remediation seulement) |

### 3.4. Override

Identique à ADR-027 : `total_clip_events > 0` ou `n_post_drop < 25` force
`KAPPA_INCONCLUSIVE` indépendamment de p et d.

### 3.5. Concordance primaire/transparence

Rapporter les deux entropies. Si `verdicts_agree == false`, le verdict final est
`KAPPA_INCONCLUSIVE` (aligne sur ADR-026 v2.1 §3).

## 4. Tests ADT (`tests/adt/test_memory1_agent.py`)

Minimum requis avant gel SHA :

| ID | Test | Critère pass |
|---|---|---|
| ADT-κ-1 | déterminisme | deux instances même seed → trajectoires d'actions bit-identiques sur 1000 ticks |
| ADT-κ-2 | conformité interface | `select_action(O)` retourne `int` ∈ `[0, G)`, `reset()` remet `m` à $\mathbf{0}$ |
| ADT-κ-3 | mise à jour mémoire | après `select_action(O_t)`, l'état interne `m` = `O_t` (égalité bit-identique) |
| ADT-κ-4 | cas $t=0$ | sur $O_0$ donné, $A_0 = \arg\min(O_0)$ |
| ADT-κ-5 | rejet observation invalide | `observe` shape ≠ $(G,)$ ou hors $[0,1]$ → `ValueError` |

Tous doivent passer avant freeze SHA-256 du fichier agent.

## 5. Plan de gel (avant tout tirage)

1. Implémenter `src/agents/memory1_agent.py`.
2. Implémenter `tests/adt/test_memory1_agent.py` (5 tests min).
3. `pytest tests/adt/test_memory1_agent.py -v` → 5/5 vert.
4. Calculer SHA-256 de `memory1_agent.py` + `test_memory1_agent.py`.
5. Geler ces SHA dans `H7_KAPPA_FREEZE_MANIFEST.json` (v1) avec :
   - constantes E₀ (héritées de `H7_SIGMA_FREEZE_MANIFEST.json` v3) ;
   - SHA des 4 ADRs amont (026 v2 + 026 v2.1 + 027 + 028) + ADR-030 elle-même ;
   - SHA du runner κ (à écrire) et de l'adjudicateur κ (réutilise `sigma_adjudicator.py`
     v post-patch SHA `f6c5aeff…` si la sortie JSON est compatible, sinon écrire
     `kappa_adjudicator.py` séparé).
6. Tirer seeds `1500..1529` (30 seeds, ~3 min wall-clock à constantes égales).
7. Adjudication → `h7_kappa_verdict.json` + `h7_kappa_run_results.csv`.
8. Si verdict ∈ {REINFORCES, REVERSES, NEUTRAL} → release v0.4.0 selon protocole
   ADR-029 §7 (mêmes 13 étapes, mêmes garanties).
9. Si `INCONCLUSIVE` → ADR de remediation (pas de release prématurée).

## 6. Garde-fous doctrinaux

- **Vocabulaire admis ici** : *mémoire* (op def §2.2), *état interne*, *politique
  conditionnée*, *gradient temporel local* (descriptif §2.5).
- **Vocabulaire toujours banni** (ADR-026 v2.1 §7, inchangé) : `apprentissage`,
  `entraînement`, `cognition`, `intention`, `prédiction` (sens cognitif),
  `comprend`, `internalise`.
- **Ce pré-enregistrement ne ré-ouvre PAS H7-σ** : v0.3.0 reste un résultat
  terminal et figé.
- **Le pool [1500-1599] ne sera tiré qu'après freeze SHA complet** (étapes 1-5
  ci-dessus). Toute déviation matérielle = nouveau manifest, nouvelle ADR.

## 7. Conséquences procédurales

- ADR-030 passe en `ACCEPTED` au moment du gel SHA (pas avant).
- Si la chaîne statistique nécessite une modification (ex. ajout d'une métrique),
  rédiger ADR-031 *avant* tirage.
- Le code de `memory1_agent.py` sera **public** dans le repo principal (contrairement
  au code H7 σ qui reste privé jusqu'à v0.4.0 selon ADR-029 §4.4) : la mémoire-1
  est sémantiquement publiable car elle ne révèle aucun secret de R.

---

*Brouillon ouvert le 2026-05-09. Statut DRAFT jusqu'au passage 5/5 ADT et au calcul
des SHA. Aucun tirage autorisé tant que le statut n'est pas ACCEPTED.*
