# ADR-031 — Trilemme post-κ : engagement de séquence B-first

**Statut** : ACCEPTED
**Date d'ouverture** : 2026-05-09
**Date d'acceptation** : 2026-05-09
**Décideur** : CEO
**Amont** : ADR-028 §7 (Option A acceptée), ADR-029 (release v0.3.0), ADR-030 (pré-reg κ ACCEPTED), [RELEASE.md](../../RELEASE.md) v0.4.0 §6 (trois pistes ouvertes), [doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §3
**Aval** : ADR-032 (pré-reg E₁, à rédiger immédiatement après ACCEPTED), ADR-033 (H₈ trigger conditionnel), ADR-034 (boundary-of-validity conditionnel), ADR-037 (κ-stability sweep technique, conditionnel à `KAPPA_TRANSFERS`)
**Pool ressources** : aucun nouveau pool ouvert par cette ADR. Tail `[1530-1599]` reste **GELÉ**.
**Release attendue** : aucune release directement attribuée. Cette ADR est un *contrat de séquence*, pas une expérience.

---

## 1. Contexte

Le verdict v0.4.0 (`KAPPA_REVERSES`, Cohen $d = +2.66$, $p_{>} = 9.31 \times 10^{-10}$, 30/30 seeds) a fermé ADR-030 et ouvert trois pistes mutuellement non-exclusives, listées dans [RELEASE.md](../../RELEASE.md) v0.4.0 §6 :

- **Voie A — κ-stability sweep** : profondeur de mémoire (mémoire-2, EMA, leaky integrator) sur E₀.
- **Voie B — Cross-environment portability** : κ réplique-t-il hors E₀ (E₁ avec dynamiques distinctes) ?
- **Voie C — H₈ architectural pivot** : refonte conditionnelle si A et B échouent.

Les ressources H1 (1 ETP scientifique, ≤ 200 €/mois compute) interdisent l'exécution simultanée des trois voies. Une **séquence doit être figée publiquement** avant tout tirage exploratoire, faute de quoi la première tentation (creuser la profondeur de mémoire sur E₀) deviendra un fait accompli méthodologique.

Cette ADR fige cette séquence et inscrit Voie B en priorité absolue.

## 2. Décision

**Voie B (Cross-env portability) est exécutée avant Voie A (κ-stability sweep).**

Voie C (H₈ pivot) n'est pas rédigée par défaut. Elle est déclenchée *conditionnellement* à un échec de gate G1 (cf. §5).

Conséquence directe : **ADR-032** (pré-enregistrement de E₁ et du protocole de portabilité) est rédigée immédiatement après l'acceptation de la présente ADR, deadline `2026-09-30`.

## 3. Justification — Trois arguments indépendants

### 3.1 Falsifiabilité asymétrique

Voie B est un test **binaire informatif** : κ réplique hors E₀ (avec $d \ge 1.0$ sur ≥ 2 environnements indépendants) ou non. Toute issue est publiable avec un verdict signé sans ambiguïté narrative.

Voie A produit une courbe $d(k)$ où $k$ est la profondeur de mémoire. Une courbe est *toujours interprétable* : un plateau, une décroissance, une oscillation, une croissance saturante sont tous "compatibles avec une loi d'échelle" pour un lecteur motivé. À ressources égales, un test binaire informatif domine en valeur scientifique par seed un raffinement non-binaire.

### 3.2 Coût d'opportunité asymétrique

- **Si A est exécutée d'abord et B échoue ensuite** : tout le travail Voie A devient rétrospectivement non-publiable comme contribution de plateforme. Il se publie au mieux comme "raffinement local d'un effet spécifique à E₀", avec une note de bas de page dévalorisante.
- **Si B est exécutée d'abord et passe** : Voie A devient une priorité naturelle de H2, exécutée alors avec un budget plus large et un cadre théorique solidifié par la portabilité prouvée.
- **Si B est exécutée d'abord et échoue** : ADR-034 (boundary-of-validity) est déclenchée, le scope κ est borné publiquement, et Voie A est abandonnée sans coût sunk.

L'ordre B-puis-A maximise l'option dans les trois branches. L'ordre A-puis-B la détruit dans deux branches sur trois.

### 3.3 Doctrine d'instrument

CAE se prétend instrument **indépendant du substrat** ([doc_base/CAE_Vision_Position.md](../../doc_base/CAE_Vision_Position.md) §6). En métrologie, l'ordre canonique est : **calibrer le capteur dans plusieurs atmosphères avant de cartographier les pressions d'une seule.** Tester l'instrument (Voie B) avant d'approfondir le signal (Voie A) est l'application littérale de cette doctrine.

L'inversion de cet ordre (A-puis-B) reviendrait à publier des isobars détaillés pour une seule cuve avant d'avoir vérifié que le baromètre fonctionne hors de cette cuve.

## 4. Conséquences

### 4.1 Conséquences de gel (immédiates)

- Le pool de seeds tail `[1530-1599]` reste **GELÉ** jusqu'à la publication de v0.5.0-portability. Aucun tirage exploratoire ne s'y autorise.
- Aucun nouvel agent à mémoire de profondeur > 1 (`memory2_agent`, `memory_ema_agent`, `memory_leaky_agent`, etc.) n'est ajouté à `src/agents/` avant la publication du verdict v0.5.0.
- Aucun nouveau script de sweep (`kappa_sweep_runner.py` ou équivalent) n'est ajouté à `src/experiments/` avant la publication du verdict v0.5.0.
- Aucun manifest `MANIFEST.v0.5.0-sweep.yaml` ou équivalent n'est créé avant ADR-037.

### 4.2 Conséquences de rédaction (séquencées)

| Étape | Livrable | Deadline |
|---|---|---|
| 1 | ADR-031 ACCEPTED (présent document) | 2026-05-10 |
| 2 | ADR-032 PROPOSED (spec E₁ + pré-reg portabilité) | 2026-06-30 |
| 3 | Soumission ADR-032 à reviewer externe (théorie systèmes complexes ou RL théorique) | 2026-07-15 |
| 4 | ADR-032 ACCEPTED (après intégration des objections) | 2026-09-30 |
| 5 | Implémentation `src/env/e1.py` + image Docker `cae-research-kit:0.5.0` | 2026-11-30 |
| 6 | Tirage portabilité + verdict v0.5.0 (`KAPPA_TRANSFERS` / `KAPPA_FAILS_TRANSFER` / `KAPPA_BOUNDED`) | 2026-12-31 |

### 4.3 Conséquences de promotion (post-G1)

- Si v0.5.0 = `KAPPA_TRANSFERS` (gate G1 passée) : ADR-037 ouvert pour Voie A en priorité H2 ; ADR-035 (CAE-Cert v0.1) ouvert en parallèle.
- Si v0.5.0 = `KAPPA_FAILS_TRANSFER` : ADR-034 (boundary-of-validity) prioritaire sur tout autre travail. Voie A n'est *pas* exécutée par défaut.
- Si v0.5.0 = `KAPPA_BOUNDED` (réplique partielle, ex. d ∈ [0.3, 1.0)) : décision de comité scientifique externe (constitué via ADR-036) sur l'opportunité d'exécuter Voie A à scope borné.

## 5. Garde-fous doctrinaux

1. **Refus documenté de toute pression contraire.** Si une pression interne ou externe pousse à exécuter Voie A avant Voie B (raison "précaution technique", "sécurisation de l'outil", "facilité d'implémentation"), elle est archivée dans `.forge_private/external_pressure/` avec date, source, motif invoqué, et refus signé. Cf. Narrative-Trap-A nommée dans [doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §2.3.
2. **Aucune modification rétroactive de la séquence.** Si Voie B échoue, la séquence n'est *pas* réécrite a posteriori en "A puis C". L'échec est publié, ADR-034 est ouvert, et toute reprise éventuelle de A passe par une nouvelle ADR explicitement amont-pointée vers cette ADR-031 (qui reste figée).
3. **Aucun raccourci de revue.** ADR-032 *doit* passer par un reviewer externe avant ACCEPTED. Si aucun reviewer externe ne peut être engagé avant `2026-08-31`, la deadline ADR-032 (2026-09-30) glisse, et un ADR public d'explication est rédigé conformément à [doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §9.2.
4. **Inviolabilité du pool tail [1530-1599].** Tout tirage exploratoire sur ce pool avant verdict v0.5.0 invalide la chaîne κ et déclenche un revert + un ADR de remédiation.

## 6. Alternatives rejetées

### 6.1 Alt-1 : A puis B

*Rejetée.* Voir §3.1 (falsifiabilité asymétrique) et §3.2 (coût d'opportunité). Argument supplémentaire : la séduction émotionnelle de Voie A ($\kappa$ "fonctionne" sur E₀, donc "creusons") est exactement la pente que la doctrine ADR-020 oblige à refuser.

### 6.2 Alt-2 : A et B en parallèle

*Rejetée.* Ressources H1 = 1 ETP scientifique. La parallélisation se traduirait soit par un retard sur les deux voies, soit par une dégradation de la rigueur sur l'une (typiquement Voie B, plus exigeante en spec). Le coût de coordination dépasse la valeur ajoutée.

### 6.3 Alt-3 : C immédiatement (H₈ pivot sans A ni B)

*Rejetée.* Prématuré. ADR-033 ne peut être rédigée à partir de premiers principes ; elle a besoin des données de réfutation produites par A et/ou B pour être informative. La rédiger maintenant produirait un placeholder narratif, exactement le type d'artefact que ce projet bannit.

### 6.4 Alt-4 : "Précaution technique" — rédiger ADR-037 (sweep technique) avant ADR-032

*Rejetée.* Cette alternative reformule Alt-1 sous un vocabulaire neutre. Elle est nommée et écartée explicitement ici pour empêcher sa réintroduction sous d'autres habillages lexicaux.

## 7. Engagements opérationnels

1. **Aucun ADR-037 (sweep technique)** rédigé avant publication du verdict v0.5.0.
2. **Aucune écriture** dans `src/env/e1.py` avant ADR-032 ACCEPTED.
3. **Aucun tirage** Voie A (profondeur > 1, EMA, leaky integrator) sur quelque pool que ce soit avant verdict v0.5.0.
4. **Tout glissement** de la deadline ADR-032 (2026-09-30) > 1 trimestre déclenche un ADR public d'explication, conformément à [doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §9.2.
5. **Tout pitch externe** reçu pendant H1 qui présuppose Voie A en cours est archivé sans réponse engageante.

## 8. Vérification

Critères binaires reproductibles par tout tiers à partir du repo public :

```bash
# §4.1 — gel des agents profondeur > 1
test "$(ls src/agents/memory[2-9]_agent.py 2>/dev/null | wc -l)" -eq 0
test "$(ls src/agents/memory_*ema*.py src/agents/memory_*leaky*.py 2>/dev/null | wc -l)" -eq 0

# §4.1 — gel des scripts de sweep
test "$(ls src/experiments/*sweep* 2>/dev/null | wc -l)" -eq 0

# §4.1 — gel du pool tail [1530-1599]
! grep -rE "seed\s*[:=]\s*15[3-9][0-9]" research/ src/

# §7.1 — pas d'ADR-037 prématurée
test ! -f docs/adr/ADR-037-*.md  # tant que research/h7_kappa_*v0.5* n'existe pas

# §5.4 — chaîne ADR amont préservée
sha256sum docs/adr/ADR-026-v2.1-*.md docs/adr/ADR-027-*.md docs/adr/ADR-030-*.md \
  | diff - research/MANIFEST.v0.4.0.yaml.adr_chain.expected  # à matérialiser dans MANIFEST.v0.5.0
```

L'indicateur `DH_q` ([doc_base/CAE_Roadmap_Strategique.md](../../doc_base/CAE_Roadmap_Strategique.md) §9.3) calculé fin Q2 2026 inclut le respect binaire de cette ADR comme contrôle (poids +1.0 si ACCEPTED, −5.0 si modification rétroactive détectée, −3.0 par violation des critères §8).

## 9. Notes de rédaction

- Cette ADR est volontairement courte (≈ 150 lignes hors front-matter). Elle ne contient *aucune* spec technique : elle est un **contrat de séquence**.
- Elle ne supersede aucune ADR antérieure. Elle ne sera supersédée que si Voie B livre `KAPPA_TRANSFERS` *et* qu'une décision explicite de comité réordonne la suite (auquel cas un ADR-039 ou supérieur sera ouvert, pas cette ADR-031 réécrite).
- La numérotation Annexe A du roadmap est respectée : ADR-031 = trilemme, ADR-032 = E₁, ADR-037 = sweep technique conditionnel.

---

*Devise inchangée : "La discipline est le produit."*
