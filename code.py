import math
import random
import numpy as np
import time

EMPTY = 0
BLACK = 1
WHITE = 2

SIZE = 15 # dimension des côtés du plateau

RESTRICT_MIN, RESTRICT_MAX = 4, 10 # Restriction pour le Long Pro

####################################
# Génération des barres sur 5 cases
####################################

BARR = [] # Set les barres de coups
BARR_PAR_CASE = {} # Set les cases qui ont des barres

def init_barr(): #Initialise toutes les combinaisons possibles de barres sur 5 cases
    global BARR, BARR_PAR_CASE
    BARR = []
    BARR_PAR_CASE = {}
    for r in range(SIZE): # Prépare une liste pour chaque case du plateau
        for c in range(SIZE):
            BARR_PAR_CASE[(r,c)] = []
    # 1) Les barres des lignes horizontales
    for r in range(SIZE):
        for c in range(SIZE - 4):
            bar = [(r, c+i) for i in range(5)] #Liste des barre sur la ligne r
            idx = len(BARR) # Index de la barre ( c'est le prochain index libre )
            BARR.append(bar) # La barre est ajouté à la liste globale des barres
            for (rr,cc) in bar: # Associer l'index de la barre à chaque case qu'elle parcours
                BARR_PAR_CASE[(rr,cc)].append(idx)
    # 2) Les barres des colonnes verticales
    for r in range(SIZE - 4):
        for c in range(SIZE):
            bar = [(r+i, c) for i in range(5)] #Liste des barre sur la colonne c
            idx = len(BARR) # Index de la barre ( c'est le prochain index libre )
            BARR.append(bar) # La barre est ajouté à la liste globale des barres
            for (rr,cc) in bar: # Associer l'index de la barre à chaque case qu'elle parcours
                BARR_PAR_CASE[(rr,cc)].append(idx)
    # 3) Les barres des diagonales de gauche à droite
    for r in range(SIZE - 4):
        for c in range(SIZE - 4):
            bar = [(r+i, c+i) for i in range(5)] #Liste des barre sur la diagonale
            idx = len(BARR) # Index de la barre ( c'est le prochain index libre )
            BARR.append(bar) # La barre est ajouté à la liste globale des barres
            for (rr,cc) in bar: # Associer l'index de la barre à chaque case qu'elle parcours
                BARR_PAR_CASE[(rr,cc)].append(idx)
    # 4) Les barres des diagonales de droite à gauche
    for r in range(4, SIZE):
        for c in range(SIZE - 4):
            bar = [(r-i, c+i) for i in range(5)] #Liste des barre sur la diagonale
            idx = len(BARR) # Index de la barre ( c'est le prochain index libre )
            BARR.append(bar) # La barre est ajouté à la liste globale des barres
            for (rr,cc) in bar: # Associer l'index de la barre à chaque case qu'elle parcours
                BARR_PAR_CASE[(rr,cc)].append(idx)

####################
# État des "barres"
####################

def create_barres_state(): # Crée l'état des barre dans le jeu
    n = len(BARR) # Set le nombre de barre
    return {
        'countB': [0]*n, # Set le nombre de barre Noir
        'countW': [0]*n, # Set le nombre de barre Blanche
        'active': set(range(n)) # Set les barres active ( toute en début de game )
    }

def clone_barres_state(barres_state): # Clone l'état des barre dans le jeu pour y appliquer des actions
    return {
        'countB': barres_state['countB'][:],
        'countW': barres_state['countW'][:],
        'active': barres_state['active'].copy()
    }

def update_barres_state(barres_state, r, c, player): # Met à jour le statut des barres
    bar_idxs = BARR_PAR_CASE[(r,c)] # Set la liste d'index des barres de la case
    adv = BLACK if player==WHITE else WHITE
    for idx in bar_idxs:
        if idx not in barres_state['active']: # Vérifie que la barre n'est pas active dans le statut des barres
            continue
        if player == BLACK: # Vérifie la barre doit être désactivé pour le joueur Noir
            barres_state['countB'][idx] += 1 # On incrémente le compteur de case occupées par le joueur Noir pour cette barre
            # si barre mixte ( plusieur couleur dessus ) elle deviens inactive
            if barres_state['countW'][idx] > 0:
                barres_state['active'].discard(idx)
            elif barres_state['countB'][idx] >= 5:
                pass
        else: # Vérifie la barre doit être désactivé pour le joueur Blanc
            barres_state['countW'][idx] += 1 # On incrémente le compteur de case occupées par le joueur Blanc pour cette barre
            # si barre mixte ( plusieur couleur dessus ) elle deviens inactive
            if barres_state['countB'][idx] > 0:
                barres_state['active'].discard(idx)
            elif barres_state['countW'][idx] >= 5:
                pass

def has5_in_state(barres_state): # Regarde si 5 coup sont aligné
    for index in barres_state['active']: # Vérifie si il y a une barre de 5 coup ou plus pour les Blanc
        if barres_state['countB'][index] >= 5:
            return BLACK # Retourne les Noir comme ayant une barre de 5 coup
        if barres_state['countW'][index] >= 5:
            return WHITE # Retourne les Blanc comme ayant une barre de 5 coup
    return 0 # Retourne 0 si personne à une barre de 5 coup

def eval_barres_state(barres_state): # Evalue qui à l'avantage, Noir ou Blanc, sur chaque barre
    pw = [0,1,6,16,200,99999]  # pondérations utilisé pour l'évaluation
    scN=0
    scW=0
    for idx in barres_state['active']: # Parcours les barres actives
        bN = barres_state['countB'][idx] # Nombre de cases occupées par  le joueur Noir
        bW = barres_state['countW'][idx] # Nombre de cases occupées par  le joueur Blanc
        if bN>0 and bW>0: # Si la barre est mixte, elle ne contribue pas au score
            continue
        if bN>0: # Si la barre est occupé uniquement par les Noir, on ajoute le score de la pondération correspondante
            scN += pw[bN]
        if bW>0: # Si la barre est occupé uniquement par les Blanc, on ajoute le score de la pondération correspondante
            scW += pw[bW]
    return scN - scW # Retourne qui à l'avantage en les Noir et les Blanc

################################
# Représentation globale du jeu
################################

def create_game_state(): # Crée le statut de la partie, le Game State
    board = np.zeros((SIZE,SIZE), dtype=int) # Crée un tableau 15x15
    barres = create_barres_state()
    played = set() # Crée le set des coup qui ont été joué
    return {
        'board': board,
        'barres': barres,
        'played': played,
        'moves_count': 0
    }

def clone_game_state(gs): # Clone le Game State pour effectué des actions dessus
    return {
        'board': gs['board'].copy(),
        'barres': clone_barres_state(gs['barres']),
        'played': gs['played'].copy(),
        'moves_count': gs['moves_count']
    }

def getWinner(gs): # Vérifie si il y a un gagnant
    w = has5_in_state(gs['barres']) # Vérifie si il y a 5 coups alignées et renvoie le vainqueur ou 0 si la partie continue
    if w != 0:
        return w
    if len(gs['played']) >= SIZE*SIZE: # Si le nombre de coup joué est égale à la taille du plateau, la partie est nul
        return -1  # draw
    return 0

def doMove(gs, r, c, player): # Joue le coup du joueur associer
    gs['board'][r][c] = player # Met sur la case r,c la couleur du joueur qui à joué le coup
    update_barres_state(gs['barres'], r, c, player) # Met à jour l'état des barres de coup
    gs['played'].add((r,c)) # Ajoute le coup au coup joué
    gs['moves_count'] += 1 # Met à jour le nombre total de coup joué

def undoMove(gs, r, c, old_barres_state): # Enlève un coup joué
    gs['board'][r][c] = EMPTY # Enlève sur la case r,c la couleur
    gs['played'].discard((r,c)) # Enlève le coup au coup joué
    gs['barres'] = old_barres_state # Reviens à l'état des barres de coup d'avant
    gs['moves_count'] -= 1 # Met à jour le nombre total de coup joué

######################
# Génération de coups
######################

def generateMoves(gs, player): # Génere des coups possible
    mc = gs['moves_count'] # Nombre de coup joué
    board = gs['board'] # Le plateau actuel
    # 3e coup de la partie -> hors zone [4..10] pour le LongPro
    if mc == 2 and player == BLACK:
        res = set()
        for r in range(SIZE): # genrère tous les coup possible a joué hors zone pour le LongPro et les ajoutes au set "res"
            for c in range(SIZE):
                if board[r][c] == EMPTY:
                    if not (RESTRICT_MIN <= r <= RESTRICT_MAX and RESTRICT_MIN <= c <= RESTRICT_MAX):
                        res.add((r,c))
        return res # Retourne tous les coup possibles hors zone
    return getAroundOrAll(gs) # Sinon éxecute la fonction getAroundOrAll

def getAroundOrAll(gs):
    board = gs['board'] # Set l'état du plateau
    out = set() # Set pour stocker les coups possibles
    for (r,c) in gs['played']: # Pour toute les case joué, on regarde les 8 cases voisines
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                rr = r+dr
                cc = c+dc
                if 0 <= rr < SIZE and 0 <= cc < SIZE: # Vérifie que la case est dans le plateau
                    if board[rr][cc] == EMPTY: # Vérifie si la case est vide
                        out.add((rr,cc)) # Ajoute la case à la liste de coup posible
    if len(out) < 5: # Si le nombre de case disponible autour des coup joué est inférieur à 5, on renvoie toute les case qui sont vides
        out = {(r,c) for r in range(SIZE) for c in range(SIZE)
               if board[r][c] == EMPTY}
    return out # Renvoie les coups possibles ou tout ceux autour des cases joué

#######################
# NegaMax (alpha-beta)
#######################

def negamax(gs, depth, alpha, beta, color): # Evalue le score d'utilité des coups jouables
    # Vérifie si un joueur va gagner la partie ou si la profondeur max est atteinte ou si toute les cases sont joué ( match nul )
    w = has5_in_state(gs['barres'])
    if w == BLACK:
        return (1e9 if color>0 else -1e9)
    if w == WHITE:
        return (1e9 if color<0 else -1e9)
    if len(gs['played']) >= SIZE*SIZE or depth <= 0: # Vérifie si la profondeur max est atteint ou si toute les cases sont joué
        return color * eval_barres_state(gs['barres']) # Retourne une évaluation du score pour cet état du plateau en fonction du tour ( quel joueur -- > color )

    bestVal = -math.inf # Set la meilleur valeur comme moins l'infini à cette étape de récursion
    moves = generateMoves(gs, (BLACK if color>0 else WHITE)) # Set moves, tout les coups possibles de jouer à cette étape de récursion
    localAlpha = alpha # Set un clone d'alpha pour suivre la meilleure valeur dans la branche actuelle

    for (r,c) in moves:
        oldBarres = clone_barres_state(gs['barres']) # Set un clone de l'état des barres
        doMove(gs, r, c, (BLACK if color>0 else WHITE)) # Fait le coup dans une des cases possible

        val = -negamax(gs, depth - 1, -beta, -localAlpha, -color) # Evalue le score d'utilité du coup grace à une récusion de la fonction

        undoMove(gs, r, c, oldBarres) # Enlève le coup jouer pour revenir à l'état initial du plateau et du statut des barres
        if val > bestVal: # Determine le meilleur coup entre celui actuel et les anciens
            bestVal = val
        if bestVal > localAlpha: #Met à jour alpha en fonction de la meilleur valeur trouvé
            localAlpha = bestVal
        if localAlpha >= beta: # Si alpha dépasse ou atteint beta, ça veut dire que les autre branches n'influenceront pas le résultat final, on arrête donc l'étalage
            break
    return bestVal # Retourne le meilleur coup possible dans cette étapes de récursion

def pickMove(gs, depth, color): # Evalue le meilleur coup à jouer pour l'IA
    bestVal = -math.inf # Set la meilleur valeur comme moins l'infini
    bestMove = (-1, -1) # Set le meilleur coup a joué
    alpha, beta = -math.inf, math.inf # Set alpha comme la meilleure valeur que le joueur maximisant peut avoir et beta comme la meilleure valeur que le joueur minimisant peut avoir
    moves = generateMoves(gs, (BLACK if color>0 else WHITE)) # Set moves, tout les coups possibles de jouer

    for (r,c) in moves: # Teste chaque coup possible pour avoir leur score et choisir le meilleur possible
        oldBarres = clone_barres_state(gs['barres']) # Set un clone de l'état des barres
        doMove(gs, r, c, (BLACK if color>0 else WHITE)) # Fait le coup dans une des cases possible

        val = -negamax(gs, depth - 1, -beta, -alpha, -color) # Evalue le score d'utilité du coup grace à la fonction negamax

        undoMove(gs, r, c, oldBarres) # Enlève le coup jouer pour revenir à l'état initial du plateau et du statut des barres
        if val > bestVal: # Determine le meilleur coup entre celui actuel et les anciens
            bestVal = val
            bestMove = (r, c)
        if bestVal > alpha: # Met à jour alpha en fonction de la meilleur valeur trouvé
            alpha = bestVal
        if alpha >= beta: # Si alpha dépasse ou atteint beta, ça veut dire que les autre branches n'influenceront pas le résultat final, on arrête donc l'étalage
            break
    return bestMove # Retourne le meilleur coup possible

############
# Affichage
############

def printBoard(gs): # Permet d'afficher le jeu
    board = gs['board'] # Set la variable tableau comme étant l'état du jeu
    print("  ", end="")
    for col in range(SIZE): # Affiche la première ligne
        print(f"{col:2d}", end=" ")
    print("") # Saute une ligne
    for row in range(SIZE): #Pour chaque ligne du tableau, va afficher la ligne et son remplissage
        rowChar = chr(row + ord('A'))
        print(f"{rowChar:2s} ", end="")
        for col in range(SIZE): # Remplis le tableau par des points si la case est vide et par des lettre, B ou W, pour les cases jouées
            val = board[row][col]
            if val == EMPTY:
                print(".", end="  ")
            elif val == BLACK:
                print("B", end="  ")
            else:
                print("W", end="  ")
        print("") # Saute une ligne

############
# Main loop
############

# Diminuer la profondeur pour accélérer les calculs
MAX_DEPTH = 3  # 2 ou 3 pour des coups < 5 secondes (dépend de votre machine)

def main(): # Lance une partie
    init_barr() # Génération des barres de 5
    gs = create_game_state() # création du Game State

    print("Qui commence ? (1) Humain  (2) IA") # Demande à l'utilisateur qui commence, l'IA ou l'autre joueur
    choice = input("Entrez votre choix : ").strip()

    # Détermine qui est Noir / qui est Blanc
    if choice == '1':
        # L'humain est Noir, l'IA est Blanc
        humanColor = BLACK
        aiColor = WHITE

        # L'humain DOIT jouer (7,7) pour le premier coup (Long Pro)
        while True:
            mv = input("Premier coup Noir (obligatoirement H7) : ").strip() # Demande à l'utilisateur qui commence de faire le premier coup
            if len(mv) < 2: # Vérifie que le format est respecter
                print("Invalide.")
                continue
            rr = ord(mv[0].upper()) - ord('A')
            try: # Vérifie si l'entrée est valide
                cc = int(mv[1:])
            except ValueError:
                print("Invalide.")
                continue
            if rr == 7 and cc == 7: # Vérifie que le premier coup est bien H7
                doMove(gs, rr, cc, BLACK) #Joue le coup en 7,7 de la part des noirs
                print("Premier coup Black = (7,7).")
                break
            else:
                print("Le premier coup Black doit être H7.")

        current_player = WHITE # Donne le tour au joueur Blanc

    else:
        # L'IA est Noir, l'humain est Blanc
        humanColor = WHITE
        aiColor = BLACK
        doMove(gs, 7, 7, BLACK) # Joue le coup en 7,7 de la part des noirs
        print("Premier coup Black = (7,7).")
        current_player = WHITE # Donne le tour au joueur Blanc

    while True: # Execute la partie tant qu'il n'y a pas de gagnant ou que la partie est nul
        printBoard(gs) # Affiche le tableau
        w = getWinner(gs) # Vérifie si le match est fini avec un gagnant ou est nul et l'affiche et sort de la boucle
        if w == BLACK:
            print("Black gagne !")
            break
        elif w == WHITE:
            print("White gagne !")
            break
        elif w == -1:
            print("Match nul (plateau plein).")
            break

        if current_player == humanColor:
            # Tour du joueur humain
            print(f"Tour Humain ({'Black' if humanColor==BLACK else 'White'}).")
            while True:
                mv = input("Votre coup (ex: A3) : ").strip()  # Demande à l'utilisateur de faire sont coup
                if len(mv) < 2: # Vérifie que le format est respecter
                    print("Invalide.")
                    continue
                rr = ord(mv[0].upper()) - ord('A')
                try: # Vérifie si l'entrée est valide
                    cc = int(mv[1:])
                except ValueError:
                    print("Invalide.")
                    continue
                if not (0 <= rr < SIZE and 0 <= cc < SIZE): # Vérifie si l'entrée est dans le tableau
                    print("Hors limites.")
                    continue
                if gs['board'][rr][cc] != EMPTY: # Vérifie si la case est occupée
                    print("Case occupée.")
                    continue
                doMove(gs, rr, cc, humanColor) # Joue le coup sur la case voulu
                break
        else:
            # Tour de l'IA
            print(f"Tour de l'IA ({'Black' if aiColor==BLACK else 'White'}):")
            start_time = time.time() # Set un checkpoint dans le temps pour pouvoir calculer le temps total d'exécution du code de l'IA
            (r, c) = pickMove(gs, MAX_DEPTH, (+1 if aiColor==BLACK else -1)) # Calcul le meilleur coup que l'IA peux faire
            elapsed = time.time() - start_time # Calcule le temps total d'exécution du code de l'IA

            doMove(gs, r, c, aiColor) # Joue le coup sur la case voulu
            print(f"L'IA joue {chr(r + ord('A'))}{c} en {elapsed:.3f} secondes")

        # Alterne le joueur
        current_player = WHITE if current_player == BLACK else BLACK # Donne le tour à l'autre joueur

    print("Fin de partie.")

if __name__ == "__main__": # Exécute le main
    main()
