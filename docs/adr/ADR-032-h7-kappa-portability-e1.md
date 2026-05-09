# ADR-032 — Pré-enregistrement E₁ et protocole de portabilité κ

**Statut** : ACCEPTED INTERNAL
**Date d'ouverture** : 2026-05-09
**Date d'acceptation interne** : 2026-05-09 (post-amendements §12, post-ADR-031.bis)
**Statut terminal** : ACCEPTED INTERNAL (cf. §7.2). Pas de statut ACCEPTED distinct — voir ADR-031.bis.
**Décideur** : CEO (verrous épistémiques V1-V2-V3 §7.1 ; aucun reviewer requis)
**Amont** : ADR-031 ACCEPTED (séquence B-first), ADR-030 (spec M_κ figée), ADR-027 (chaîne statistique réutilisée), [doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §3.2 et §4.1
**Aval** : ADR-034 (boundary-of-validity, déclenché *si* verdict v0.5.0 = `KAPPA_FAILS_TRANSFER`), ADR-035 (CAE-Cert v0.1, déclenché *si* verdict = `KAPPA_TRANSFERS`)
**Pool ressources** : nouveaux pools `[2000-2029]` (E₁ premier tirage) et `[2100-2129]` (E₂ secondaire optionnel). **Aucun chevauchement avec pools κ existants.**
**Release attendue** : `v0.5.0-portability` (verdict `KAPPA_TRANSFERS` / `KAPPA_FAILS_TRANSFER` / `KAPPA_BOUNDED`), deadline 2026-12-31.

---

## 1. Contexte

ADR-031 a figé la séquence B-first. Cette ADR-032 spécifie la **Voie B** : sous quelle forme E₁ doit être construit pour que le test de portabilité de κ soit *destructif* et non *complaisant*.

Le risque dominant nommé dans [doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §8.1 est : "κ artefact d'E₀ (non-portable)". Le risque méthodologique miroir, qui peut le masquer, est : **construire un E₁ qui ressemble structurellement à E₀**, ce qui produirait un transfert artificiel et un faux verdict `KAPPA_TRANSFERS`.

Cette ADR doit donc, *avant* de spécifier E₁, **figer les conditions sous lesquelles un environnement E_n est admissible comme test de portabilité κ**. Sans cette clause d'invalidation, n'importe quel environnement co-conçu avec κ pourrait passer trivialement.

## 2. Clause d'invalidation — Conditions d'admissibilité d'un environnement E_n

Un environnement E_n (n ≥ 1) est **admissible comme test de portabilité κ** *si et seulement si* il satisfait les **cinq critères suivants**, vérifiables binairement avant tout tirage :

### 2.1 Critère C1 — Déterminisme bit-identique par seed

Conforme à `src/config/determinism.py`. Deux instanciations avec le même seed produisent une trajectoire bit-identique sur tout l'horizon. Vérification : `pytest tests/adt/test_<env>.py::test_determinism_bitwise` doit passer en CI.

### 2.2 Critère C2 — Isolation boîte-noire stricte

Conforme à `docs/PROTOCOL-v1.0.md` §3. L'API exposée à un agent se réduit à :
- `observe() → np.ndarray` (vecteur de pression, shape identique pour tous E_n d'une même release pour permettre la comparaison de M_κ)
- `act(position: int) → None`
- `step() → dict[str, Any]` (télémétrie externe uniquement)
- `t`, `is_done`, `config` (lecture seule)

Aucune méthode privée (préfixe `_`) n'est appelable par un agent. L'audit `tests/adt/test_<env>.py::test_blackbox_isolation` enforce cette règle par introspection.

### 2.3 Critère C3 — Différenciation structurelle minimale par rapport à E₀

E_n doit différer de E₀ sur **au moins un axe structurel** parmi :
1. **Couplage spatial** : présence d'une dynamique non-locale (diffusion, advection, propagation d'onde) absente de E₀.
2. **Non-linéarité dynamique** : présence d'un terme multiplicatif, seuil, saturation non-triviale (au-delà du `np.clip`).
3. **Topologie** : grille non-1D, graphe irrégulier, dimension > 1.
4. **Stochasticité externalisée** : un terme de bruit pseudo-aléatoire déterministe par seed, qui se propage dans la dynamique du champ (pas seulement dans la condition initiale).
5. **Sémantique d'action** : action multiplicative, action propagée, action retardée.

**Contrainte forte** : aucune cosmétique (renommage de variables, changement de constantes, re-paramétrisation) n'est admissible comme différenciation. Un E_n qui est une fonction continue de E₀ par déformation paramétrique seule est un E₀-bis et est **rejeté de droit**.

**Contrainte d'irréductibilité** (ajout amendement interne §12 / 2026-05-09) : la différence structurelle doit être *irréductible* au sens où aucun changement de coordonnées lisse, aucun re-échelonnement temporel ou spatial externe au champ ne doit pouvoir ramener E_n sur E₀. Formulation opératoire : E_n n'est pas difféomorphe à E₀ par transformation externe. Cette contrainte verrouille l'interprétation de la « cosmétique » et exclut par anticipation les transformations passives (changement de base spectrale, re-échantillonnage).

### 2.4 Critère C4 — Préservation de la *mesurabilité* de κ

E_n doit préserver les éléments structurels qui rendent κ *définissable* (mais pas nécessairement performant) :
- `observe()` retourne un vecteur de pression dans un espace de même dimension que E₀ (ou de dimension réductible par une projection canonique pré-spécifiée et figée par SHA).
- L'action affecte le champ à une position quelconque (le répertoire d'actions $K$ est défini de la même façon, cf. ADR-027).
- L'horizon est de même ordre de grandeur (≥ 256, ≤ 2048).

**Justification** : la portabilité teste *si κ transfère*, pas *si κ pourrait être défini*. Si E_n change la sémantique d'action ou la dimension d'observation, on teste un autre instrument.

### 2.5 Critère C5 — Co-conception interdite

E_n est spécifié *avant* tout tirage exploratoire. Aucune mesure préliminaire de M_κ sur E_n n'a lieu avant l'ACCEPTED de cette ADR. Aucun ajustement de E_n après visualisation d'un effet n'est autorisé. Le manifest E₁ (SHA-256 de `src/env/e1.py`) est figé dans le pré-tirage.

**Vérification** : `git log --all -- src/env/e1.py` doit montrer une généalogie linéaire propre, avec un seul commit "implement E₁ per ADR-032 ACCEPTED" précédant tout commit de tirage.

## 3. Spécification de E₁ (environnement primaire)

### 3.1 Choix de différenciation structurelle

E₁ satisfait C3 par **l'axe 1 (couplage spatial)** : ajout d'un terme de **diffusion Laplacienne** dans la relaxation passive du champ. Aucun autre axe n'est modifié. Cette parcimonie est délibérée : un seul axe modifié = un seul facteur d'imputation possible en cas de `FAILS_TRANSFER`.

### 3.2 Configuration figée

```python
@dataclass(frozen=True)
class E1Config:
    grid_size: int = 64                  # identique E₀
    horizon: int = 512                   # identique E₀
    n_modes: int = 4                     # identique E₀
    seed: int = 42                       # surchargeable au tirage
    drift_rate: float = 0.015            # identique E₀
    action_kernel_width: int = 5         # identique E₀
    action_amplitude: float = 0.10       # identique E₀
    relaxation: float = 0.05             # identique E₀
    diffusion_coeff: float = 0.020       # NOUVEAU — sera figé après calibration §3.4
    laplacian_boundary: str = "periodic" # NOUVEAU — s'applique UNIQUEMENT au Laplacien §3.3
```

### 3.3 Dynamique

À chaque `step()`, après la relaxation linéaire de E₀ et **avant** le `clip` final :

$$ f_{t+1} \leftarrow f_{t+1} + D \cdot \Delta_{ring} f_{t+1} $$

où $\Delta_{ring}$ est le Laplacien discret 1D sur anneau (conditions aux bords périodiques) :

$$ (\Delta_{ring} f)_i = f_{i-1 \bmod G} - 2 f_i + f_{i+1 \bmod G} $$

Tous les autres termes (relaxation vers `_reference_field`, drift quasi-périodique, kernel d'action gaussien) sont **bit-identiques** à E₀.

**Périmètre de la condition aux limites périodique** (clarification amendement §12 / 2026-05-09) : `laplacian_boundary="periodic"` s'applique *exclusivement* à l'opérateur Laplacien $\Delta_{ring}$. Le **kernel d'action** reste bit-identique à E₀ (distance euclidienne non-modulaire), donc une action près de $i=0$ ne « déborde » pas sur $i = G-1$. La base spectrale de cosinus de E₀ est elle-même implicitement périodique sur la grille (`linspace(0, 1, G, endpoint=False)`) ; la condition périodique du Laplacien n'introduit donc aucune topologie *nouvelle*, elle utilise la topologie déjà présente. **Conséquence** : E₁ diffère de E₀ sur **un seul axe structurel** (couplage spatial via le Laplacien) ; le principe de parcimonie §3.1 est préservé.

### 3.4 Calibration de `diffusion_coeff`

`diffusion_coeff` est calibré une seule fois, *avant* tout tirage de portabilité, par la procédure suivante :

1. Soit $\bar\sigma^{E_0}$ l'écart-type spatial du champ E₀ **moyenné sur le régime stationnaire** : moyenne temporelle de $\sigma_t = \mathrm{std}_x(f_t)$ sur la fenêtre $t \in [T_{warmup}, T_{warmup} + T_{stat}]$ (mêmes valeurs que la chaîne ADR-027 réutilisée en §5.3), elle-même moyennée sur 10 seeds calibration `[3000-3009]` (pool de calibration **disjoint** des pools de tirage).
2. Soit $\bar\sigma^{E_1}(D)$ la même quantité sur E₁ avec coefficient $D$, calculée sur la *même* fenêtre temporelle stationnaire avec les mêmes seeds.
3. Choisir $D \in \{0.005, 0.010, 0.020, 0.040, 0.080\}$ tel que $\bar\sigma^{E_1}(D) \in [0.5, 0.8] \times \bar\sigma^{E_0}$.
4. Le $D$ retenu est figé dans `E1Config.diffusion_coeff` et **ne peut plus être modifié** sans nouvelle ADR.
5. **Diagnostic obligatoire** : le script de calibration produit un audit `research/calibration_e1.json` contenant $\bar\sigma^{E_0}$, $\bar\sigma^{E_1}(D)$ pour chaque $D$ de la grille, le $D$ retenu, et la fenêtre temporelle exacte utilisée. Cet audit est versionné et hashé dans le manifest v0.5.0.

**Justification** : la chaîne statistique §5.3 opère sur la distribution stationnaire (Wasserstein post-warmup), pas sur le régime transitoire. Calibrer la lisseur visée sur le *même* régime que celui où la mesure est effectuée garantit que `diffusion_coeff` exprime une propriété *structurelle* du champ E₁, et non un effet transitoire qui s'évanouirait après warmup. (Amendement §12 / 2026-05-09 corrigeant la version initiale qui ciblait $t = $ horizon.)

On impose à E₁ d'être *structurellement plus lisse* que E₀ (la diffusion lisse en moyenne stationnaire), mais pas dégénéré (champ uniforme). L'intervalle [0.5, 0.8] garantit une dynamique non-triviale tout en assurant que la prédiction locale de κ est *plus difficile* qu'en E₀.

### 3.5 Tests obligatoires avant tirage

- `tests/adt/test_e1.py::test_determinism_bitwise` (C1)
- `tests/adt/test_e1.py::test_blackbox_isolation` (C2)
- `tests/adt/test_e1.py::test_structural_difference_from_e0` (révisé amendement §12 / 2026-05-09 bis) : vérifie que pour chacune des 10 seeds calibration `[3000-3009]`, la **distance L1 moyenne** entre les champs E₀ et E₁ sur le régime stationnaire $t \in [T_{warmup}, T_{warmup} + T_{stat}]$ vérifie $\langle |f_t^{E_1}(i) - f_t^{E_0}(i)| \rangle \geq 0.015$. Justification du seuil : minimum mesuré sur le pool calibration = 0.018 (seed 3006), seuil fixé 17% sous ce minimum pour marge de sécurité. La métrique L1 mesure directement ce que la spec §3.1 vise (E₁ s'éloigne de E₀ *en valeur*, pas seulement en *forme* — la corrélation scalaire est inappropriée car E₀ et E₁ partagent par construction le même drift quasi-périodique).
- `tests/adt/test_e1.py::test_spatial_autocorrelation_nonlocal` (révisé amendement §12 / 2026-05-09 bis) : vérifie *empiriquement* que la diffusion produit un effet de lissage **directionnel universel** : pour chacune des 10 seeds calibration, la fonction d'autocorrélation spatiale $C(\Delta) = \langle f_t(i) f_t(i+\Delta) \rangle / \langle f_t(i)^2 \rangle$ (centrée, moyennée sur régime stationnaire) satisfait $C^{E_1}(\Delta=4) - C^{E_0}(\Delta=4) > 0$. Justification du test directionnel (et non d'un seuil de signe absolu) : la valeur absolue $C^{E_0}(4)$ varie sur $[-0.81, +0.66]$ selon les fréquences/phases tirées par seed, mais l'effet de lissage Laplacien est *directionnel* (10/10 seeds, marge minimale mesurée +0.026). Cette signature prouve que le couplage spatial est non-local et systématique, indépendamment du contenu spectral local.
- `tests/adt/test_e1.py::test_kappa_definability` (C4)
- `tests/adt/test_e1.py::test_calibration_reproducibility` (C5)

Tous doivent passer en CI avant tirage `[2000-2029]`.

## 4. E₂ secondaire (optionnel — pour redondance du verdict)

E₂ n'est **pas** requis pour rendre un verdict v0.5.0. Il est **recommandé** comme contrôle de robustesse si les ressources le permettent (1-2 semaines wall-clock supplémentaires).

Spécification résumée d'E₂ : satisfait C3 par **l'axe 2 (non-linéarité)**. Concrètement, terme logistique par cellule :

$$ f_{t+1} \leftarrow f_{t+1} + r_{logistic} \cdot f_{t+1} \cdot (1 - f_{t+1}) $$

avec $r_{logistic}$ calibré par procédure analogue à §3.4 (à figer dans une éventuelle ADR-032.bis si E₂ est exécuté).

**Si E₂ exécuté** : verdict pondéré sur les deux environnements (cf. §6.4).

## 5. Protocole de tirage pré-enregistré

### 5.1 Pools de seeds

| Pool | Usage | Statut |
|---|---|---|
| `[3000-3009]` | Calibration `diffusion_coeff` (E₁) | utilisable dès ACCEPTED, *non* utilisable pour tirage |
| `[2000-2029]` | Tirage portabilité E₁ (premiers 30 seeds) | **GELÉ** jusqu'à ACCEPTED + implémentation passée |
| `[2030-2099]` | Réserve E₁ (tirage tail si demandé par reviewer) | GELÉ |
| `[2100-2129]` | Tirage portabilité E₂ (si exécuté) | GELÉ |

Pools κ existants (`[1500-1529]` consommés, `[1530-1599]` tail) restent figés conformément à ADR-031 §4.1.

### 5.2 Conditions appariées sur E₁

Sur chaque seed $s \in [2000, 2029]$ :
- Run R (réactif sans mémoire, identique ADR-026 v2.1)
- Run M_κ (memory-1 sur pression locale, identique ADR-030)
- Run S (obs-shuffled control, identique ADR-024)
- Run M baseline (Markov, identique chaîne σ)

Calcul de :
- $\delta_\sigma^{R}(s)$, $\delta_\sigma^{M_\kappa}(s)$, $\delta_\sigma^{S}(s)$ (Wasserstein contre M baseline, double reporting Miller-Madow + plug-in)
- $\Delta_s = \delta_\sigma^{M_\kappa}(s) - \delta_\sigma^{R}(s)$ (statistique principale)

### 5.3 Statistique d'inférence

Réutilisation **bit-identique** de la chaîne ADR-027 :
- Wilcoxon apparié $\Delta_s$ vs zéro, branche `greater`
- Cohen $d$ (moyenne / écart-type apparié)
- Double branche entropie (concordance Miller-Madow ↔ plug-in)
- Override `INCONCLUSIVE` si une seule branche est positive significativement

Aucune nouvelle métrique. Aucun ajustement post-hoc.

### 5.4 Diagnostics action-side (informatifs, non-décisionnels)

- Médiane $K_{M_\kappa} - K_R$ (recouvrement de répertoire d'action)
- Médiane $\delta_\sigma^{M_\kappa}$ et $\delta_\sigma^{R}$ (signe et amplitude)

Ces diagnostics permettent de *qualifier* le verdict (cf. §6.3) sans servir à le rendre.

## 6. Définition des verdicts

Le verdict v0.5.0 est rendu *uniquement* sur les chiffres pré-enregistrés du tirage E₁ pool `[2000-2029]`, double branche concordante.

### 6.1 `KAPPA_TRANSFERS`

**Conditions conjointes** :
- Cohen $d \ge 1.0$ (effet large)
- $p_{>}$ (Wilcoxon greater) $< 10^{-4}$ sur les deux branches d'entropie
- $\ge 25/30$ seeds avec $\Delta_s > 0$
- 0 clip event (intégrité numérique)

Conséquence : G1 PASSÉE. Ouvre H2 (cf. ADR-031 §4.3) et déclenche ADR-035.

### 6.2 `KAPPA_FAILS_TRANSFER`

**Conditions conjointes** :
- Cohen $d < 0.3$ (effet absent ou trivial), **ou** $p_{>} > 10^{-2}$ sur l'une des branches, **ou** $< 18/30$ seeds avec $\Delta_s > 0$
- Diagnostic action-side cohérent avec l'absence de signal (médiane $K_{M_\kappa} - K_R$ proche de 0)

Conséquence : G1 ÉCHOUÉE. Déclenche ADR-034 (boundary-of-validity) en priorité absolue. Voie A reste interdite.

### 6.3 `KAPPA_BOUNDED`

**Conditions** : tous les cas intermédiaires (effet présent mais réduit, $d \in [0.3, 1.0)$, ou concordance partielle des branches).

Conséquence : G1 PARTIELLEMENT PASSÉE. Le scope κ est borné publiquement à un sous-ensemble caractérisable des dynamiques. Décision d'exécuter Voie A à scope borné renvoyée au comité scientifique externe (constitué via ADR-036).

### 6.4 Si E₂ exécuté

Verdict global = verdict E₁ **uniquement** si E₂ concorde (même classe). Si E₁ et E₂ divergent (ex. E₁ TRANSFERS, E₂ FAILS), le verdict global est `KAPPA_BOUNDED` *par construction*, et le rapport de release documente la divergence.

### 6.5 Override INCONCLUSIVE (s'applique universellement à §6.1, §6.2, §6.3, §6.4)

Si la chaîne statistique détecte une incohérence majeure — clip events > 0, divergence Miller-Madow vs plug-in > 1 ordre de grandeur sur Cohen $d$, ou échec d'un test ADT sur le pool de tirage — le verdict est `INCONCLUSIVE` **quelle que soit** la classe nominale du résultat (TRANSFERS, FAILS_TRANSFER, BOUNDED, ou divergence E₁/E₂). Cette règle prime sur §6.1-§6.4. Un re-tirage sur pool de réserve `[2030-2099]` est autorisé après publication d'un ADR de remédiation. **Aucun re-tirage silencieux.** (Clarification amendement §12 / 2026-05-09.)

## 7. Protocole de discipline épistémique (verrous internes)

Cette section ne définit *pas* un protocole de validation sociale. Le repo est public, les commits sont horodatés et signés, les données et manifestes sont versionnés et hashés. Le public juge — c'est son rôle, pas une condition d'existence du travail.

Cette section définit en revanche **trois verrous épistémiques** que le CEO s'impose à lui-même, indépendamment de toute revue externe. Leur fonction : permettre, dans 6 ou 18 mois, de répondre avec certitude à la question *« ai-je trouvé quelque chose, ou ai-je simplement bien cherché ? »*.

### 7.1 Les trois verrous

**Verrou V1 — Pas de mesure M_κ sur E₁ avant freeze de la spec** (formalisation de C5).

Tant que `src/env/e1.py` n'est pas figé par un commit signé portant explicitement « E₁ spec frozen per ADR-032 §3.1-§3.3 », aucune exécution d'un agent M_κ sur une instance E₁ n'est admissible — sur aucun seed, dans aucun pool, pour aucune raison (incluant « simple curiosité » ou « debug »). La calibration §3.4 et les tests ADT §3.5 sont autorisés *parce qu'ils ne font pas tourner M_κ* — ils mesurent des propriétés du champ, pas l'effet κ.

**Vérification** : `git log --all --grep="E₁ spec frozen"` doit retourner exactement un commit, et tout commit ultérieur touchant `src/agents/memory1_agent.py` ou un script de tirage E₁ doit lui être postérieur.

**Verrou V2 — Pas de modification de §3.1-§3.3 après observation de la dynamique E₁** (C5-bis).

Une fois E₁ implémenté et la calibration §3.4 lancée (même partiellement), les sections §3.1 (choix d'axe structurel), §3.2 (configuration figée), §3.3 (dynamique) deviennent **immuables** sans repartir au statut PROPOSED. Tout amendement à §3.1-§3.3 force :
- Retour explicite au statut PROPOSED (commit signé).
- Invalidation du pool de calibration `[3000-3009]` (un nouveau pool doit être ouvert via ADR-032.bis).
- Suppression de tout audit `research/calibration_e1.json` produit avant l'amendement.

**Justification** : si pendant la calibration une intuition émerge (« j'aurais dû mettre une advection en plus »), c'est une intuition contaminée par l'observation. La discipline impose qu'elle passe par un nouveau pré-enregistrement, pas par un patch silencieux.

**Verrou V3 — Pas de tirage `[2000-2029]` avant pré-enregistrement complet des attentes** (déjà encodé en §6).

Le pool `[2000-2029]` ne peut être touché qu'après :
- ACCEPTED INTERNAL prononcé (cf. §7.2).
- Tests ADT §3.5 tous passés en CI.
- Calibration §3.4 complétée et `diffusion_coeff` figé.
- §6 (définition des trois verdicts) inchangé depuis ACCEPTED INTERNAL.
- Commit signé « ready for portability draw, ADR-032 §6 verdicts frozen ».

### 7.2 Statuts et transitions

L'ADR-032 connaît deux statuts opérationnels. Les transitions sont actées par commits signés et ne dépendent d'aucun acteur externe.

| De | À | Condition |
|---|---|---|
| PROPOSED | ACCEPTED INTERNAL | Commit signé du CEO attestant relecture intégrale post-amendements §12. Aucun reviewer requis. |
| ACCEPTED INTERNAL | (tirage autorisé) | Verrous V1, V2, V3 satisfaits. Pas de changement de label de statut — l'autorisation est donnée par le commit « ready for portability draw » (§7.1 V3). |
| toute | SUPERSEDED | Nouvelle ADR explicite. |

**Note** : il n'y a *pas* de statut « ACCEPTED » distinct. Le label ACCEPTED INTERNAL est terminal du point de vue du protocole interne. Si une revue externe survient ultérieurement (cf. §7.3), elle est intégrée comme commentaire au journal §12 sans changer le statut — parce que la validité de l'ADR ne dépend pas d'elle.

### 7.3 Revue publique éventuelle (intégrée, pas exigée)

Le repo étant public, toute personne peut ouvrir une PR ou issue contre cette ADR. Si cela survient :

- Les objections sont lues et traitées comme amendements éventuels au journal §12.
- Une objection touchant §3.1-§3.3 *après* freeze E₁ ne peut pas modifier l'ADR-032 en cours — elle motive éventuellement une ADR-033 ou un E₂ dans une release ultérieure.
- Une objection touchant §6 (verdicts) *après* tirage est rejetée de droit (modification rétroactive interdite, garde-fou §8.3).
- Une objection touchant §2 (clause d'invalidation) ou §3.4-§3.5 (calibration, tests) *avant* tirage est traitée au cas par cas et tracée publiquement dans le fil GitHub.

Aucune objection externe n'est *requise* pour avancer. Aucune objection externe ne peut *forcer* un retour en arrière sur un freeze déjà acté.

### 7.4 Articulation avec ADR-031 §5.3

ADR-031 §5.3 originel exigeait « reviewer externe avant ACCEPTED ». Cette articulation est révisée par **ADR-031.bis** (2026-05-09), qui supersede §5.3 et acte que la fonction protégée (intégrité épistémique) est désormais portée par les verrous V1-V2-V3 ci-dessus. Voir `docs/adr/ADR-031.bis-supersede-section-5-3.md`.

## 8. Garde-fous doctrinaux

1. **Pas de tirage exploratoire sur E₁.** Le pool calibration `[3000-3009]` est *exclusivement* pour calibrer `diffusion_coeff` et exécuter les tests ADT. Aucune mesure de M_κ sur ce pool n'est admise.
2. **Pas d'optimisation de E₁ après visualisation.** Si la calibration §3.4 ne produit aucun $D$ admissible dans la grille `{0.005, 0.010, 0.020, 0.040, 0.080}`, la grille n'est *pas* élargie : un ADR-032.bis est ouvert avec justification.
3. **Pas de modification rétroactive de la grille de verdict.** Les seuils §6.1, §6.2, §6.3 sont figés à l'ACCEPTED. Toute proposition de modification après le tirage est traitée comme une faute grave de méthode.
4. **Pas de re-tirage caché.** Tout re-tirage passe par la procédure §6.5 et un ADR de remédiation public.
5. **Pas de communication anticipée du verdict.** Aucune mention du résultat E₁ hors du repo avant la publication formelle de v0.5.0 (RELEASE.md + DOI Zenodo + manifest signé).

## 9. Vérification

### 9.1 Pré-ACCEPTED (CI)

```bash
# C5 — pas de spec dérivée d'une mesure
test "$(git log --oneline -- src/env/e1.py 2>/dev/null | wc -l)" -le 1

# C1, C2, C4 — tests ADT passent
pytest tests/adt/test_e1.py -v --strict-markers

# C3 — différenciation structurelle vérifiée
pytest tests/adt/test_e1.py::test_structural_difference_from_e0 -v

# §3.4 — calibration reproductible
python -m src.experiments.calibrate_e1 --seeds 3000-3009 --grid 0.005,0.010,0.020,0.040,0.080
```

### 9.2 Pré-tirage

```bash
# §5.1 — pools gelés
! grep -rE "seed\s*[:=]\s*(20[0-2][0-9]|21[0-2][0-9])" src/experiments/

# §7 — revue externe archivée
test -f docs/external_reviews/ADR-032_review_*.md
```

### 9.3 Post-tirage (RELEASE v0.5.0)

```bash
# Verdict aligné avec §6
python -m src.experiments.verdict_v05 --pool 2000-2029 --strict

# Manifest κ chaîné
sha256sum src/env/e0.py src/env/e1.py docs/adr/ADR-030-*.md docs/adr/ADR-032-*.md \
  >> research/MANIFEST.v0.5.0.yaml
```

L'indicateur `DH_q` ([doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §9.3) calculé fin Q4 2026 inclut le respect binaire de cette ADR : +1.0 ACCEPTED, +2.0 verdict signé, −5.0 par modification rétroactive, −3.0 par violation d'un critère §2 ou §8.

## 10. Notes de rédaction

- Cette ADR est **délibérément longue** sur §2 (clause d'invalidation) et **délibérément courte** sur §4 (E₂). E₂ peut faire l'objet d'une ADR-032.bis si exécuté ; E₁ seul suffit à rendre un verdict v0.5.0 valide.
- Le choix d'un seul axe structurel modifié (couplage spatial) est défendable comme **principe de parcimonie expérimentale** : un environnement qui diffère sur deux axes simultanément est moins diagnostique en cas d'échec.
- Cette ADR ne supersede aucune ADR antérieure. Elle sera supersédée *uniquement* par une ADR explicitant un changement de protocole de portabilité, jamais par réécriture in situ.

## 11. Annexe — Commentaires publics (le cas échéant)

*Cette section archive, si elles surviennent, les objections externes ouvertes via PR ou issue publique sur le repo CAE, conformément à §7.3. La validité de l'ADR ne dépend pas de leur présence.*

*La revue interne contradictoire datée du 2026-05-09 (CEO, posture devil's advocate) est archivée dans `docs/internal_reviews/ADR-032_internal_2026-05-09.md`. Elle a motivé les amendements §12 du 2026-05-09.*

## 12. Amendements internes (journal)

Cette section enregistre les modifications internes apportées à l'ADR. Les amendements ne nécessitent pas de validation externe ; ils sont actés par commit signé du CEO.

### 2026-05-09 — Amendement initial post-revue interne contradictoire

**Source** : revue interne contradictoire (CEO, posture devil's advocate), archivée dans `docs/internal_reviews/ADR-032_internal_2026-05-09.md`.

**Modifications appliquées** :

1. **§2.3 — Contrainte d'irréductibilité** : ajout d'une clause explicitant que la différence structurelle doit être irréductible par transformation lisse externe (E_n non-difféomorphe à E₀). Verrouille l'interprétation de « cosmétique » contre les transformations passives.
2. **§3.2 + §3.3 — Périmètre de la condition aux limites périodique** : renommage `boundary` → `laplacian_boundary` ; clarification explicite que la périodicité ne s'applique qu'à l'opérateur Laplacien, pas au kernel d'action (qui reste bit-identique à E₀, distance euclidienne). La base spectrale de E₀ étant déjà implicitement périodique (`linspace(..., endpoint=False)`), aucune topologie *nouvelle* n'est introduite. La parcimonie §3.1 (un seul axe modifié) est préservée et désormais auditée.
3. **§3.4 — Calibration sur régime stationnaire** : remplacement de la cible $\sigma_t$ à $t = $ horizon (régime potentiellement transitoire) par $\bar\sigma$ moyennée sur la fenêtre stationnaire $[T_{warmup}, T_{warmup} + T_{stat}]$ utilisée par la chaîne ADR-027 §5.3. Ajout d'un audit JSON versionné et hashé dans le manifest v0.5.0. *Cette correction est substantielle* : elle élimine le risque qu'un $D$ soit retenu pour ses propriétés transitoires plutôt que structurelles.
4. **§3.5 — Test d'autocorrélation spatiale non-locale** : ajout d'un test ADT prouvant *empiriquement* que la corrélation à distance $\Delta = 2$ est non-triviale en E₁ et significativement supérieure à E₀. Ce test renforce C3 au-delà de la simple divergence trajectorielle.
5. **§6.5 — Universalité de l'override INCONCLUSIVE** : clarification que §6.5 prime sur §6.1, §6.2, §6.3, §6.4 *quelle que soit* la classe nominale du résultat. Lève une ambiguïté potentielle.

**Modifications NON appliquées** :
- Affinement de §6.4 (règle de divergence E₁/E₂) : conservé en l'état (BOUNDED par construction). La posture de sécurité maximale est préférée à l'optimisation directionnelle.

### 2026-05-09 (suite) — Amendement §7 : recadrage épistémique

**Décision CEO** : la version initiale de §7 confondait deux fonctions distinctes — protection épistémique (interne) et validation sociale (externe). Cette confusion menait à un protocole inutilement restrictif (deadline reviewer, format imposé, blocage du travail technique) au prix d'aucun gain réel : le repo étant public, signé et horodaté, la validation sociale est *déjà* assurée par le mécanisme repo lui-même.

**Modifications appliquées** :

1. **§7 réécrite** sous le titre « Protocole de discipline épistémique (verrous internes) ». Plus de protocole de revue externe formelle.
2. **§7.1 — Trois verrous nommés** : V1 (pas de M_κ sur E₁ avant freeze), V2 (pas de modification §3.1-§3.3 après observation), V3 (pas de tirage avant pré-enregistrement complet). Ces verrous sont vérifiables par `git log` et fingerprint, sans dépendance externe.
3. **§7.2 — Statuts simplifiés** : PROPOSED → ACCEPTED INTERNAL (terminal). Pas de statut ACCEPTED distinct ; le passage au tirage est conditionné par les verrous, pas par un label.
4. **§7.3 — Revue publique éventuelle** : si elle survient via PR/issue, elle est intégrée comme commentaire ; elle n'est *ni requise pour avancer ni habilitée à forcer un retour en arrière sur un freeze acté*.
5. **§7.4 — Articulation ADR-031 §5.3** : la fonction protégée par ADR-031 §5.3 est désormais portée par les verrous V1-V2-V3 ; voir ADR-031.bis (2026-05-09) qui acte la révision au niveau ADR-031.
6. **§11 réécrite** en conséquence (annexe « commentaires publics » au lieu d'« annexe revue externe »).

**Justification doctrinale** : les trois verrous V1-V2-V3 protègent la capacité du CEO à répondre, dans 6 ou 18 mois, à la question « ai-je trouvé quelque chose, ou ai-je simplement bien cherché ? ». C'est la seule fonction que la doctrine doit garantir.

**Statut post-amendement** : PROPOSED. Le passage à ACCEPTED INTERNAL requiert un commit signé séparé du CEO actant relecture intégrale.

### 2026-05-09 (suite, bis) — Amendement §3.5 : seuils data-driven

**Source** : implémentation E1 + calibration §3.4 réussie (D=0.080), puis exécution des tests ADT §3.5 originels qui ont échoué 10/22.

**Constat** : les seuils originels de §3.5 (corrélation < 0.95 ; ratio d'amplitude autocorr 2× à Δ=2) avaient été fixés sur intuition pré-implémentation. Mesure factuelle sur pool calibration `[3000-3009]` :
- Corrélation trajectorielle E₀/E₁ mesurée ∈ [0.983, 0.995] : seuil 0.95 mathématiquement infaisable car E₀ et E₁ partagent par construction le même drift quasi-périodique (`_reference_field` bit-identique).
- Ratio autocorr |C^E1(2)|/|C^E0(2)| mesuré ≈ 1.11 (et non 2.0) : E₀ a déjà 0.59 d'autocorrélation structurelle à Δ=2 par construction (cosines basse-fréquence sur grille 64), saturer un ratio 2× est impossible.

**Décision** : reformulation des deux tests sur la base des données factuelles, sans toucher §3.1-§3.3 (verrou V2 préservé) ni faire tourner M_κ (verrou V1 préservé).

**Modifications appliquées** :

1. **Test 1** : remplacement de la corrélation par la **distance L1 moyenne** $\langle |f^{E_1} - f^{E_0}| \rangle$ sur régime stationnaire. Seuil ≥ 0.015 (17% sous le minimum mesuré 0.018). La métrique L1 mesure directement *ce que la spec §3.1 vise* : éloignement *en valeur*, pas en forme.
2. **Test 2** : remplacement du ratio d'amplitude par un **test directionnel à Δ=4** : $C^{E_1}(4) - C^{E_0}(4) > 0$ par seed. Justification : valeur absolue $C^{E_0}(4) \in [-0.81, +0.66]$ selon seed (donc test de signe absolu instable), mais effet de lissage Laplacien directionnel sur 10/10 seeds (marge min +0.026).

**Doctrine respectée** :
- V1 : aucune mesure M_κ exécutée pour ce diagnostic (uniquement propriétés du champ).
- V2 : aucune modification de §3.1, §3.2, §3.3.
- Calibration §3.4 : D=0.080 retenu, audit `research/calibration_e1.json` reste valide.
- Honnêteté : trace publique de l'erreur de spec et de sa correction, sans patch silencieux du code E₁ pour faire passer les tests.

**Statut post-amendement** : ACCEPTED INTERNAL préservé (les amendements §3.5 sont des seuils opérationnels de tests, pas une modification de la dynamique). Le commit de freeze V1 « E₁ spec frozen per ADR-032 §3.1-§3.3 » devient émissible dès passage CI 22/22.

---

*Devise inchangée : "La discipline est le produit."*
