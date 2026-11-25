# Révision — Réseaux Bayésiens (M2 IAFA)

> **Infos examen :** Durée ~1h30 · **1 feuille A4 recto-verso** + **calculatrice** autorisées · La logique possibiliste (présente avant 2022) n'est **pas** au programme.

## Structure type des annales (20 points)

1. **Modéliser un Réseau Bayésien** : graphe causal + tables de probabilités *(3 pts)*
2. **La d-séparation & indépendance conditionnelle** *(3 pts)*
3. **Arbre de groupes, arbre de jonction & initialisation des tables** *(5 pts)*
4. **Calcul de probabilité par marginalisation** *(3 pts)*
5. **Envoi de messages, évidences dures & question piège** *(6 pts)*

---

## Étape 1 : Modéliser un Réseau Bayésien *(Question 1 — 3 pts)*

Un **réseau bayésien** représente des connaissances incertaines de façon compacte grâce à **deux éléments** :

### 1. Un graphe causal (DAG)
- **Sommets (nœuds)** : les variables du problème.
- **Arcs (flèches)** : les liens de **cause à effet direct**. Si `A → B`, alors `A` est un **parent** de `B` ($A \in \text{pa}(B)$).
- **Sans circuit (DAG)** : impossible de tourner en rond en suivant les flèches.

> **Astuce examen :** Pour identifier les parents d'une variable $X$, repère les variables qui apparaissent dans les « *si ...* » de la phrase donnant les probabilités de $X$.

### 2. Une table de probabilités conditionnelles par variable
Pour **chaque** variable $X$, on donne la table $P(X \mid \text{pa}(X))$ :
- Si $X$ n'a **aucun parent** (racine), on donne sa probabilité *a priori* $P(X)$.
- Si $X$ a des parents, on met **en colonnes** toutes les combinaisons possibles des parents, et **en lignes** les valeurs de $X$.
- **Règle d'or :** **la somme de chaque colonne vaut toujours $1$** (100 %).

### 3. Formule de la probabilité conjointe
Grâce à la **propriété de Markov** (*chaque variable est indépendante de ses non-descendants sachant ses parents*), la probabilité conjointe de toutes les variables $U$ est le produit des tables :

$$P(U) = \prod_{X \in U} P(X \mid \text{pa}(X))$$

### Exemple du cours (le verglas)
> Il y a du verglas ($Ve$) 70 % du temps. S'il y a du verglas, William ($W$) a un accident dans 80 % des cas ; sinon dans 10 % des cas. Idem pour Hector ($H$).

- **Graphe :** `Ve → W` et `Ve → H`
- **Tables :**

| $P(Ve)$ | `ve` | `nve` |
|---|:---:|:---:|
| | 0.7 | 0.3 |

| $P(W \mid Ve)$ | `Ve = ve` | `Ve = nve` |
|---|:---:|:---:|
| `W = acc` | 0.8 | 0.1 |
| `W = non` | 0.2 | 0.9 |

*(Même table pour $P(H \mid Ve)$.)*

- **Probabilité conjointe :** $P(Ve, W, H) = P(Ve) \times P(W \mid Ve) \times P(H \mid Ve)$
  - Exemple : $P(ve, acc, non) = 0.7 \times 0.8 \times 0.2 = 0.112$.

---

### Mini-exercice 1 : Pluie, Arroseur, Herbe

**Énoncé :**
- Variables : $P$ (Pluie : `oui`, `non`), $A$ (Arroseur : `oui`, `non`), $H$ (Herbe mouillée : `oui`, `non`).
- Il pleut 30 % des jours.
- S'il pleut, l'arroseur s'allume dans 10 % des cas ; s'il ne pleut pas, dans 60 % des cas.
- Si pluie et arroseur : herbe mouillée à 99 %. Pluie seule : 90 %. Arroseur seul : 80 %. Aucun des deux : 0 %.

**Correction :**
1. **Graphe causal :** `P → A`, `P → H`, `A → H`.
```
  P ──► A
   \   /
    ▼ ▼
     H
```
2. **Tables de probabilités :**

| $P(P)$ | `oui` | `non` |
|---|:---:|:---:|
| | 0.30 | 0.70 |

| $P(A \mid P)$ | `P = oui` | `P = non` |
|---|:---:|:---:|
| `A = oui` | 0.10 | 0.60 |
| `A = non` | 0.90 | 0.40 |

| $P(H \mid P, A)$ | `oui, oui` | `oui, non` | `non, oui` | `non, non` |
|---|:---:|:---:|:---:|:---:|
| `H = oui` | 0.99 | 0.90 | 0.80 | 0.00 |
| `H = non` | 0.01 | 0.10 | 0.20 | 1.00 |

3. **Probabilité conjointe :**
$$P(P, A, H) = P(P) \times P(A \mid P) \times P(H \mid P, A)$$

---

## Étape 2 : La d-séparation & Indépendance *(Questions 2 et 3 — 3 pts)*

Une **chaîne** relie deux nœuds en suivant les arêtes **sans tenir compte du sens des flèches** (on peut remonter une flèche). Sur une chaîne, chaque nœud intermédiaire $V$ forme l'une des **3 connexions de base** :

| Connexion | Dessin | Sans connaître $V$ | Si on connaît $V$ (dans $Z$) |
|---|---|---|---|
| **1. Série** *(effet indirect)* | `A → V → B` (ou `A ← V ← B`) | **OUVERTE** | **BLOQUÉE** |
| **2. Divergente** *(cause commune)* | `A ← V → B` | **OUVERTE** | **BLOQUÉE** |
| **3. Convergente** *(effet commun)* | `A → V ← B` | **BLOQUÉE** | **OUVERTE** *(si $V$ **ou un descendant de $V$** est dans $Z$ !)* |

### Définition de la d-séparation
Un ensemble $Z$ **d-sépare** $A$ et $B$ ssi **toutes les chaînes** simples entre $A$ et $B$ sont **bloquées** (il suffit d'un seul nœud bloqué pour bloquer toute une chaîne).

### Méthode en 3 étapes
1. Lister **toutes les chaînes simples** entre $A$ et $B$ (en ignorant le sens des flèches).
2. Repérer les chaînes déjà **bloquées** par une connexion convergente (si $Z = \emptyset$ suffit déjà, on s'arrête !).
3. Pour les chaînes ouvertes, placer dans $Z$ un nœud en connexion **série** ou **divergente**... **en vérifiant que cet ajout n'ouvre pas une connexion convergente** sur une autre chaîne !

### Lien avec l'indépendance *(Théorème de Verma & Pearl — Question 3)*
Si $Z$ d-sépare $A$ et $B$ dans un réseau bayésien (qui satisfait la propriété de Markov), alors **$A$ et $B$ sont indépendantes sachant $Z$** :
$$P(A \mid B, Z) = P(A \mid Z) \qquad \text{et si } Z = \emptyset : \quad P(A \mid B) = P(A)$$

---

### Mini-exercice 2 : d-séparation (graphe de l'annale 2025-26)

**Graphe :** `C → Q → R → E`, `C → V → E`, `K → V`.
```
  C ──► V ◄── K
  │     │
  ▼     │
  Q     │
  │     │
  ▼     ▼
  R ──► E
```

**Questions & Correction :**
1. **Chaînes simples entre `K` et `E` (il y en a 2) :**
   - Chaîne 1 : `K → V → E`
   - Chaîne 2 : `K → V ← C → Q → R → E`
2. **Si $Z = \emptyset$ :**
   - Chaîne 1 : série en `V` sans info $\Rightarrow$ **OUVERTE**.
   - Chaîne 2 : convergente en `V` sans info sur `V` ni son descendant `E` $\Rightarrow$ **BLOQUÉE**.
3. **Ensemble minimal $Z$ d-séparant `{K}` et `{E}` :**
   - Pour bloquer la Chaîne 1, on doit connaître `V`.
   - **Piège :** connaître `V` **ouvre** la connexion convergente `K → V ← C` de la Chaîne 2 !
   - Il faut donc bloquer aussi la Chaîne 2 en `C` (divergente), `Q` (série) ou `R` (série).
   - **Réponse :** **`{V, C}`** (ou **`{V, Q}`**, ou **`{V, R}`**).
4. **Déduction :** `K` et `E` sont **indépendantes sachant `{V, C}`** (ou `{V, Q}` ou `{V, R}`).
5. **Bonus — Ensemble minimal d-séparant `{K}` et `{R}` :**
   - Chaînes : `K → V ← C → Q → R` (convergente en `V` $\Rightarrow$ bloquée) et `K → V → E ← R` (convergente en `E` $\Rightarrow$ bloquée).
   - **Réponse :** **`Z = ∅`** $\Rightarrow$ `K` et `R` sont **indépendantes** : $P(R \mid K) = P(R)$.

---

## Étape 3 : Arbre de groupes, Arbre de jonction & Initialisation *(Question 4 — 5 pts)*

### 1. Arbre de groupes
Un graphe dont les nœuds sont des **groupes** de variables reliés par des **séparateurs** ($S = G_i \cap G_j$) est un **arbre de groupes** du réseau bayésien ssi :
1. **Arbre :** graphe non orienté **connexe** et **sans cycle**.
2. **De groupes :** pour chaque variable $X$ du réseau, il existe au moins un groupe contenant **$X$ et tous ses parents $\text{pa}(X)$**.

### 2. Arbre de jonction
C'est un arbre de groupes qui vérifie en plus la **propriété de jonction** (*intersection courante*) :
> Pour toute paire de groupes $G_1$ et $G_2$, toute variable $X \in G_1 \cap G_2$ appartient à **tous les groupes (et tous les séparateurs)** de l'unique chaîne entre $G_1$ et $G_2$.

*(En pratique, il suffit de vérifier les paires de groupes **non adjacents** !)*

**Exemple (annale 2025-26) :**
```
Arbre A (PAS de jonction) :          Arbre B (ARBRE DE JONCTION) :
[CQ] ──(C)── [KVC]                   [CQV] ──(CV)── [CKV]
 │                                     │
(Q)                                   (QV)
 │                                     │
[QR] ──(R)── [EVR]                   [QRV] ──(RV)── [ERV]
```
- **Arbre A** est un arbre de groupes, mais **pas** un arbre de jonction car $KVC \cap EVR = \{V\}$ et `V` n'apparaît pas sur le chemin entre `KVC` et `EVR`.
- **Arbre B** est un arbre de jonction : on a ajouté `V` dans les groupes et séparateurs du chemin ; tous les groupes non adjacents n'ont que `V` en commun, et `V` est présent partout.

### 3. Construction et minimalité de la taille des groupes
- **Recette de construction :**
  1. Former pour chaque variable sa famille $\{X\} \cup \text{pa}(X)$ et ne garder que les groupes maximaux (supprimer ceux inclus dans un autre).
  2. Relier ces groupes en un arbre (séparateurs = intersections).
  3. Vérifier la propriété de jonction et, si une variable commune à deux groupes éloignés manque sur le chemin, l'ajouter dans les groupes/séparateurs intermédiaires.
- **Justifier la taille minimale :** Si une variable $X$ a $k$ parents, tout arbre de groupes doit contenir un groupe de taille **au moins $k + 1$** pour contenir $\{X\} \cup \text{pa}(X)$.

### 4. Initialisation des tables
1. Initialiser **toutes** les tables (groupes et séparateurs) à $\mathbb{1}$.
2. Pour **chaque variable $X$** du réseau (**exactement une fois**), choisir un groupe contenant $\{X\} \cup \text{pa}(X)$ et multiplier sa table par $P(X \mid \text{pa}(X))$.
3. **Pour qu'un groupe ait directement la probabilité conjointe de ses variables :** choisir un groupe contenant des variables racines (sans parents) et leurs enfants directs, et y affecter toutes leurs tables.

---

### Mini-exercice 3 : Arbre de jonction & Initialisation (annale 2024-25)

**Graphe :** `M → E`, `M → T`, `E → T`, `E → D`, `T → D`, `D → R`, `H → R`.

**Correction :**
1. **Arbre de jonction (groupes maximaux = `MET`, `ETD`, `DRH`) :**
```
[MET] ──(ET)── [ETD] ──(D)── [DRH]
```
2. **Justifications :**
   - **Taille minimale = 3 :** il faut un groupe contenant `T` et ses 2 parents (`M, E`), `D` et ses 2 parents (`E, T`), `R` et ses 2 parents (`D, H`). Nos groupes étant de taille 3, c'est optimal.
   - **Arbre de jonction :** connexe sans cycle, chaque variable apparaît avec ses parents dans un groupe, et les seuls groupes non adjacents (`MET` et `DRH`) vérifient $MET \cap DRH = \emptyset$ (propriété de jonction trivialement satisfaite).
3. **Initialisation des tables :**
   - $t_{MET} = t_{ETD} = t_{DRH} = t_{ET} = t_{D} = \mathbb{1}$.
   - Affectation :
     - $t_{MET} = P(M) \times P(E \mid M) \times P(T \mid E, M)$
     - $t_{ETD} = P(D \mid E, T)$
     - $t_{DRH} = P(H) \times P(R \mid D, H)$
     - $t_{ET} = t_{D} = \mathbb{1}$
4. **Groupe ayant la probabilité conjointe :** **`MET`**, car par la règle de la chaîne :
   $$t_{MET} = P(M) \times P(E \mid M) \times P(T \mid E, M) = P(M, E, T)$$

---

## Étape 4 : Marginalisation & Calcul de probabilité *(Question 5 — 3 pts)*

### Principe
À partir d'une table contenant la **probabilité conjointe** d'un groupe (ex : $t_{MET} = P(M, E, T)$), on obtient la probabilité marginale d'une variable en **sommant sur toutes les combinaisons possibles des autres variables** :

$$P(T = t) = \sum_{M, E} t_{M, E, T=t}$$

*(Si $M$ a $a$ valeurs et $E$ a $b$ valeurs, la somme contient exactement $a \times b$ termes.)*

### Rappel : Probabilité conditionnelle
$$P(A \mid B = b) = \frac{P(A, B = b)}{P(B = b)} \qquad \text{avec } P(B = b) = \sum_A P(A, B = b)$$

---

### Mini-exercice 4 : Calcul numérique (Question 5 de 2024-25)

**Données :**
- $P(M = \text{fav}) = 0.62$, $P(M = \text{def}) = 0.38$
- $P(E = \text{oui} \mid \text{fav}) = 0.3$, $P(E = \text{non} \mid \text{fav}) = 0.7$, $P(E = \text{oui} \mid \text{def}) = 0.7$, $P(E = \text{non} \mid \text{def}) = 0.3$
- $P(T = \text{velo} \mid \text{oui}, \text{fav}) = 0.4$, $P(\text{velo} \mid \text{non}, \text{fav}) = 0.5$, $P(\text{velo} \mid \text{oui}, \text{def}) = 0.1$, $P(\text{velo} \mid \text{non}, \text{def}) = 0.2$

**Correction :**
1. **Formule :**
$$\begin{aligned}
P(T = \text{velo}) &= \sum_{M, E} t_{M, E, T=\text{velo}} \\
&= P(\text{fav})P(\text{oui}\mid\text{fav})P(\text{velo}\mid\text{oui},\text{fav}) + P(\text{fav})P(\text{non}\mid\text{fav})P(\text{velo}\mid\text{non},\text{fav}) \\
&\quad + P(\text{def})P(\text{oui}\mid\text{def})P(\text{velo}\mid\text{oui},\text{def}) + P(\text{def})P(\text{non}\mid\text{def})P(\text{velo}\mid\text{non},\text{def})
\end{aligned}$$
2. **Application numérique :**
$$P(T = \text{velo}) = 0.62 \times 0.3 \times 0.4 + 0.62 \times 0.7 \times 0.5 + 0.38 \times 0.7 \times 0.1 + 0.38 \times 0.3 \times 0.2 = \mathbf{0.3408}$$
3. **Bonus ($P(E = \text{oui})$) :**
$$P(E = \text{oui}) = \sum_M P(M)P(E=\text{oui}\mid M) = 0.62 \times 0.3 + 0.38 \times 0.7 = 0.186 + 0.266 = \mathbf{0.452}$$

---

## Étape 5 : Envoi de messages, Évidences & Piège de la Q7 *(Questions 6 et 7 — 6 pts)*

### 1. Envoi d'un message de $G_1$ vers un voisin $G_2$ *(séparateur $S = G_1 \cap G_2$)*
Pour propager la probabilité conjointe depuis $G_1$ vers $G_2$ :
1. **Mise à jour du séparateur $S$** *(marginalisation de $G_1$ sur $G_1 \setminus S$)* :
   $$t'_S = \sum_{G_1 \setminus S} t_{G_1}$$
2. **Mise à jour du groupe destinataire $G_2$ :**
   $$t'_{G_2} = t_{G_2} \times \frac{t'_S}{t_S}$$
   *(À l'initialisation, $t_S = \mathbb{1}$.)*
3. **Si on veut $P(X)$ pour $X \in G_2$ :** marginaliser $t'_{G_2}$ sur les autres variables : $P(X) = \sum_{G_2 \setminus \{X\}} t'_{G_2}$.

### 2. Intégrer une évidence dure $X = x$ et calculer $P(Y = y \mid X = x)$
1. **Mise à jour locale :** dans la table du groupe de départ contenant $X$ (et ayant sa proba conjointe), on **met à $0$ toutes les cases où $X \neq x$**. La table contient $P(G_{\text{départ}}, X = x)$.
2. **Propagation :** on envoie des messages de proche en proche le long du chemin jusqu'au groupe $G_{\text{cible}}$ contenant $Y$. Sa table devient $P(G_{\text{cible}}, X = x)$.
3. **Marginalisation et normalisation :**
   - $P(Y = y, X = x) = \sum_{G_{\text{cible}} \setminus \{Y\}} t'_{G_{\text{cible}}, X=x}$
   - $P(X = x)$ par marginalisation sur toutes les autres variables (de $G_{\text{départ}}$ ou $G_{\text{cible}}$)
   - $P(Y = y \mid X = x) = \dfrac{P(Y = y, X = x)}{P(X = x)}$

### 3. Le piège : *« Peut-on éviter l'envoi de message pour ce calcul ? »*
**Réflexe :** vérifier si $Y$ et $X$ sont **d-séparées par $\emptyset$** !
- **Non d-séparées** $\Rightarrow$ **NON**, il faut propager l'évidence.
- **D-séparées par $\emptyset$** $\Rightarrow$ $P(Y \mid X = x) = P(Y)$ *(l'évidence $X = x$ est inutile)*, puis distinguer **2 sous-cas** :
  - **$P(Y)$ est connue directement** (ex : $Y$ est une racine, comme $P(H \mid E) = P(H) = 0.89$ en 2024-25) $\Rightarrow$ **OUI**, on évite tout envoi de message !
  - **$P(Y)$ n'est PAS connue directement** (ex : $P(R \mid K) = P(R)$ en 2025-26, où on ne connaît que $P(R \mid Q)$) $\Rightarrow$ **NON**, il faut quand même envoyer des messages pour obtenir la conjointe dans un groupe contenant $R$ et calculer $P(R)$ !

---

### Mini-exercice 5 : Envoi de messages & Évidence (Questions 6 et 7 de 2025-26)

**Arbre de jonction :** `[CKV] ──(CV)── [CQV] ──(QV)── [QRV] ──(RV)── [ERV]`
- $t_{CKV} = P(C)P(K)P(V \mid C, K) = P(C, K, V)$
- $t_{CQV} = P(Q \mid C)$, $t_{QRV} = P(R \mid Q)$, $t_{ERV} = P(E \mid V, R)$, séparateurs à $\mathbb{1}$.

**Correction :**
1. **Calcul de $P(Q)$ par un envoi de message :**
   - Envoi de **`CKV` vers `CQV`** (séparateur `CV`) :
     - $t'_{CV} = \sum_{K} t_{CKV} = P(C, V)$
     - $t'_{CQV} = \dfrac{t_{CQV} \times t'_{CV}}{t_{CV}} = \dfrac{P(Q \mid C) \sum_{K} t_{CKV}}{\mathbb{1}} = P(C, Q, V)$
     - $P(Q) = \sum_{C, V} t'_{CQV}$
2. **Calcul de $P(R = \text{hallu} \mid K = \text{ignorant})$ :**
   - Mettre à jour $t_{CKV}$ avec $K = \text{ignorant}$ (mettre à $0$ les autres valeurs de $K$) $\Rightarrow P(C, V, K = \text{ignorant})$.
   - Envoyer un message de `CKV` vers `CQV` (via `CV`) $\Rightarrow P(C, Q, V, K = \text{ignorant})$.
   - Envoyer un message de `CQV` vers `QRV` (via `QV`) $\Rightarrow t'_{QRV} = P(Q, R, V, K = \text{ignorant})$.
   - Marginaliser : $P(R = \text{hallu}, K = \text{ignorant}) = \sum_{Q, V} t'_{Q, R=\text{hallu}, V, K=\text{ignorant}}$ et $P(K = \text{ignorant}) = \sum_{C, V} t_{C, V, K=\text{ignorant}}$ (ici $0.3$).
   - Diviser : $P(R = \text{hallu} \mid K = \text{ignorant}) = \dfrac{P(R = \text{hallu}, K = \text{ignorant})}{P(K = \text{ignorant})}$.
   - **Peut-on éviter l'envoi de message ?** `R` et `K` sont d-séparées par $\emptyset$, donc $P(R \mid K) = P(R)$ *(pas besoin d'intégrer $K = \text{ignorant}$)*. **Mais NON**, on ne peut pas éviter l'envoi de message car $P(R)$ n'est pas connue directement : il faut tout de même propager `CKV → CQV → QRV` pour obtenir la conjointe dans `QRV` puis marginaliser.

---

## Focus approfondi : Proba conjointe, Initialisation & Formule des probas composées

### 1. Probabilité conjointe vs Probabilité conditionnelle

- **Probabilité conjointe $P(A, B)$** = probabilité que **$A$ ET $B$ se produisent en même temps**.
  - **Signe distinctif :** **la somme de TOUTES les cases du tableau vaut exactement $1$**.
  - Exemple (`Météo`, `Parapluie`) :

    | $P(\text{Météo}, \text{Parapluie})$ | `soleil` | `pluie` |
    |---|:---:|:---:|
    | `parapluie = oui` | `0.07` | `0.27` |
    | `parapluie = non` | `0.63` | `0.03` |

    *(Somme totale = $0.07 + 0.63 + 0.27 + 0.03 = 1$. On peut marginaliser directement : $P(\text{oui}) = 0.07 + 0.27 = 0.34$.)*

- **Probabilité conditionnelle $P(B \mid A)$** = probabilité de $B$ **sachant** $A$.
  - **Signe distinctif :** **chaque colonne** somme à $1$, donc la somme de tout le tableau vaut $2$, $3$, etc. (**pas $1$**).
  - Pour la transformer en conjointe, il manque $P(A)$ : $P(A, B) = P(A) \times P(B \mid A)$.

---

### 2. L'initialisation avec l'analogie « cartes et boîtes »

- **Tes cartes** = exactement **1 table de la Question 1 par variable** du réseau (tu n'inventes aucune autre proba !).
- **Tes boîtes** = les groupes de l'arbre de jonction (et les séparateurs entre eux).
- **Procédure :**
  1. Mettre **`1`** ($\mathbb{1}$) dans toutes les boîtes (groupes et séparateurs).
  2. Poser **chaque carte dans UNE SEULE boîte** contenant toutes les lettres de la carte (la variable + ses parents). Si une boîte reçoit plusieurs cartes, on les **multiplie**.
- **Vérification rapide :** le nombre total de $P(\dots)$ dans tout l'arbre doit être égal au nombre de variables du réseau.

> **Pourquoi ne peut-on pas garder les tables d'initialisation pour les autres boîtes ?**
> Parce que chaque table du RB n'est placée qu'**une seule fois** ! Résultat : une seule boîte a sa vraie probabilité conjointe ✅ ; les autres n'ont que des conditionnelles ❌ (ex : $t_{EL} = P(E \mid L)$ somme à $2$, pas à $1$, car il lui manque $P(L)$). Les **envois de messages** servent justement à propager le ✅ de proche en proche jusqu'à ce que toutes les boîtes aient leur probabilité conjointe.

---

### 3. Comment repérer ET prouver qu'une boîte contient sa probabilité conjointe ?

- **Raccourci au brouillon (test visuel des cartes) :** une boîte `[X, Y, Z]` contient $P(X, Y, Z)$ si **chaque variable de la boîte** apparaît à gauche de `|` (ou sans `|`) dans son produit et que tous les parents après `|` sont aussi dans la boîte.
- **Preuve mathématique sur la copie :** on utilise la **formule des probabilités composées** (effet « boule de neige ») :

$$P(A, B) = P(A) \times P(B \mid A)$$
$$P(A, B, C) = P(A) \times P(B \mid A) \times P(C \mid A, B)$$
$$P(A, B, C, D) = P(A) \times P(B \mid A) \times P(C \mid A, B) \times P(D \mid A, B, C)$$

**Recette en 2 étapes :**
1. **Choisir le bon ordre :** toujours mettre les variables dans l'ordre des flèches du graphe (**les parents AVANT les enfants**).
2. **Comparer terme à terme avec la table de la boîte :** si une variable est « en trop » après la barre `|`, justifier par **d-séparation** qu'on a le droit de la barrer !

#### Mini-test corrigé (connexion divergente `B ← A → C`)
1. Ordre parents $\to$ enfants : **`A, B, C`**.
2. Formule des probas composées : $P(A, B, C) = P(A) \times P(B \mid A) \times P(C \mid A, B)$.
3. Simplification : `B ← A → C` est une connexion **divergente en `A`** ; sachant `A`, elle est bloquée $\Rightarrow$ `{A}` d-sépare `B` et `C` $\Rightarrow P(C \mid A, \cancel{B}) = P(C \mid A)$.
4. Conclusion : $P(A, B, C) = P(A) \times P(B \mid A) \times P(C \mid A)$.

---

### 4. Application complète : Exam 2021 — Question 3

**Graphe causal :** `N → D → M`, `N → L ← R`, `L → E`.

- **Arbre V1 :** `[DM] ──(D)── [DN] ──(N)── [LNR] ──(L)── [EL]`
  - Init : $t_{LNR} = P(N)P(R)P(L \mid N, R)$, $t_{DN} = P(D \mid N)$, $t_{DM} = P(M \mid D)$, $t_{EL} = P(E \mid L)$, séparateurs à $\mathbb{1}$.
- **Arbre V2 :** `[DMN] ──(N)── [LNR] ──(L)── [EL]`
  - Init : $t_{DMN} = P(M \mid D)P(D \mid N)$, mêmes $t_{LNR}, t_{EL}$, séparateurs à $\mathbb{1}$.

**Obtention des probabilités conjointes dans tous les groupes :**
1. **`LNR` (déjà conjointe dès l'init) :**
   - Formule des probas composées (ordre `N, R, L`) : $P(L, N, R) = P(N) \times P(R \mid N) \times P(L \mid N, R)$.
   - Or la seule chaîne entre `N` et `R` est `N → L ← R` (**convergente en `L`**), bloquée sans info sur `L` ni son descendant `E` $\Rightarrow$ `N` et `R` sont d-séparées par $\emptyset$, donc indépendantes : $P(R \mid N) = P(R)$.
   - Donc $t_{LNR} = P(N)P(R)P(L \mid N, R) = \mathbf{P(L, N, R)}$ ✅.
2. **`LNR → EL` (séparateur `L`) :**
   - $t'_L = \sum_{N, R} t_{LNR} = P(L)$, puis $t'_{EL} = \dfrac{t_{EL} \times t'_L}{t_L} = \dfrac{P(E \mid L) P(L)}{\mathbb{1}} = \mathbf{P(E, L)}$ ✅.
3. **Partie gauche (V1) :**
   - **`LNR → DN` (séparateur `N`) :** $t'_N = \sum_{L, R} t_{LNR} = P(N)$, puis $t'_{DN} = \dfrac{t_{DN} \times t'_N}{t_N} = \dfrac{P(D \mid N) P(N)}{\mathbb{1}} = \mathbf{P(D, N)}$ ✅.
   - **`DN → DM` (séparateur `D`) :** $t'_D = \sum_{N} t'_{DN} = P(D)$, puis $t'_{DM} = \dfrac{t_{DM} \times t'_D}{t_D} = \dfrac{P(M \mid D) P(D)}{\mathbb{1}} = \mathbf{P(D, M)}$ ✅.
4. **Partie gauche (V2, si groupe `DMN`) :**
   - **`LNR → DMN` (séparateur `N`) :** $t'_N = \sum_{L, R} t_{LNR} = P(N)$, puis $t'_{DMN} = P(N)P(D \mid N)P(M \mid D)$.
   - Justification : $P(D, M, N) = P(N)P(D \mid N)P(M \mid D, N)$ et `N → D → M` est **série en `D`**, donc `{D}` d-sépare `M` et `N` $\Rightarrow P(M \mid D, N) = P(M \mid D)$, d'où $t'_{DMN} = \mathbf{P(D, M, N)}$ ✅.

---

## Mémo express pour ta feuille A4

| Notion | Formule / Règle clé |
|---|---|
| **Proba conjointe d'un RB** | $P(U) = \prod_{X \in U} P(X \mid \text{pa}(X))$ *(somme totale du tableau = $1$)* |
| **Formule des probas composées** | $P(A, B, C) = P(A) P(B \mid A) P(C \mid A, B)$ *(choisir l'ordre **parents $\to$ enfants**, puis barrer les variables en trop par d-séparation)* |
| **Somme des colonnes** | Dans toute table conditionnelle $P(X \mid \text{pa}(X))$, chaque colonne somme à $1$ |
| **d-séparation** | **Série / Divergente** : bloquée si dans $Z$ · **Convergente** : ouverte si dans $Z$ ou un descendant dans $Z$ |
| **Verma & Pearl** | $Z$ d-sépare $A$ et $B$ $\implies$ $A \perp B \mid Z$, i.e. $P(A \mid B, Z) = P(A \mid Z)$ |
| **Arbre de groupes** | Connexe + sans cycle + chaque $\{X\} \cup \text{pa}(X)$ inclus dans au moins un groupe |
| **Propriété de jonction** | $\forall G_i, G_j$, tout $X \in G_i \cap G_j$ est dans tous les groupes/séparateurs sur la chaîne entre $G_i$ et $G_j$ |
| **Taille minimale** | $\ge 1 + \max_X |\text{pa}(X)|$ |
| **Initialisation (« cartes & boîtes »)** | Toutes les tables à $\mathbb{1}$, puis chaque carte $P(X \mid \text{pa}(X))$ multipliée dans **un seul** groupe contenant $\{X\} \cup \text{pa}(X)$ |
| **Repérer une boîte conjointe ✅** | Chaque variable de la boîte a sa carte (à gauche de `\|`) et ses parents sont dans la boîte *(à prouver via probas composées + d-séparation)* |
| **Marginalisation** | $P(X) = \sum_{G \setminus \{X\}} t_G$ *(quand $t_G = P(G)$)* |
| **Envoi de message ($G_1 \to G_2$, sép. $S$)** | $t'_S = \sum_{G_1 \setminus S} t_{G_1}$ puis $t'_{G_2} = t_{G_2} \times \dfrac{t'_S}{t_S}$ |
| **Conditionnelle avec évidence** | $P(Y \mid X=x) = \dfrac{P(Y, X=x)}{P(X=x)}$ (vérifier d-séparation $Y \perp X \mid \emptyset$ pour la question piège !) |
