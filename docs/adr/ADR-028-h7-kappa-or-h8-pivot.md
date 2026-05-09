# ADR-028 — Suite de H7-σ INVERTED : décomposition (H7-κ) ou pivot (H8) ?

**Statut** : ACCEPTED (Option A — H7-κ retenue)
**Date d'ouverture** : 2026-05-09
**Date de décision** : 2026-05-09
**Décideur** : CEO
**Bloque** : tirage du pool réservé `[1500-1599]` jusqu'à freeze ADR-030 (pre-reg H7-κ)
**Référence amont** : ADR-029 §6 (option ouverte), ADR-026 v2.1 (verdicts disjoints)
**Verdict de fond intégré** : `H7_SIGMA_INVERTED` (d = −0.758, p_less = 1.04e-05, n=30, hors-échantillon)
**Décision** : **Option A — H7-κ : décomposition de l'inversion via agent à mémoire-1**

---

## 1. Contexte

H7-σ a produit un signal directionnel **inverse** de la prédiction pré-enregistrée : la
trajectoire de pression de l'agent réel R, mesurée par sa divergence stationnaire au
baseline markovien M, est **plus proche** de M que celle du contrôle shuffled S.
Sémantique opérationnelle stricte (ADR-026 v2.1 §7) : *couplage inversé*, ou
*stabilisation par feedback*.

Ce signal n'épuise pas le programme H7. Il en redéfinit le sol :
- E₀ + agent réactif minimal (`scripted_agent` + boucle d'action) suffit déjà à produire
  une réduction structurelle de la divergence stationnaire.
- La prédiction initiale (R divergerait de M *plus* que S) supposait que l'agent réactif
  serait neutre vis-à-vis de la structure stationnaire ; cette supposition est
  empiriquement fausse.

La question ouverte est donc : **que mesure-t-on ensuite ?**

Le pool `[1500-1599]` (100 seeds réservés, gelés depuis ADR-026 v2 §2) reste la seule
ressource non-brûlée encore ré-utilisable pour un test directionnel hors-échantillon de
même calibre que le main run. Le **brûler sans pré-enregistrement explicite** détruirait
la chaîne de garantie pré-enregistrée → out-of-sample qui fait la valeur épistémique de
l'instrument. Cette ADR-028 est le pré-enregistrement obligatoire avant tout tirage.

## 2. Décision à prendre

Choisir **exactement une** des deux options ci-dessous (A ou B) avant tout tirage de seed
dans `[1500-1599]`. Une troisième option C (clôture sans suite) est possible et explicitée
en §5.

Les deux options partagent :
- même environnement gelé E₀ (fingerprint `406ce26e…`)
- même chaîne statistique que ADR-027 (Wilcoxon apparié, α = 0.005, seuil Cohen |d| = 0.5,
  bin FEEDBACK_ONLY = |d| < 0.2)
- mêmes constantes de mesure (T_warmup=5_000, T_stat=50_000, B=64, P∈[0,1], Miller-Madow
  primaire, naive transparence)
- même protocole de gel manifest avant tirage
- même ressource (pool `[1500-1599]`, n=30 tirés du début du pool ; reste 70 disponibles
  pour remediation seulement)

Elles diffèrent sur **ce qui change dans l'agent**, **ce qui est mesuré**, et
**ce qui constituerait un "couplage trouvé"**.

---

## 3. Option A — H7-κ : décomposition de l'inversion

### 3.1. Hypothèse

L'inversion observée en σ est *un effet de boucle réactive sans mémoire*. Un agent doté
d'un **état interne minimal** (mémoire de trajectoire, dimension ≥ 1) doit produire une
divergence stationnaire **différente** de celle du `scripted_agent` réactif, dans une
direction prédite par la nature de la mémoire :

- mémoire alignée sur l'invariant E₀ ⇒ **renforcement** de l'inversion (R encore plus
  proche de M que S)
- mémoire orthogonale ⇒ **annulation** de l'inversion (R revient vers la zone S)

Le κ pré-enregistré dans ADR-026 v2 (decomposition de la divergence en composantes
attribuables à l'invariant) est ré-orienté : κ ne décompose plus une *expansion* attendue
mais une *contraction* observée.

### 3.2. Pre-registered prediction

Soit M_κ un agent à mémoire-1 sur la trajectoire de pression locale. Notons
δ_σ^M_κ = D_KL(P_{M_κ} ‖ P_M) − D_KL(P_S ‖ P_M).

Prédiction stricte (à figer avant tirage) :
$$ \delta_\sigma^{M_\kappa} \le \delta_\sigma^R \quad \text{(inversion renforcée)} $$
testée par Wilcoxon apparié `less` sur (δ_σ^M_κ − δ_σ^R), α = 0.005, seuil |d| ≥ 0.5.

### 3.3. Critère de succès (ce qui clôt H7-κ)

| Branche | δ_σ^M_κ vs δ_σ^R | Cohen d | p | Verdict |
|---|---|---|---|---|
| `KAPPA_REINFORCES` | M_κ encore plus inversé | d ≤ −0.5 | p_less < 0.005 | **mémoire amplifie l'inversion** ⇒ couplage opérationnel via mémoire-1 |
| `KAPPA_NEUTRAL` | indistinct | |d| < 0.2 | p_less ≥ 0.005 ∧ p_greater ≥ 0.005 | mémoire-1 inopérante ⇒ inversion = effet pur de réactivité |
| `KAPPA_REVERSES` | M_κ revient vers S | d ≥ +0.5 | p_greater < 0.005 | **mémoire détruit l'inversion** ⇒ inversion = artefact de simplicité agent |
| `KAPPA_INCONCLUSIVE` | autre | | | rerun ou abandon |

### 3.4. Ce que A *ne fait pas*

- ne ré-ouvre pas σ (verdict `INVERTED` reste publié et figé en v0.3.0)
- ne change pas E₀
- ne ré-active pas le vocabulaire banni (mémoire ici = état interne dim≥1, op def)
- n'introduit pas d'apprentissage (M_κ est paramétré, pas entraîné)

### 3.5. Coûts

- 1 nouvel agent à figer (`memory1_agent`) + tests ADT
- 30 seeds du pool `[1500-1599]` brûlés
- 1 main run (~3 min wall-clock à constantes égales) + adjudication
- 1 release (v0.4.0) si verdict décisif (REINFORCES, NEUTRAL ou REVERSES)

### 3.6. Risques

- **Pertinence** : si κ est neutral, on aura brûlé 30 seeds pour un non-résultat
  publiable mais peu informatif.
- **Sur-spécification** : mémoire-1 trajectoire de pression est *un* choix parmi
  plusieurs (mémoire-1 action, mémoire-1 état d'environnement, mémoire-k…). Le choix
  doit être figé dans cette ADR avant tirage.

---

## 4. Option B — H8 : pivot vers une thermodynamique de l'information

### 4.1. Hypothèse

L'inversion en σ révèle que la métrique de divergence stationnaire n'est pas la bonne
sonde : tout agent fermant une boucle locale réduit cette divergence *par construction*
(stabilisation), indépendamment de toute structure d'intérêt. Il faut une métrique qui
distingue **stabilisation triviale** (réduction d'entropie locale) de **structuration**
(réduction d'entropie *conditionnelle au passé*).

Sonde proposée : **taux d'entropie** $h(P)$ d'ordre k vs. entropie de Shannon
$H(P)$ stationnaire. Un agent qui stabilise sans structurer fait baisser H mais laisse
h ≈ H (passé non-informatif). Un agent qui structure fait baisser h *strictement plus*
que H (passé informatif).

### 4.2. Pre-registered prediction

Notons $\Delta_R = H(P_R) - h_k(P_R)$ et $\Delta_S = H(P_S) - h_k(P_S)$ pour k=2 (à figer).

Prédiction stricte :
$$ \Delta_R - \Delta_S > 0 $$
(R extrait plus d'information du passé que S), testée par Wilcoxon apparié `greater`,
α = 0.005, seuil |d| ≥ 0.5. Test miroir `less` formalisé pré-tirage (analogue ADR-026 v2.1)
pour bin INVERTED.

### 4.3. Critère de succès (ce qui clôt H8)

| Verdict | Δ_R − Δ_S | Cohen d | p | Sémantique |
|---|---|---|---|---|
| `H8_STRUCTURAL` | > 0 | d ≥ +0.5 | p_greater < 0.005 | **structuration trouvée** : passé informatif chez R, pas chez S |
| `H8_INVERTED` | < 0 | d ≤ −0.5 | p_less < 0.005 | passé *moins* informatif chez R que S — anti-structuration, à interpréter |
| `H8_FEEDBACK_ONLY` | ≈ 0 | |d| < 0.2 | p ≥ 0.005 | passé indistinctement (non-)informatif ⇒ stabilisation σ est purement markovienne |
| `H8_INCONCLUSIVE` | autre | | | rerun ou refonte |

### 4.4. Ce que B *ne fait pas*

- n'invalide pas v0.3.0 (σ reste un résultat publié, juste re-cadré comme *baseline*)
- ne change pas E₀
- ne réutilise pas la chaîne σ : H8 a sa propre métrique et son propre code (à écrire,
  privé jusqu'à v0.5.0)

### 4.5. Coûts

- nouvelle métrique à implémenter (`entropy_rate.py`) + ADT (≥5 tests)
- 30 seeds du pool `[1500-1599]` brûlés
- 1 main run + adjudication
- 1 ADR de pré-enregistrement séparée (équivalent ADR-026 + ADR-027 pour H8)
- 1 release (v0.4.0 ou v0.5.0 selon ordonnancement)

### 4.6. Risques

- **Délai** : H8 nécessite au minimum 1 ADR de pré-reg + 1 cycle de dev/freeze avant
  tirage (vs. A qui peut tirer dans la semaine).
- **Risque de confondu** : si Δ_R > Δ_S parce que R explore moins d'états (support plus
  petit), on confond structuration et concentration. Contrôle nécessaire :
  rapporter $|supp(P_R)|$, $|supp(P_S)|$ et discuter.
- **Coût d'opportunité** : abandonner κ avant de l'avoir testé revient à laisser une
  question ouverte au programme.

---

## 5. Option C — Clôture sans suite

Publier v0.3.0 comme résultat terminal de la branche H7. Geler `[1500-1599]`
définitivement. Ne pas ouvrir H7-κ ni H8. Réserver toute capacité expérimentale future
à un programme à re-définir.

Avantage : préserve la ressource. Inconvénient : laisse l'inversion non-décomposée et
ferme la question scientifique posée par v0.3.0.

Cette option est listée pour complétude — elle requiert une décision CEO explicite et
n'est pas l'option par défaut.

---

## 6. Critères de discrimination A vs B (aide à la décision)

| Critère | Option A (κ) | Option B (H8) |
|---|---|---|
| Délai jusqu'à main run | ~1 semaine | ~3-4 semaines |
| Réutilise infra σ | oui (même métrique, agent change) | non (nouvelle métrique) |
| Risque non-résultat | NEUTRAL plausible (~30 %) | INCONCLUSIVE plausible (~25 %) |
| Information si succès | confirme/réfute mémoire-1 comme cause | distingue stabilisation vs structuration |
| Information si échec | inversion = pur effet réactif (clôt programme) | métrique σ disqualifiée comme sonde unique |
| Engagement doctrinal | léger (extension d'agent) | lourd (nouvelle hypothèse pré-enregistrée) |
| Coût en seeds | 30 / 100 du pool κ | 30 / 100 du pool κ (ou autre pool à allouer) |
| Réversibilité | haute | basse |

## 7. Décision (CEO, 2026-05-09)

- [x] **Option A — H7-κ** : geler `memory1_agent` + ré-orienter κ vers décomposition de
  l'inversion. Tirer 30 seeds de `[1500-1599]`. Délai cible : v0.4.0 sous ~3 semaines.
- [ ] ~~Option B — H8~~ (différée ; pourra être ré-ouverte conditionnellement au verdict κ).
- [ ] ~~Option C — Clôture~~ (rejetée).

**Rationale de la décision** :
1. *Information par seed* : κ teste *directement* la cause hypothétique de l'inversion
   (réactivité-sans-mémoire). Tous les bins de verdict (REINFORCES / NEUTRAL / REVERSES)
   sont actionnables.
2. *Réutilisation de l'instrument* : même métrique, même adjudicateur, même pipeline σ.
   Délai court, risque procédural minimal.
3. *Conditionnalité H8* : si κ donne `NEUTRAL`, ce non-résultat *fort* justifie le pivot
   B avec un cadrage enrichi. H8 reste accessible *après* κ, pas avant.

## 8. Conséquences (Option A actée)

1. **ADR-030 à rédiger** : pre-reg H7-κ détaillée incluant :
   - choix exact de la mémoire-1 (variable d'état mémorisée, dimension, mise à jour) ;
   - freeze code `memory1_agent` (SHA-256) ;
   - ≥ 5 tests ADT (déterminisme, idempotence, conformité interface `Agent`) ;
   - manifest gelé pré-tirage (analogue `H7_SIGMA_FREEZE_MANIFEST.json`).
2. **ADR-031 (optionnelle)** : seulement si la chaîne statistique κ diverge de ADR-027
   (sinon ré-utilisation directe).
3. **Pool `[1500-1599]`** : reste **gelé** jusqu'au freeze de ADR-030. Tirage prévu :
   30 seeds (1500-1529). Solde 70 seeds réservés remediation.
4. **Vocabulaire** : `mémoire` admis désormais avec op def stricte (état interne dim ≥ 1,
   mise à jour déterministe). Reste banni : `apprentissage`, `entraînement`, `prédiction
   cognitive`. Le `memory1_agent` est *paramétré*, pas entraîné.
5. **Release cible** : v0.4.0-h7-κ-{reinforces|neutral|reverses|inconclusive} sous
   ~3 semaines, avec même rigueur de chaîne que v0.3.0.

## 9. Notes doctrinales

- Aucune des options ne ré-active le vocabulaire banni (ADR-026 v2.1 §7).
- Aucune des options ne ré-ouvre H7-σ (verdict figé v0.3.0).
- Aucune des options ne brûle le pool `[1500-1599]` au-delà de 30 seeds (les 70 restants
  restent disponibles uniquement pour remediation, pas pour exploration libre).
- Toute déviation matérielle de cette ADR (changement de constantes, d'agent, de métrique
  après freeze) déclenche une réécriture de manifest et une ré-adjudication, comme pour
  ADR-026 v2.1.

---

*Brouillon ouvert le 2026-05-09 par l'opérateur (assistant) à la demande du CEO. Aucun
gel SHA-256 tant que l'option n'est pas choisie. À figer avant tout tirage dans
`[1500-1599]`.*
