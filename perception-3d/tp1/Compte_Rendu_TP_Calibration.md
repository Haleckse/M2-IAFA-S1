# Compte-Rendu de TP — Perception 3D : Calibration Monoculaire et Stéréovision

Ce document présente la réalisation complète du TP de calibration (`CalibTools.py`, `CalibrationMono.py`, `CalibrationStereo.py` et `test.py`) ainsi que les réponses détaillées à toutes les questions du sujet.

---

## 1. Vision monoculaire

### 1.1 Calibration Monoculaire

#### 1.1.1 Détection de la mire

1. **Type de mire et caractéristiques :**
   - En inspectant les images du dossier `data/Calib/` (ainsi que les paramètres passés dans `CalibrationMono.py` et l'inscription au bas de la mire `Calib.io | 15 x 7`), il s'agit d'une **grille asymétrique de cercles** (*Asymmetric Circle Grid*).
   - **Dimensions :** `cols = 7` cercles par ligne et `rows = 15` lignes décalées en quinconce (soit $7 \times 15 = 105$ cercles au total), avec un pas `patternSize_mm = 85.0` mm (espacement diagonal de $60\text{ mm}$, soit $60\sqrt{2} \approx 85\text{ mm}$ entre deux cercles d'une même ligne/colonne).
   - **Résolution des images :** $1024 \times 1024$ pixels.

2. **Implémentation de `detectPattern` (`CalibTools.py`) :**
   ```python
   patternFound, imgPoints = cv2.findCirclesGrid(
       gray, (cols, rows), flags=cv2.CALIB_CB_ASYMMETRIC_GRID
   )
   ```

3. **Résultats de la détection :**
   Sur les 22 images de chaque caméra, la mire est détectée dans **15 images** pour la caméra gauche (`*_0.png`) et **15 images** pour la caméra droite (`*_1.png`). Les échecs de détection sur les 7 autres vues s'expliquent par une mire partiellement hors-champ (`_00154_0`, `_00156_0`, `_00353_0`, `_00356_0`) ou une forte surexposition solaire effaçant les cercles supérieurs (`_00510`, `_00514`, `_00537`).

---

#### 1.1.2 Calibration

1. **Implémentation de `asymmetricWorldPoints` (`CalibTools.py`) :**
   Dans le repère 3D lié à la mire ($Z = 0$), les coordonnées des centres des cercles d'une grille asymétrique suivent la convention OpenCV :
   ```python
   for i in range(rows):
       for j in range(cols):
           patternPoints.append([2 * j + i % 2, i, 0])
   ```

2. **Implémentation de `calibrateMono` (`CalibTools.py`) :**
   ```python
   ret, mtx, dist, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, pve = cv2.calibrateCameraExtended(
       objpoints, imgpoints, imgSize, None, None
   )
   ```

3. **Signification et cohérence de `mtx` et `dist` :**
   - **`mtx` (Matrice intrinsèque $K$ de taille $3 \times 3$)** :
     $$K = \begin{pmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{pmatrix}$$
     où $(f_x, f_y)$ sont les distances focales exprimées en pixels et $(c_x, c_y)$ les coordonnées en pixels du centre optique (point principal).
     - **Cohérence :** Les valeurs obtenues sont tout à fait cohérentes :
       - $f_x \approx f_y \approx 753.7\text{ px}$ (gauche) et $756.4\text{ px}$ (droite), ce qui montre que les pixels sont bien carrés ($f_x / f_y \approx 1.000$) et que les deux caméras ont des optiques quasi identiques.
       - $(c_x, c_y) \approx (507.6, 505.7)$ (gauche) et $(505.5, 509.1)$ (droite), très proches du centre géométrique théorique $(512, 512)$ d'une image $1024 \times 1024$.
   - **`dist` (Vecteur des 5 coefficients de distorsion)** :
     $$\text{dist} = (k_1, k_2, p_1, p_2, k_3)$$
     où $k_1, k_2, k_3$ modélisent la **distorsion radiale** et $p_1, p_2$ la **distorsion tangentielle** (décentrement des lentilles).
     - **Cohérence :** Le coefficient $k_1 \approx -0.17 < 0$ indique une **distorsion en barillet** (*barrel distortion*), nettement visible à l'œil nu sur les images brutes (courbure de l'horizon et des arbres sur les bords). Les coefficients tangentiels $p_1, p_2 \approx 10^{-4}$ sont très faibles, signe d'un bon alignement mécanique capteur/lentille.

4. **Signification de `rvecs` et `tvecs` :**
   - Pour chacune des $N$ images où la mire est détectée, `rvecs[i]` (vecteur de rotation de Rodrigues $\in \mathbb{R}^3$, dont la direction donne l'axe de rotation et la norme l'angle $\theta$) et `tvecs[i]` (vecteur de translation $\in \mathbb{R}^3$) représentent la **pose extrinsèque** $(R_i, t_i)$ de la mire $i$ dans le repère 3D de la caméra :
     $$P_{\text{caméra}} = R_i \, P_{\text{mire}} + t_i$$
   - La visualisation 3D produite par `visualizeBoards` confirme cette interprétation : chaque rectangle coloré représente la position et l'orientation 3D de la mire par rapport au repère caméra (pyramide rouge à l'origine).

---

#### 1.1.3 Rectification

1. **Implémentation de `computeCorrectionMapsMono` et rôle de `mapx`, `mapy` :**
   ```python
   mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, newImageSize, cv2.CV_32FC1)
   ```
   - **Signification de `mapx` et `mapy` :** Ce sont deux grilles (matrices 2D de même taille que l'image de sortie) contenant, pour chaque pixel $(u', v')$ de l'image rectifiée destination, les coordonnées flottantes $(u, v) = (\text{mapx}(v', u'), \text{mapy}(v', u'))$ du pixel correspondant dans l'image brute distordue (transformation inverse permettant une interpolation bilinéaire sans trous).

2. **Implémentation de `rectify` :**
   ```python
   dst = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
   ```

3. **Observation sur les images rectifiées et explication :**
   - **Observation :** Les droites de la scène (bords de la mire, troncs d'arbres) ne sont plus courbées, mais on observe des **bordures noires incurvées** en périphérie de l'image rectifiée.
   - **Explication :** Cela est dû à la correction de la distorsion radiale en barillet avec le paramètre `alpha = 1.0` dans `cv2.getOptimalNewCameraMatrix`. Avec `alpha = 1.0`, la nouvelle matrice caméra est choisie pour conserver 100 % des pixels de l'image originale : en « dé-courbant » les coins vers l'extérieur, les milieux des bords se rétractent vers l'intérieur, laissant apparaître des zones où aucun pixel source n'existe (pixels noirs). Avec `alpha = 0.0`, l'image serait recadrée (zoomée) pour éliminer ces bords noirs au prix de la perte de certains pixels périphériques.

---

### 1.2 Analyse

1. **Interprétation de la figure `plotRMS`, qualité de la calibration et facteurs clés :**
   - **Que représente la figure ?** Elle affiche l'erreur quadratique moyenne de reprojection (*Root Mean Square reprojection error*, en pixels) calculée individuellement pour chaque image de calibration (`pve`, points bleus) ainsi que le RMS global moyen sur l'ensemble des vues (ligne pointillée). L'erreur de reprojection mesure la distance euclidienne (en pixels) entre les centres des cercles détectés dans l'image et la projection 2D des points 3D de la mire via les paramètres estimés $(K, \text{dist}, R_i, t_i)$.
   - **Qualité de la calibration :** Le RMS moyen est très faible ($\approx 0.052\text{ px}$ à gauche, $\approx 0.044\text{ px}$ à droite, bien inférieur à $0.1\text{ px}$), ce qui traduit une excellente précision de ré-estimation sur les vues utilisées. Toutefois, la figure révèle une disparité entre la majorité des vues ($\text{RMS} \in [0.02, 0.04]\text{ px}$) et quelques vues aberrantes (*outliers* comme `_00290` à $0.11\text{ px}$ ou `_00466` à $0.09\text{ px}$).
   - **Facteurs importants pour un étalonnage précis :**
     1. **Couverture spatiale complète du capteur :** Placer la mire sur toute la surface de l'image (centre, bords et les 4 coins) pour bien contraindre la distorsion radiale ($k_1, k_2, k_3$) et le centre optique $(c_x, c_y)$.
     2. **Diversité des orientations 3D et des distances :** Incliner la mire selon différents angles (tangage, roulis, lacet) et profondeurs pour découpler la focale de la profondeur.
     3. **Conditions d'acquisition :** Éclairage homogène sans reflets spéculaires (soleil brûlant les cercles), absence de flou de bougé, planéité rigide de la mire et absence d'occultation par les doigts.

2. **Pistes d'amélioration dans notre cas :**
   - **Couvrir la moitié gauche de l'image :** Comme le montre la figure `visualizeBoards`, l'opérateur est resté du côté droit du champ de vue ($x > 0$ dans le repère caméra) sur toutes les prises de vue ; acquérir des images dans la moitié gauche améliorerait l'estimation globale de la distorsion et du point principal.
   - **Écarter les vues aberrantes (*outliers*) :** Sur le graphe `plotRMS`, les vues `_00290` (ombre de la main et bord extrême), `_00466` (forte inclinaison transformant les cercles en ellipses asymétriques), `_00062` et `_00453` présentent une erreur deux à trois fois supérieure à la moyenne. En filtrant les images ayant $\text{PVE} > 0.06\text{ px}$, le RMS global descend de **$0.0524\text{ px}$ à $0.0292\text{ px}$** pour la caméra gauche et de **$0.0443\text{ px}$ à $0.0322\text{ px}$** pour la caméra droite.

3. **Valeurs numériques obtenues en fin de calibration monoculaire :**

| Paramètre | Caméra Gauche (`*_0.png`) | Caméra Droite (`*_1.png`) |
| :--- | :---: | :---: |
| **Nombre de vues retenues** | $15 / 22$ | $15 / 22$ |
| **RMS global (pixels)** | **$0.0524\text{ px}$** | **$0.0443\text{ px}$** |
| **Focale $(f_x, f_y)$ (pixels)** | $(753.61,\; 753.73)$ | $(756.33,\; 756.43)$ |
| **Centre optique $(c_x, c_y)$ (pixels)** | $(507.55,\; 505.70)$ | $(505.52,\; 509.05)$ |
| **Distorsion radiale $(k_1, k_2, k_3)$** | $(-0.1734,\; 0.1281,\; -0.0308)$ | $(-0.1683,\; 0.1139,\; -0.0157)$ |
| **Distorsion tangentielle $(p_1, p_2)$** | $(-1.52 \times 10^{-4},\; -2.17 \times 10^{-4})$ | $(2.30 \times 10^{-4},\; 3.62 \times 10^{-4})$ |

---

## 2. Stéréovision

### 2.1 Calibration Stéréo

1. **Implémentation de `calibrateStereo` (`CalibTools.py`) :**
   Sur les **11 paires d'images** où la mire est simultanément détectée à gauche et à droite, on effectue d'abord l'étalonnage intrinsèque de chaque caméra via `cv2.calibrateCameraExtended`, puis l'étalonnage extrinsèque du banc stéréo via `cv2.stereoCalibrateExtended`.

2. **Signification des variables $R$ et $T$ retournées par `stereoCalibrateExtended` :**
   - **$R$ (Matrice de rotation $3 \times 3$)** et **$T$ (Vecteur de translation $3 \times 1$)** représentent la **transformation rigide extrinsèque entre la caméra gauche et la caméra droite** : pour tout point 3D exprimé par ses coordonnées $P_L$ dans le repère de la caméra gauche, ses coordonnées $P_R$ dans le repère de la caméra droite sont données par :
     $$P_R = R \, P_L + T$$
   - En particulier, $\|T\|$ correspond à la **base stéréo** (*baseline*, distance entre les deux centres optiques), et $T_x < 0$ reflète le fait que la caméra droite est décalée vers $+X$ par rapport à la caméra gauche (donc l'origine de la caméra gauche a une abscisse négative dans le repère de la caméra droite).

3. **Valeurs obtenues et analyse de cohérence :**
   - **RMS Stéréo :** **$0.0555\text{ px}$** (très faible, inférieur à un vingtième de pixel).
   - **Paramètres intrinsèques et distorsions (sur les 11 paires stéréo communes) :**
     - **Gauche :** $f_x = 754.60\text{ px}$, $f_y = 754.72\text{ px}$, $(c_x, c_y) = (508.36, 505.05)$, $\text{dist}_L = [-0.1728, 0.1289, 1.49\times 10^{-5}, -1.93\times 10^{-4}, -0.0315]$.
     - **Droite :** $f_x = 755.86\text{ px}$, $f_y = 755.95\text{ px}$, $(c_x, c_y) = (505.85, 508.89)$, $\text{dist}_R = [-0.1671, 0.1117, 2.10\times 10^{-4}, 5.12\times 10^{-4}, -0.0146]$.
   - **Paramètres extrinsèques $(R, T)$ :**
     $$R = \begin{pmatrix} 0.999983 & 0.005115 & 0.002807 \\ -0.005124 & 0.999982 & 0.003274 \\ -0.002791 & -0.003288 & 0.999991 \end{pmatrix}, \qquad T = \begin{pmatrix} -703.42 \\ 0.36 \\ 2.88 \end{pmatrix}\text{ mm}$$
     *(Note : avec la convention OpenCV $[2j + i\pmod 2, i, 0] \times 85\text{ mm}$ où le demi-pas vaut $85\text{ mm}$, $T_x = -703.42\text{ mm}$ ; en prenant $85\text{ mm}$ comme l'espacement entre deux cercles d'une même ligne soit un demi-pas de $42.5\text{ mm}$, la base physique réelle vaut $T_x = -351.71\text{ mm} \approx -35.2\text{ cm}$).*
   - **Cohérence des résultats :**
     - La matrice de rotation $R$ est extrêmement proche de la matrice identité $I_3$ (angles parasites $< 0.3^\circ$), ce qui confirme que les deux caméras du banc stéréo sont montées quasi parallèlement.
     - Le vecteur de translation $T$ est porté quasi exclusivement par l'axe horizontal $X$ ($T_y \approx 0.36\text{ mm} \approx 0$ et $T_z \approx 2.88\text{ mm} \approx 0$), ce qui correspond parfaitement à un banc stéréo horizontal de rover.

---

### 2.2 Rectification Stéréo

1. **Implémentation de `computeCorrectionMapsStereo` (`CalibTools.py`) :**
   ```python
   R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
       mtxLeft, distLeft, mtxRight, distRight, (w, h), R, T, alpha=alpha, newImageSize=newImageSize
   )
   mapxLeft, mapyLeft = cv2.initUndistortRectifyMap(mtxLeft, distLeft, R1, P1, newImageSize, cv2.CV_32FC1)
   mapxRight, mapyRight = cv2.initUndistortRectifyMap(mtxRight, distRight, R2, P2, newImageSize, cv2.CV_32FC1)
   ```

2. **Observations sur les images stéréo-rectifiées et rôle des lignes affichées :**
   - **Observations :** Les distorsions optiques sont corrigées dans les deux vues et les deux images sont ré-orientées dans un plan image commun coplanaire. Chaque détail physique de la scène (les centres des cercles de la mire, le sommet du rocher, l'horizon) se situe désormais exactement à la **même ordonnée $v$ (même ligne horizontale)** dans l'image gauche et dans l'image droite.
   - **Que représentent les lignes affichées ?** Elles représentent les **lignes épipolaires** horizontales après stéréo-rectification. Grâce au respect de la contrainte épipolaire en géométrie canonique rectifiée, le correspondant d'un point $(u_L, v_L)$ de l'image gauche se trouve sur la même ligne $v_R = v_L$ dans l'image droite, ce qui réduit la recherche de mise en correspondance stéréo (*stereo matching*) d'un problème 2D à une recherche 1D le long des lignes horizontales.

---

### 2.3 Reconstruction 3D

1. **Observation des résultats sur les images de test (`left_2.png` / `right_2.png`) :**
   La carte de disparité met clairement en évidence la géométrie 3D de la scène : un dégradé continu du premier plan (en bas, jaune/vert) vers l'arrière-plan (en haut, bleu foncé), avec le rocher posé sur le sol qui ressort nettement vers le haut-centre de l'image. La bande noire verticale à gauche ($u < 256$) correspond à la zone de l'image gauche sans recouvrement possible dans l'image droite pour la plage de recherche `numDisparities = 256`.

2. **Signification de l'image *Disparity map* et de ses valeurs :**
   - La **carte de disparité** associe à chaque pixel $(u_L, v)$ de l'image gauche rectifiée le décalage horizontal (en pixels) :
     $$d(u_L, v) = u_L - u_R$$
     où $(u_R, v)$ est le pixel homologue dans l'image droite rectifiée (calculé ici par l'algorithme Semi-Global Block Matching `cv2.StereoSGBM_create`, qui retourne des entiers 16 bits codés en virgule fixe avec 4 bits fractionnaires, soit $16 \times d$).
   - **Interprétation des valeurs :** La disparité $d$ est **inversement proportionnelle à la profondeur $Z$** :
     - Une **grande valeur de disparité** (couleurs chaudes : jaune/rouge) correspond à un objet **proche** du banc stéréo (le sol au premier plan et le bras du rover).
     - Une **faible valeur de disparité** (couleurs froides : bleu foncé) correspond à un objet **éloigné**.
     - Une valeur nulle ou masquée (noir) correspond aux pixels sans mise en correspondance valide (occultations, bord gauche hors champ de la caméra droite).

3. **Obtention d'une carte de profondeur à partir d'une image de disparité :**
   Par triangulation dans une configuration stéréo rectifiée canonique de focale rectifiée $f$ (en pixels) et de base stéréo $B = \|T\|$ (en mm ou m), la profondeur $Z$ de chaque pixel $(u, v)$ de disparité $d(u, v) > 0$ s'obtient par la relation :
   $$Z(u, v) = \frac{f \cdot B}{d(u, v)}$$
   *(Attention : avec `StereoSGBM` d'OpenCV, les valeurs brutes de sortie doivent d'abord être divisées par $16.0$ pour obtenir la disparité réelle en pixels : $d_{\text{px}} = \text{disparity} / 16.0$).*

4. **Reprojection d'une carte de profondeur 2D (ou de disparité) en un nuage de points 3D :**
   - **À partir de la carte de profondeur $Z(u, v)$ et des paramètres intrinsèques rectifiés $(f_x, f_y, c_x, c_y)$ :**
     Pour chaque pixel $(u, v)$ valide, on inverse le modèle sténopé (*pinhole*) pour calculer ses coordonnées 3D $(X, Y, Z)$ dans le repère caméra :
     $$\begin{cases}
     X = \dfrac{(u - c_x) \cdot Z(u, v)}{f_x} \\[6pt]
     Y = \dfrac{(v - c_y) \cdot Z(u, v)}{f_y} \\[6pt]
     Z = Z(u, v)
     \end{cases}$$
   - **Directement sous OpenCV à partir de la disparité $d(u, v)$ et de la matrice de reprojection $Q$ (fournie par `cv2.stereoRectify`) :**
     On utilise la fonction `points3D = cv2.reprojectImageTo3D(disparity / 16.0, Q)`, qui applique la transformation projective homogène :
     $$\begin{pmatrix} X \\ Y \\ Z \\ W \end{pmatrix} = Q \begin{pmatrix} u \\ v \\ d(u, v) \\ 1 \end{pmatrix}, \qquad Q = \begin{pmatrix} 1 & 0 & 0 & -c_x \\ 0 & 1 & 0 & -c_y \\ 0 & 0 & 0 & f \\ 0 & 0 & -\frac{1}{T_x} & \frac{c_x - c'_x}{T_x} \end{pmatrix}$$
     suivie de la division perspective $(X/W,\; Y/W,\; Z/W)$.
