# ADR-036 — CAE-Cert v0.1 (signed verdict certification protocol)

**Statut** : ACCEPTED
**Date d'ouverture** : 2026-05-10
**Date d'acceptation** : 2026-05-10 (CEO, acte verbal verbatim ; cf. §11)
**Décideur** : CEO (verrous épistémiques V1-V2-V3 ADR-032 §7.1 préservés ; aucune nouvelle expérience scientifique, aucun nouveau pool, aucune modification du moteur)
**Amont** :
- ADR-020 (lexique froid, vocabulaire interdit / requis)
- ADR-032 §6.1 (verdict v0.5.0 = `KAPPA_TRANSFERS`, $d = +3.0906$)
- ADR-033 ACCEPTED (audit gate, comparator pinné, doctrine de bit-identité)
- ADR-034 §1 amont ("Aval : ADR-035 (CAE-Cert v0.1) *si* v0.5.0 = `KAPPA_TRANSFERS`") — mandat CAE-Cert orphelin
- ADR-034 §5 (verdict v0.6.0 `KAPPA_INCONCLUSIVE` formel, défense ADR-035 PASS)
- ADR-035 §5.1 (lecture physique `KAPPA_BAND_LIMITED upper_open`, max $|\Delta| = 4.5 \times 10^{-11}$)
- [research/MANIFEST.v0.6.0.yaml](../../research/MANIFEST.v0.6.0.yaml) (release certifiable de référence)
- [RELEASE.md](../../RELEASE.md) v0.6.0 §6 (lacune CAE-Cert non couverte par v0.5.0/v0.6.0)
**Aval** : release `v0.7.0-cert-protocol` (protocole + outillage + rétrofit v0.6.0) ; ADR-037 (multi-marginales pré-reg, déclenché en parallèle dès ACCEPTED) ; sprint pulsaride `GATE-M4-Certification` (consommateur externe).
**Pool ressources** : **AUCUN nouveau pool**. **Aucune nouvelle expérience**. Pure formalisation.
**Coût** : ~5 jours-homme (rédaction + outillage + rétrofit + paper). Compute : négligeable (validation par dry-run sur artefacts v0.6.0 existants).
**Release attendue** : `v0.7.0-cert-protocol`, deadline 2026-05-17.

---

## 1. Contexte

### 1.1 Le mandat CAE-Cert orphelin

ADR-032 prévoyait initialement deux ADR aval mutuellement exclusives :

- *si* v0.5.0 = `KAPPA_FAILS_TRANSFER` → ADR-034 (boundary-of-validity)
- *si* v0.5.0 = `KAPPA_TRANSFERS` → ADR-035 (CAE-Cert v0.1)

Le verdict v0.5.0 ayant été `KAPPA_TRANSFERS`, le mandat ADR-035=CAE-Cert était nominal. ADR-034 a néanmoins été ouverte (boundary-of-validity ré-orientée pour borner par le haut une réussite plutôt qu'un échec, cf. ADR-034 §1.1). Puis le sweep ADR-034 a fired §5.4 sur la concordance inter-pools, et ADR-035 a été réquisitionné en urgence comme **réplication seed-paired** pour défendre le verdict — non plus comme protocole de certification.

Le mandat CAE-Cert est resté **orphelin** depuis le 2026-05-10. Cette ADR le reprend.

### 1.2 Pourquoi le moment est venu

Trois faits convergent :

1. **L'asset défendable est constitué.** v0.6.0 publie simultanément un verdict formel `KAPPA_INCONCLUSIVE` (protocole honoré à la lettre) et une lecture opérationnelle `KAPPA_BAND_LIMITED upper_open` (défense ADR-035, max $|\Delta| = 4.5 \times 10^{-11}$). Cette dualité — refus de réviser une règle pré-enregistrée même quand on en a l'occasion + démonstration cryptographique de l'invariance du moteur — est la signature CAE. Sans format de certification, elle n'est pas exportable hors du repo.
2. **La consommation externe est prête.** Le sprint pulsaride-h7 (livré en parallèle, hors scope de cette ADR) requiert un `GATE-M4-Certification` qui dépend explicitement d'un protocole CAE-Cert ACCEPTED côté CaePivot. Sans ADR-036, M4 reste bloqué.
3. **La pré-emption académique est urgente.** RELEASE.md §6 et ROADMAP §8 identifient la pré-emption comme risque stratégique majeur. Un protocole formellement publié + paper arXiv = ancrage sémantique défensif.

### 1.3 Question protocolaire

Comment transformer un MANIFEST + chaîne d'ADR + artefacts CSV/JSON en un **objet auto-portable, signé cryptographiquement, vérifiable hors-ligne** par un tiers (auditeur, régulateur, client, reviewer) sans accès au repo source ?

La réponse standard "publiez sur Zenodo avec DOI" résout la persistance et la citabilité, **pas** l'auto-vérification : un DOI Zenodo n'atteste ni de l'identité de l'émetteur, ni de l'absence d'altération entre dépôt et lecture, ni de la cohérence interne du verdict. CAE-Cert v0.1 comble cette lacune avec un objet JSON canonicalisé + signature détachée Ed25519.

---

## 2. Décision

Adopter le **protocole CAE-Cert v0.1** défini en §3-§5, l'appliquer rétroactivement à v0.6.0 selon §6, et le geler par bump de fingerprint Docker à `cae-research-kit:0.7.0` (§7).

**Hors-scope explicite** :
- Pas d'autorité de certification tierce — CAE auto-certifie en v0.1, comme un DOI auto-déposé. Une autorité externe est différée v0.2+.
- Pas de gouvernance multi-signataires — CEO seul signe en v0.1.
- Pas de format binaire (CBOR, protobuf) — JSON only, RFC 8785 JCS pour canonicalisation.
- Pas de standardisation IETF / W3C — différée H2 selon traction.
- Pas d'expiration de certificat en v0.1 — réservée v0.2.
- Pas de modification du moteur scientifique (`src/env/`, `src/agents/`, `src/metrics/`, `src/analysis/`, `src/experiments/`) — strictement byte-identique post-v0.6.0.
- Pas de modification rétroactive d'ADR ou de MANIFEST déjà publiés (chaîne immuable §10).

---

## 3. Schéma `cae-cert.v01.json`

### 3.1 Structure canonique

Tous les champs ci-dessous sont **obligatoires** sauf mention explicite. L'ordre des clés dans le fichier sérialisé est imposé par RFC 8785 (lexicographique strict sur les clés UTF-8).

```json
{
  "cert_version": "0.1.0",
  "cert_id": "<UUID v4>",
  "issued_at": "<ISO 8601 UTC, suffixe Z>",
  "issuer": {
    "name": "<chaîne libre, ex. 'CAE Project (self-issued)'>",
    "public_key_fingerprint_sha256": "<hex 64>"
  },
  "subject": {
    "release_tag": "<ex. 'v0.6.0-h7-κ-boundary'>",
    "doi": "<ex. '10.5281/zenodo.20112259'>",
    "manifest_path": "<chemin repo-relatif, ex. 'research/MANIFEST.v0.6.0.yaml'>",
    "manifest_sha256": "<hex 64>"
  },
  "claims": {
    "formal_verdict": "<un de: KAPPA_TRANSFERS, KAPPA_FAILS_TRANSFER, KAPPA_INCONCLUSIVE, KAPPA_INCONCLUSIVE_CONFIRMED, KAPPA_BAND_LIMITED, KAPPA_FRAGILE, KAPPA_ROBUST_PORTABILITY>",
    "operational_verdict": "<un de: identique formal, ou KAPPA_BAND_LIMITED_UPPER_OPEN, ou KAPPA_BAND_LIMITED_LOWER_OPEN, ou null>",
    "operational_envelope": {
      "parameter": "<ex. 'D' (E₁ diffusion_coeff)>",
      "min": <float ou null>,
      "max": <float ou null>,
      "rupture_above": <float ou null>,
      "rupture_below": <float ou null>
    },
    "primary_metrics": {
      "cohen_d_median": <float ou null>,
      "cohen_d_range": [<float>, <float>] | null,
      "p_value": <float ou null>,
      "n_seeds": <int ou null>,
      "n_pos": <int ou null>,
      "clip_total": <int ou null>
    }
  },
  "evidence_chain": [
    { "adr_id": "ADR-XXX", "path": "docs/adr/...", "sha256": "<hex 64>" }
  ],
  "audit_artefacts": [
    { "path": "research/...", "sha256": "<hex 64>", "role": "<ex. 'sweep_csv', 'verdict_json', 'audit_report'>" }
  ],
  "protocol_clauses": [
    { "id": "<ex. 'ADR-034 §5.4'>", "status": "<PASS | FIRE | N/A>", "note": "<chaîne libre, ≤ 280 chars>" }
  ],
  "defense_chain": [
    { "adr_id": "ADR-XXX", "claim": "<chaîne libre, ≤ 280 chars>", "max_abs_delta": <float ou null> }
  ],
  "expiry": null,
  "revocation_url": "<URL stable, ex. 'https://github.com/<org>/CaePivot/releases/tag/cert-revocations'>",
  "notes": "<chaîne libre, ≤ 4096 chars, ou null>"
}
```

### 3.2 Contraintes de validation

| Champ | Contrainte |
|---|---|
| `cert_version` | semver strict, `0.1.0` en v0.1 |
| `cert_id` | UUID v4, unique par certificat (pas par release) |
| `issued_at` | ISO 8601 avec suffixe `Z`, granularité seconde minimum |
| `*.sha256` | exactement 64 caractères hex bas-de-casse |
| `claims.formal_verdict` | enum fermé (voir §3.1), valeur exacte du `release.scientific_status` du MANIFEST référencé |
| `claims.operational_verdict` | peut différer de `formal_verdict` uniquement si une `defense_chain` non-vide le justifie |
| `evidence_chain` | ≥ 1 entrée, ordre = ordre d'ouverture des ADR |
| `audit_artefacts` | ≥ 1 entrée, chaque `sha256` doit être recalculable à partir du fichier référencé |
| `protocol_clauses` | toute clause FIRE doit avoir une note non-triviale |
| `defense_chain` | obligatoire si `operational_verdict ≠ formal_verdict` ; vide sinon |

### 3.3 Canonicalisation (RFC 8785 JCS)

La signature porte sur la **représentation canonicalisée** du JSON, pas sur la sérialisation libre. Règles RFC 8785 strictes :

1. Clés objet triées par ordre lexicographique UTF-16 code-unit
2. Pas d'espaces, pas de retours à la ligne dans la forme canonique
3. Nombres flottants normalisés (forme courte ECMAScript `Number.prototype.toString`)
4. Strings JSON-escapés minimalement (uniquement `"`, `\`, contrôles)
5. UTF-8 sans BOM

L'implémentation utilise `jcs` (PyPI, pinné `0.2.1`) pour garantir l'interopérabilité.

### 3.4 Fichier de signature `.sig`

Format binaire séparé : `cae-cert-<release_tag>.v01.json.sig`. Contenu :

```
CAESIGv01<EOL>
algo=ed25519<EOL>
pubkey_fp=<hex 64><EOL>
sig=<base64 88 chars (64 bytes signature)><EOL>
```

Header `CAESIGv01` permet de détecter incompatibilité de version sans parser. Toute autre forme est rejetée par `verify`.

---

## 4. Mécanique de signature

### 4.1 Génération de clé

Hors-repo, hors-CI, sur poste de l'émetteur :

```bash
mkdir -p ~/.cae-keys && chmod 700 ~/.cae-keys
python -m src.cert.keygen \
    --output-private ~/.cae-keys/cae-cert-issuer.ed25519 \
    --output-public  ~/.cae-keys/cae-cert-issuer.pub
```

- Algorithme : Ed25519 (Bernstein et al. 2012, RFC 8032)
- Format clé privée : PEM PKCS#8, chmod 600
- Format clé publique : PEM SubjectPublicKeyInfo, chmod 644
- Backup : copie chiffrée GPG sur support hors-ligne (responsabilité émetteur)

Le fingerprint SHA-256 de la clé publique (DER bytes) est l'**ancre de confiance**. Il est commit dans le MANIFEST de la release qui adopte CAE-Cert (§7).

### 4.2 Signature d'un certificat

```bash
python -m src.cert.issue \
    --release-tag v0.6.0-h7-κ-boundary \
    --manifest research/MANIFEST.v0.6.0.yaml \
    --private-key ~/.cae-keys/cae-cert-issuer.ed25519 \
    --output-cert research/cae-cert-v0.6.0.v01.json \
    --output-sig  research/cae-cert-v0.6.0.v01.json.sig
```

Le script :
1. Charge le MANIFEST, en extrait `release.scientific_status`, `release.operational_envelope`, `release.rupture_boundary`
2. Calcule SHA-256 du MANIFEST lui-même
3. Calcule SHA-256 de tous les ADR amont/aval listés dans le MANIFEST
4. Calcule SHA-256 de tous les artefacts `experiments.*.audit_artefacts.*` du MANIFEST
5. Construit le JSON selon §3.1
6. Canonicalise via JCS
7. Signe les bytes canoniques avec Ed25519
8. Écrit le JSON (forme lisible, indenté 2) + le `.sig` (format §3.4)

### 4.3 Vérification d'un certificat

```bash
python -m src.cert.verify \
    --cert research/cae-cert-v0.6.0.v01.json \
    --sig  research/cae-cert-v0.6.0.v01.json.sig \
    --public-key ~/.cae-keys/cae-cert-issuer.pub
```

Le script :
1. Parse le `.sig`, extrait l'algo, le fingerprint, la signature
2. Vérifie que le fingerprint correspond à la clé publique fournie
3. Re-canonicalise le JSON via JCS
4. Vérifie la signature Ed25519 sur les bytes canoniques
5. Re-calcule SHA-256 du MANIFEST, des ADR, des artefacts ; compare aux valeurs encodées
6. Vérifie cohérence interne : si `operational_verdict ≠ formal_verdict`, exige `defense_chain` non-vide ; si `protocol_clauses[*].status == FIRE`, exige `note` non-vide
7. Vérifie schéma pydantic strict
8. Exit 0 (PASS) ou exit 1 (FAIL) + rapport texte sur stderr

### 4.4 Indépendance vis-à-vis du repo

Une fois `cae-cert-*.v01.json` + `.sig` + clé publique en main, un tiers peut vérifier **sans accès au repo source**. Les SHA-256 encodés permettent de re-vérifier les artefacts si fournis (ex. CSV joints à un audit), mais l'absence d'artefact ne casse pas la vérification de signature — seulement la vérification d'intégrité de la chaîne.

---

## 5. Gouvernance

### 5.1 Émetteur en v0.1

**CEO seul.** Une seule paire de clés. Identité émetteur fixée à `"CAE Project (self-issued)"`. Justification : analogue d'un DOI auto-déposé Zenodo — l'autorité émane du protocole publié, pas d'une accréditation tierce. La transparence est l'asset, pas l'extériorité.

### 5.2 Rotation de clé

Si compromission suspectée ou rotation programmée :

1. Générer nouvelle paire (§4.1)
2. Publier `cae-cert-key-rotation-<date>.json` signé par l'**ancienne** clé, contenant le nouveau fingerprint et la raison
3. Bumper la version protocole (v0.1.1 minimum)
4. Re-émettre les certificats actifs avec la nouvelle clé (les anciens restent vérifiables avec l'ancienne clé publique, archivée)

### 5.3 Révocation

Publication d'un fichier `cae-cert-revocation-<cert_id>.json` à l'URL `revocation_url` du certificat révoqué, signé par la clé émettrice de l'origine. Contenu :

```json
{
  "revocation_version": "0.1.0",
  "revoked_cert_id": "<UUID>",
  "revoked_at": "<ISO 8601 UTC>",
  "reason": "<chaîne libre>",
  "successor_cert_id": "<UUID ou null>"
}
```

`verify.py` accepte un flag optionnel `--check-revocation` qui fetch l'URL et fail si le `cert_id` est révoqué. Comportement par défaut : pas de fetch réseau (vérification offline).

### 5.4 Versionnement protocole

Semver strict sur `cert_version` :
- `MAJOR` : changement incompatible de schéma (ex. retrait de champ obligatoire)
- `MINOR` : ajout de champ optionnel, nouveau verdict autorisé
- `PATCH` : clarification de validation, pas de changement sémantique

Toute évolution requiert ouverture d'une nouvelle ADR (ADR-036.bis pour patch, ADR-04X pour minor/major).

---

## 6. Rétrofit v0.6.0

### 6.1 Le certificat encode la dualité formal/opérationnel

C'est le test décisif du protocole : peut-il représenter fidèlement la situation v0.6.0 sans la trahir dans un sens ou dans l'autre ?

| Champ | Valeur v0.6.0 | Source |
|---|---|---|
| `claims.formal_verdict` | `KAPPA_INCONCLUSIVE` | MANIFEST.v0.6.0 `release.scientific_status` |
| `claims.operational_verdict` | `KAPPA_BAND_LIMITED_UPPER_OPEN` | MANIFEST.v0.6.0 `release.operational_status` (interprété, voir §6.2) |
| `claims.operational_envelope.parameter` | `D` | ADR-034 §3.1 |
| `claims.operational_envelope.min` | `0.005` | sweep |
| `claims.operational_envelope.max` | `0.320` | sweep |
| `claims.operational_envelope.rupture_above` | `0.640` | MANIFEST.v0.6.0 `release.rupture_boundary` |
| `claims.primary_metrics.cohen_d_median` | `3.0906` | ADR-032 §6.1 |
| `claims.primary_metrics.cohen_d_range` | `[2.764, 3.014]` | sweep ADR-034 |
| `claims.primary_metrics.p_value` | `9.31e-10` | ADR-032 §6.1 |
| `claims.primary_metrics.n_seeds` | `30` | par grid-point |
| `claims.primary_metrics.clip_total` | `0` | sweep ADR-034 §5 |
| `protocol_clauses` | une entrée par critère ADR-034 §5.1-§5.4 ; §5.4 = FIRE | MANIFEST.v0.6.0 |
| `defense_chain` | `[ADR-035, max_abs_delta=4.5e-11]` | ADR-035 §5.1 |

### 6.2 Note sémantique sur `operational_verdict`

Le MANIFEST v0.6.0 utilise la chaîne `kappa_signature_robust_on_validated_envelope` pour `release.operational_status` — formulation libre du Manifeste, antérieure à ce protocole. Le rétrofit la **traduit** dans l'enum fermé du schéma : `KAPPA_BAND_LIMITED_UPPER_OPEN`. La traduction est explicite dans le champ `notes` du certificat. Aucune révision du MANIFEST n'est faite (chaîne immuable).

### 6.3 Acte rétroactif vs modification rétroactive

Émettre un certificat sur v0.6.0 **n'est pas** modifier v0.6.0. Le certificat est un objet additionnel signé qui :
- pointe vers v0.6.0 par DOI + SHA-256
- ré-affirme les verdicts publiés sans les changer
- vit sous v0.7.0 (release du protocole) avec son propre DOI

Le DOI v0.6.0 reste cité tel quel. Le DOI v0.7.0 cite le protocole + le certificat. Aucune ambiguïté sur la chaîne immuable §10.

---

## 7. Conséquences sur la release v0.7.0

### 7.1 Bump fingerprint Docker

`reproduction_image.name: cae-research-kit:0.7.0`. Justification : le protocole CAE-Cert ajoute la dépendance `cryptography ~= 42.0` et `jcs == 0.2.1` au runtime ; les hooks de signature/vérification sont packagés dans l'image. Même si le moteur scientifique ne change pas, la **capacité opérationnelle** de l'image change — c'est une mutation d'environnement au sens ADR-031.bis.

### 7.2 Section nouvelle dans MANIFEST.v0.7.0

```yaml
certification:
  protocol: CAE-Cert
  protocol_version: 0.1.0
  protocol_adr: docs/adr/ADR-036-cae-cert-v01-protocol.md
  protocol_adr_sha256: <hex>
  issuer:
    name: "CAE Project (self-issued)"
    public_key_fingerprint_sha256: <hex>
    public_key_path: keys/cae-cert-issuer.pub  # publié dans le repo
  certificates_issued:
    - subject_release: v0.6.0-h7-κ-boundary
      cert_file: research/cae-cert-v0.6.0.v01.json
      cert_file_sha256: <hex>
      sig_file: research/cae-cert-v0.6.0.v01.json.sig
      sig_file_sha256: <hex>
```

### 7.3 Publication de la clé publique dans le repo

`keys/cae-cert-issuer.pub` (PEM SubjectPublicKeyInfo) est commit. La clé privée n'est **jamais** commit. `keys/.gitignore` exclut tout sauf `*.pub` et `README.md`.

### 7.4 Cible Makefile

```make
.PHONY: issue-cert verify-cert keygen-cert
keygen-cert:
	python -m src.cert.keygen --output-private ~/.cae-keys/cae-cert-issuer.ed25519 --output-public ~/.cae-keys/cae-cert-issuer.pub
issue-cert:
	python -m src.cert.issue --release-tag $(RELEASE) --manifest research/MANIFEST.$(RELEASE).yaml --private-key ~/.cae-keys/cae-cert-issuer.ed25519 --output-cert research/cae-cert-$(RELEASE).v01.json --output-sig research/cae-cert-$(RELEASE).v01.json.sig
verify-cert:
	python -m src.cert.verify --cert $(FILE) --sig $(FILE).sig --public-key keys/cae-cert-issuer.pub
```

---

## 8. Critères d'acceptation

| Critère | Condition de succès |
|---|---|
| C1. ADR-036 status | ACCEPTED par CEO, commit présent sur `main` |
| C2. Outillage `src/cert/` | `pytest tests/cert/` exit 0 (≥ 5 tests round-trip) |
| C3. Clé d'émetteur | Générée hors-repo, fingerprint publié dans MANIFEST.v0.7.0 |
| C4. Certificat v0.6.0 | `cae-cert-v0.6.0.v01.json` + `.sig` produits, vérifiables avec `verify.py` exit 0 |
| C5. MANIFEST.v0.7.0 | Section `certification:` complète, parse YAML strict |
| C6. Image Docker | `cae-research-kit:0.7.0` build, contient `cryptography` 42.x et `jcs` 0.2.1 |
| C7. Paper arXiv | Draft `paper/cae-cert-v01/paper.md`, ≤ 8 pages, 0 mot interdit ADR-020 |
| C8. DOI Zenodo | Draft prêt, **non publié** avant validation finale CEO |

---

## 9. Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Clé privée compromise | faible | élevé | Génération hors-repo §4.1 ; backup chiffré GPG ; procédure rotation §5.2 ; clé v0.1 = clé de démonstration, clé production séparée à v0.2 |
| Format JSON modifié post-v0.1 sans bump version | moyenne | moyen | CI lint sur `cert_version == "0.1.0"` exact ; test `test_schema_frozen_v01` qui fail si retrait de champ obligatoire |
| Confusion publique "cert" vs "audit scientifique" | élevée | moyen | Paper §1 et ADR §1.3 clarifient : CAE-Cert atteste de l'**intégrité et de la cohérence formelle** d'un verdict pré-enregistré, **pas** de sa vérité scientifique. Un INCONCLUSIVE certifié reste INCONCLUSIVE. |
| Pré-emption sémantique du terme "CAE-Cert" par un tiers | faible | moyen | Publication arXiv immédiate dès ACCEPTED ; dépôt Zenodo avec DOI le même jour |
| Auditeur tiers refuse Ed25519 (réglementation FIPS-only) | faible | faible | v0.2 ajoutera ECDSA P-256 optionnel via champ `algo` du `.sig` (déjà prévu §3.4) |
| Le `defense_chain` est perçu comme une échappatoire pour "réviser" un verdict | moyenne | élevé | §6.3 explicite : `defense_chain` ne change ni `formal_verdict`, ni le verdict publié dans MANIFEST. Il documente une lecture parallèle, signée, vérifiable. Refus = refuser de publier la lecture, pas refuser le protocole. |
| Le rétrofit v0.6.0 est lu comme "retouche post-hoc" | moyenne | élevé | §6.3 + ADR-036 explicitement séparée temporellement de v0.6.0 (release distincte v0.7.0, DOI distinct, manifest distinct) |

---

## 10. Engagements (chaîne immuable)

À l'acceptation, CAE s'engage publiquement à :

1. **Ne pas modifier rétroactivement** les ADR-020 à 035 ni les MANIFEST.v0.1 à v0.6.
2. **Ne pas réémettre** un certificat avec le même `cert_id` (toute modification = nouveau `cert_id`, ancien révoqué).
3. **Publier toute révocation** sur `revocation_url` dans les 24h de la décision.
4. **Ne pas déléguer** la signature à un agent automatisé sans ADR explicite (toute signature en v0.1 = acte humain CEO).
5. **Publier la clé publique** dans le repo dès la première émission ; ne jamais la retirer (rotation = ajout, pas remplacement).
6. **Ne pas certifier** une release qui n'a pas été précédée par sa propre chaîne d'ADR pré-enregistrée (le certificat est l'acte de clôture, pas l'acte d'autorisation).
7. **Refuser tout amendement** du schéma `cae-cert.v01.json` qui adoucirait le couplage `defense_chain` ↔ `operational_verdict ≠ formal_verdict`.

---

## 11. Workflow de bout en bout (récapitulatif opérationnel)

| Étape | Action | Condition de succès | Coût |
|---|---|---|---|
| 1 | ADR-036 commitée PROPOSED | tests existants restent verts | < 5 min |
| 2 | Décision CEO ACCEPTED | header mis à jour, date pinnée | < 1 min |
| 3 | Génération clé Ed25519 hors-repo | `~/.cae-keys/` créé, chmod 700 | < 10 s |
| 4 | Implémentation `src/cert/` + tests | `pytest tests/cert/` exit 0 | ~3 h |
| 5 | Émission `cae-cert-v0.6.0.v01.json` + `.sig` | `make verify-cert` exit 0 | < 30 s |
| 6 | Rédaction `MANIFEST.v0.7.0.yaml` | parse YAML strict | ~30 min |
| 7 | Bump image Docker `cae-research-kit:0.7.0` | build OK, smoke test cert | ~15 min |
| 8 | Draft paper `paper/cae-cert-v01/paper.md` | ≤ 8 pages, lexique froid OK | ~3 h |
| 9 | Draft GitHub Release + Zenodo + arXiv | non publiés, en attente CEO | ~30 min |
| 10 | Décision finale CEO → publication | tag `v0.7.0-cert-protocol` poussé, DOI minté, paper soumis | < 10 min |

Total path nominal : ~5 jours-homme.

---

## 12. Décision attendue

**Au CEO** : valider PROPOSED → ACCEPTED. À l'acceptation, l'agent d'exécution lance le workflow §11 étapes 3-9 de bout en bout sans nouvelle décision intermédiaire. L'étape 10 (publication) reste un acte humain CEO explicite, hors scope automatique.
