# ADR-029 — Décision de release H7-σ : verdict `INVERTED`, tag `v0.3.0-h7-σ-inverted`

**Statut** : ACCEPTED
**Date** : 2026-05-09
**Décideur** : CEO
**Hypothèse** : H7-σ (couplage structurel via divergence stationnaire)
**Verdict** : `H7_SIGMA_INVERTED`
**Tag de release proposé** : `v0.3.0-h7-σ-inverted`

---

## 1. Contexte

ADR-026 v2 (gelée le 2026-05-09 matin) prédit que la divergence stationnaire de l'agent réel R par rapport au baseline Markov M serait *strictement supérieure* à celle du contrôle shuffled S :

$$\delta_\sigma = D_{KL}(P_R \| P_M) - D_{KL}(P_S \| P_M) > 0$$

Le main run (pool [1400-1429], n=30) a produit le contraire avec un effet massif :
- médiane δ_σ = **−0.148**
- 26 / 30 seeds avec δ_σ < 0
- Cohen d = **−0.758** (effet "très large" inversé)
- p_less = **1.04 × 10⁻⁵** (Wilcoxon paired, alternative="less")

ADR-026 v2.1 (amendement formalisant le bin INVERTED via test miroir, gelé pré-ré-adjudication) rend ce verdict statistiquement assertable.

## 2. Verdict adjudiqué

| Branche | Statistique | p (less) | Cohen d | Verdict isolé |
|---|---|---|---|---|
| Primaire (corr) | δ_σ_corr | 1.04e-05 | −0.7581 | `H7_SIGMA_INVERTED` |
| Transparence (naive) | δ_σ_naive | 1.04e-05 | −0.7581 | `H7_SIGMA_INVERTED` |
| `verdicts_agree` | | | | **true** |
| Override clip / sample-size | total_clip_events=0 ; n_post_drop=30 | | | non déclenché |
| **Verdict final** | | | | **`H7_SIGMA_INVERTED`** |

Diagnostique structurel (témoin pilot → main, hors-échantillon) :
- median K_R − K_S : pilot −15 → main **−19** (signe conservé, magnitude renforcée)
- median K_R = 42, K_S = 61.5, K_M = 57 (B = 64 bins disponibles)
- `sign_flip_vs_pilot = false`

## 3. Lecture théorique inscrite

H7-σ rejette dans la direction inverse. La signature reproductible (pilot ⇒ main, sans aucun re-fit, hors-échantillon) est :

> Sous boucle de feedback réelle, l'agent R **concentre** sa pression sur un sous-ensemble strict de cellules de l'état (K_R ≪ K_S ≤ K_M) ; ce profil concentré est, à divergence KL stationnaire près, *plus proche* du Markov stationnaire de l'environnement que ne l'est le profil dispersé du contrôle shuffled.

Vocabulaire permis (ADR-026 v2.1 §7) : *inverted coupling*, *stabilising feedback* au sens opérationnel `δ_σ ≤ −0.5 ∧ p_less < 0.005`. Vocabulaire banni (inchangé) : tout terme cognitif, tout terme intentionnel, "model", "learn (intransitif)".

L'inscription théorique est *minimale et opérationnelle* : on ne prétend ni que R "comprend" M, ni que R "exploite" une structure ; on inscrit que la suppression de l'ordre temporel des observations (S vs R) éloigne la statistique stationnaire du baseline. Cela impose deux contraintes sur tout futur modèle de feedback dans CAE :
1. la structure *temporelle* des observations contribue à la concentration K_R (non triviale : on aurait pu avoir K_R ≈ K_S);
2. cette concentration est compatible avec — et statistiquement plus proche de — la mesure invariante de E₀.

## 4. Décision de release

**APPROUVÉE** : tag public `v0.3.0-h7-σ-inverted`.

### 4.1 Justification du tag "verdict"

Le tag inclut le verdict pour cohérence avec la pratique v0.2.0-h6-rejected (ADR-025). La transparence sur le résultat directionnel est *constitutive* du protocole CAE.

### 4.2 Ce qui est rendu public dans `research/`

- `research/h7_sigma_run_results.csv` (30 rows × 20 cols, SHA `90ee2b80…`)
- `research/h7_sigma_verdict.json` (output adjudicateur final)
- `research/MANIFEST.v0.3.0.yaml` (incl. `H7_SIGMA_FREEZE_MANIFEST.json` v3 inline)

### 4.3 Ce qui est copié dans `docs/adr/`

- `docs/adr/ADR-026-h7-sigma.md` ← copie de `ADR-026-v2-h7-sigma-FROZEN.md`
- `docs/adr/ADR-026-v2.1-h7-sigma-amendment-inverted.md` ← copie de l'amendement
- `docs/adr/ADR-027-h7-sigma-statistical-chain.md`
- `docs/adr/ADR-029-h7-sigma-release.md` ← le présent document

### 4.4 Ce qui RESTE privé (`.forge_private/`)

- Toute la chaîne pilote (`h7_dev/exploratory/`)
- `pilot_kl.py`, `pilot_runner.py`, `pilot_analyze.py`
- ADR-026 v0 (brainstorm) et v1 (draft superseded)
- Code source `h7/` lui-même reste privé pour cette release ; seuls les artefacts (CSV + JSON) + ADRs sont publiés. Rationale : le code H7 sera publié *intégralement* à la release v0.4.0 lorsque H7-κ sera adjugé (ou pas), pour éviter des release fragmentées du même module.

### 4.5 SHA freeze publié dans MANIFEST.v0.3.0.yaml

Reprise *verbatim* de `H7_SIGMA_FREEZE_MANIFEST.json` v3 (sauf entrées `h7_dev/src/`, repush au tag v0.4.0). Entrées clés publiées :
- ADR-026 v2 SHA = `7e8e4ea8…`
- ADR-026 v2.1 SHA = `2bdf8ae9…`
- ADR-027 SHA = `7d755b94…`
- pilot_kl SHA = `dccb577e…` (binding ADR-026 v2 §8)
- main CSV SHA = `90ee2b80…`
- pilot_summary SHA = `caad3901…`
- scipy 1.12.0 / numpy 1.26.4

## 5. Statut des pools

| Pool | Statut | Action |
|---|---|---|
| [9000-9009] | BURNED | aucun |
| [9100-9109] | DISPONIBLE | non utilisé (pas de remediation) |
| [1400-1429] | BURNED | publié dans v0.3.0 |
| [1500-1599] | RÉSERVÉ κ | **gelé** ; ne sera tiré que si ADR-028 (κ pre-reg) cadre l'inversion comme éligible à investigation H7-κ |

## 6. H7-κ : statut

L'inversion *n'autorise pas* automatiquement le tirage du pool κ. Le verdict `INVERTED` n'est pas le verdict `FEEDBACK_ONLY` qui était le déclencheur prévu pour κ (ADR-026 v2 §2). Une nouvelle ADR (ADR-028, *à rédiger*) doit décider :
- soit que H7-κ reste pertinente sur l'inversion (réinterprétation : κ doit décomposer la stabilisation observée) ;
- soit que H7-κ doit être abandonnée et remplacée par H8 (à ré-pré-enregistrer).

Cette décision est **hors scope d'ADR-029** et sera prise après publication v0.3.0.

## 7. Tâches release (executor)

1. ✅ Geler ADR-026 v2.1 (SHA `2bdf8ae9…`)
2. ✅ Patch + re-SHA adjudicateur (SHA `f6c5aeff…`)
3. ✅ Tests verts (5/5 sur sigma_pipeline)
4. ✅ Re-adjudication → `H7_SIGMA_INVERTED`
5. ✅ Geler manifest v3 + CSV main run (SHA `90ee2b80…`)
6. ⏭ Copier ADRs 026 v2, 026 v2.1, 027, 029 dans `docs/adr/`
7. ⏭ Copier CSV + verdict JSON dans `research/`
8. ⏭ Écrire `research/MANIFEST.v0.3.0.yaml` (avec freeze manifest inline)
9. ⏭ Mettre à jour `RELEASE.md` et `README.md`
10. ⏭ Commit + tag `v0.3.0-h7-σ-inverted` sur `main`
11. ⏭ Push + DOI Zenodo
12. ⏭ Mettre à jour `RELEASE.md` avec le DOI
13. ⏭ Commit + push final (DOI pin)

## 8. Closure

H7-σ est **statistiquement décidée** (rejet directionnel franc, hors-échantillon, sans flip pilot↔main). La théorie CAE entre dans son premier contact empirique avec une signature non-triviale et reproductible : la concentration de pression conditionnelle sous boucle réelle. Le ré-pré-enregistrement éventuel (H7-κ ou H8) commence avec ce résultat comme contrainte dure.
