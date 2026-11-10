# %% [markdown]
# # Case study : Le Robot Netoyeur
# 
# Ce case study utilise la boîte à outils MDP développée à l'INRAE https://pymdptoolbox.readthedocs.io/en/latest/index.html

# %%
import mdptoolbox, mdptoolbox.example, mdptoolbox.util, numpy
import numpy as np

# %% [markdown]
# On considère un robot ménager. Il peut se trouver soit dans le salon, soit à sa station de charge, soit être à court de batterie. Le salon peut être propre ou sale. Il y a donc cinq états : LD (dans le salon, sale), LC (dans le salon, propre), CD (au chargeur, sale), CC (au chargeur, propre), O (hors tension).
# 
# 
# ####  Actions
# Dans le salon, le robot peut choisir de nettoyer ou de charger.
# 
# Lorsqu'il se trouve dans la station de charge, le robot peut choisir de nettoyer ou de continuer à charger.
# 
# Lorsqu'il est hors tension,  chacune des deux actions (nettoyer, charger) aboutit au même résultat : rester hors tension.
# 
# ####  Récompenses
# 
# Le reward pour être dans un état propre est noté rc
# 
# Le reward pour être dans un état sale est  noté rd, et tel que  rd < rc  
# 
# Le reward pour être hors tension est noté costcrash - il doit être inférieur ou égal à rd (le salon devient sale  quand on ne le nettoie pas)
# 
# 
# ####  Transitions
# 
#      
# Lorsque le robot décide de nettoyer,
# * s'il est dans le salon, il risque de tomber en panne d'électricité avec une probabilité e
# * s'il se trouve dans la station de charge, il ne risque pas de tomber en panne d'électricité   
# * le nettoyage d'un sol propre le laisse propre
# * Le nettoyage d'un sol sale peut parfois échouer (même si la batterie est en bon état) - soit eps la probabilité d'échec du nettoyage.
# 
# Lorsque le robot décide de se recharger, l'action de rechargement l'amène toujours à la station de recharge. Lorsque le robot charge, **le salon??** peut passer de propre à sale avec une probabilité pDust - et bien sur, si le salon est déjà sale, il reste sale lorsque le robot est en charge

# %% [markdown]
# ## TODO

# %% [markdown]
# A. Modéliser le probleme par un MDP  ( horizon infini)  et decrire votre modele en details ; en particulier, dessiner le MDP et fournir les matrices de récompense et de transition. Expliquer et justifez votre modélisation.

# %%
STATE, ACTION = 5, 2
NETTOYER, CHARGER = range(ACTION)
LD, LC, CD, CC, O = range(STATE)
action2str = ["Nettoyer", "Charger"]
state2str = ["Salon sale", "Salon propre", "Chargeur sale", "Chargeur propre", "Hors tension"]

def make_P(e, eps, pDust):
    P = np.zeros((ACTION, STATE, STATE))
    # s'il est dans le salon, il risque de tomber en panne d'électricité avec une probabilité e
    P[NETTOYER, LD, O] = e
    P[NETTOYER, LC, O] = e

    # Le nettoyage d'un sol sale peut parfois échouer (même si la batterie est en bon état) - soit eps la probabilité d'échec du nettoyage
    # salon
    P[NETTOYER, LD, LD] = (1 - e) * eps
    P[NETTOYER, LD, LC] = (1 - e) * (1 - eps)
    P[NETTOYER, LC, LC] = 1 - e
    # chargeur
    P[NETTOYER, CD, LD] = eps
    P[NETTOYER, CD, LC] = 1 - eps
    P[NETTOYER, CC, LC] = 1
    # hors tension (état puit)
    P[NETTOYER, O, O] = 1

    P[CHARGER, LD, CD] = 1
    P[CHARGER, CD, CD] = 1
    P[CHARGER, LC, CC] = 1 - pDust
    P[CHARGER, LC, CD] = pDust
    P[CHARGER, CC, CC] = 1 - pDust
    P[CHARGER, CC, CD] = pDust
    P[CHARGER, O, O] = 1

    return P

P = make_P(0.1, 0.2, 0.3)           # test factice


# %%
def verify_transition_add_to1(P):
    for action in range(ACTION):
        for state in range(STATE):
            l = P[action, state, :]
            s = sum(l)
            if not np.isclose(s, 1.0):
                print(f"Action : \"{action2str[action]}\" on State : \"{state2str[state]}\" don't add up to 1 ({s}).")
                return False
    return True

if verify_transition_add_to1(P) == False:
    raise ValueError("Transition table contains incosistency.")
else:
    print("Transition table is verified.")

# %% [markdown]
# 
# B. Proposer des valeurs pour les récompenses qui sont cohérentes avec l'intuition (justifiez votre réponse)

# %%
R = np.zeros((STATE, ACTION))

rc = 10
rd = 0
costcrash = -20

if costcrash <= rd < rc:
    print("Reward respect constraints.")
else:
    raise ValueError("Rewards need to respect costcrash <= rd < rc.")

R[LC, NETTOYER] = rc                    # perd juste de la batterie a nettoyer quelque chose de propre
R[LD, NETTOYER] = rd                    # robot dans salon, salon sale => nettoie : bonne décision
R[CC, NETTOYER] = rc                    
R[CD, NETTOYER] = rd                    
R[O, NETTOYER] = costcrash              # pénaliser fortement le fait qu'un robot soit dans l'état puit O

R[LC, CHARGER] = rc                     # robot dans salon, salon propre => charger : bonne décision (une fois que le travail est fais aller charger est une bonne décision.)
R[LD, CHARGER] = rd                     # robot dans salon, salon salle => charger : plutôt mauvais décision (peut être une bonne décision si presque plus de batterie mais pas modélisé.)
R[CC, CHARGER] = rc                     # robot dans chargeur, salon propre => charger : bonne décision tant que le salon est propre
R[CD, CHARGER] = rd                     # robot dans chargeur, salon sale => charger : plutôt mauvais décision (peut être une bonne décision si presque plus de batterie mais pas modélisé.)
R[O, CHARGER] = costcrash               # pénaliser fortement le fait qu'un robot soit dans l'état puit O

print(R)

# %% [markdown]
# 
# 
# C. Utiliser l'algortihme d'itération de la valeur (ou d'itération de la politique) pour determiner la meilleure politique dans les cas suivants :
# 
# 
# 1. Lorsque la probabilité d'être à court de batterie est élevée
# 
# 2. Lorsqu'elle est faible
# 
# 3. Si le robot a une très bonne batterie (c'est-à-dire que la probabilité d'être à court de charge est très faible) ?
# 
# 4. Si le salon se salit rapidement (lorsque la probabilité de poussière augmente) ?
# 
# Interpréter et expliquer vos resultats.

# %% [markdown]
# Poster votre programme ci-dessous

# %%
scenario = {
    "1. Lorsque la probabilité d'être à court de batterie est élevée" : dict(e=0.5, eps=0.2, pDust=0.3),

    "2. Lorsqu'elle est faible" : dict(e=0.05, eps=0.2, pDust=0.3),

    "3. Si le robot a une très bonne batterie (c'est-à-dire que la probabilité d'être à court de charge est très faible) ?" : dict(e=0.001, eps=0.2, pDust=0.3),

    "4. Si le salon se salit rapidement (lorsque la probabilité de poussière augmente) ?" : dict(e=0.1, eps=0.2, pDust=0.9),
}

# %%
gamma = 0.8

for nom, params in scenario.items():
    P = make_P(**params)
    solve = mdptoolbox.mdp.ValueIteration(P, R, gamma)
    solve.run()
    print(f"{nom} : \n{[("pi(" + state2str[i]+ ") = " +action2str[a]) for i, a in enumerate(solve.policy)]}", end="\n\n")

# %% [markdown]
# Bonus
# 
# Ameliorez votre modèle de manière à prendre en considération plusieurs niveaux de batterie (élevé, moyen, faible  par exemple). Collez votre programme ci dessous et expliquez la politique optimale trouvee

# %%
STATE, ACTION = 13, 2
NETTOYER, CHARGER = range(ACTION)
LDH, LDM, LDL, LCH, LCM, LCL, CDH, CDM, CDL, CCH, CCM, CCL, O = range(STATE)
action2str = ["Nettoyer", "Charger"]
state2str = [
    "Salon sale - niveau élevé batt.", "Salon sale - niveau moyen batt.", "Salon sale - niveau bas batt.",
    "Salon propre - niveau élevé batt.", "Salon propre - niveau moyen batt.", "Salon propre - niveau bas batt.",
    "Chargeur sale - niveau élevé batt.", "Chargeur sale - niveau moyen batt.", "Chargeur sale - niveau bas batt.",
    "Chargeur propre - niveau élevé batt.", "Chargeur propre - niveau moyen batt.", "Chargeur propre - niveau bas batt.",
    "Hors tension",
]

# %% [markdown]
# **Je fais hypothès que `e` n'existe plus. Puisque mtn on a un état disant le niveau de batterie.**
# 
# - niveau bas de batterie = 0.25
# - niveau moyen de batterie = 0.1
# - niveau haut de batterie = 0.01

# %%
def make_P_bonus(eps, pDust, e_batt=(0.01, 0.1, 0.25)):
    # e_batt : probabilité de panne en nettoyant, pour un niveau de batterie (haut, moyen, bas)
    P = np.zeros((ACTION, STATE, STATE))
    SALON, CHARGEUR = 0, 1
    SALE, PROPRE = 0, 1
    HAUT, MOYEN, BAS = 0, 1, 2

    # indice de l'état, cohérent avec l'ordre LDH, LDM, LDL, LCH, ..., CCL
    def etat(lieu, proprete, batt):
        return lieu * 6 + proprete * 3 + batt

    for lieu in (SALON, CHARGEUR):
        for proprete in (SALE, PROPRE):
            for batt in (HAUT, MOYEN, BAS):
                s = etat(lieu, proprete, batt)

                # nettoyer : va au salon, risque de panne selon le niveau de batterie, perd un niveau
                e = e_batt[batt]
                batt_next = min(batt + 1, BAS)
                P[NETTOYER, s, O] = e
                if proprete == PROPRE:
                    P[NETTOYER, s, etat(SALON, PROPRE, batt_next)] = 1 - e
                else:
                    P[NETTOYER, s, etat(SALON, PROPRE, batt_next)] = (1 - e) * (1 - eps)
                    P[NETTOYER, s, etat(SALON, SALE, batt_next)] = (1 - e) * eps

                # charger : va au chargeur, gagne un niveau, le salon peut se salir
                batt_next = max(batt - 1, HAUT)
                if proprete == PROPRE:
                    P[CHARGER, s, etat(CHARGEUR, PROPRE, batt_next)] = 1 - pDust
                    P[CHARGER, s, etat(CHARGEUR, SALE, batt_next)] = pDust
                else:
                    P[CHARGER, s, etat(CHARGEUR, SALE, batt_next)] = 1

    # hors tension : état puits
    P[NETTOYER, O, O] = 1
    P[CHARGER, O, O] = 1

    return P

P = make_P_bonus(0.2, 0.3)          # test factice
if verify_transition_add_to1(P) == False:
    raise ValueError("Transition table contains incosistency.")
else:
    print("Transition table is verified.")

# %%
R = np.zeros((STATE, ACTION))

rc = 10
rd = 0
costcrash = -20

if costcrash <= rd < rc:
    print("Reward respect constraints.")
else:
    raise ValueError("Rewards need to respect costcrash <= rd < rc.")

for state in range(STATE):
    for action in range(ACTION):
        if state in [LCH, LCM, LCL, CCH, CCM, CCL]:
            R[state, action] = rc
        elif state in [LDH, LDM, LDL, CDH, CDM, CDL]:
            R[state, action] = rd
        else:
            R[state, action] = costcrash

print(R)

# %%
scenario_bonus = {
    "Batterie standard" : dict(eps=0.2, pDust=0.3),
    "Salon se salit vite" : dict(eps=0.2, pDust=0.9),
    "Très bonne batterie" : dict(eps=0.2, pDust=0.3, e_batt=(0.0, 0.05, 0.5)),
}

gamma = 0.8

for nom, params in scenario_bonus.items():
    P = make_P_bonus(**params)
    solve = mdptoolbox.mdp.ValueIteration(P, R, gamma)
    solve.run()
    print(f"{nom} : \n{[("pi(" + state2str[i]+ ") = " +action2str[a]) for i, a in enumerate(solve.policy)]}", end="\n\n")


