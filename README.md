# IA-GOMOKU
# Gomoku AI - Variante Long Pro

## Introduction

Ce projet est une Intelligence Artificielle (IA) capable de jouer au Gomoku en respectant les règles classiques ainsi que la variante Long Pro. Les spécificités incluent :

- Le premier coup Noir doit être au centre du plateau.
- Le troisième coup Noir est interdit dans une zone restreinte de 7×7 autour du centre.

Jusqu'à preuve du contraire en profondeur 3 cette ia est invincible la profondeur 2 est légèrement mois performante mais bien plus rapide.

## Structure du Plateau

### Représentation

Le plateau est une matrice de dimensions **15×15**, où :

- `0` représente une case vide.
- `1` représente un pion Noir.
- `2` représente un pion Blanc.

Une fonction `printBoard()` permet d'afficher la grille avec des indices en lettres (A, B, C...) pour les lignes et des chiffres (0, 1, 2...) pour les colonnes.

### Alignements possibles

Je pré-calcule tous les alignements possibles de 5 cases (horizontaux, verticaux, diagonaux) dans une liste **BARR**. Cela permet d'accélérer la vérification des alignements gagnants.

Chaque case du plateau est associée à une liste d'alignements qu'elle peut influencer, grâce à un dictionnaire **BARR\_PAR\_CASE**.

## Gestion des États et Alignements

### Suivi des alignements

Une structure `create_barres_state()` suit le nombre de pions Noir et Blanc dans chaque alignement. Je garde en mémoire :

- **countB** : nombre de pions Noirs par alignement.
- **countW** : nombre de pions Blancs par alignement.
- **active** : ensemble des alignements encore valides (sans pions mélangés).

### Mise à jour après chaque coup

À chaque mouvement joué, la fonction `update_barres_state()` :

1. Met à jour les compteurs de Noir et Blanc.
2. Désactive les alignements qui deviennent « mixtes ».

### Vérification de victoire

La fonction `has5_in_state()` détecte si un joueur aligne **au moins 5 pions consécutifs** dans un alignement actif. Si c'est le cas, la partie est gagnée.

## Génération des Coups

### Fonctionnement

`generateMoves(gs, player)` retourne l'ensemble des coups valides pour le joueur actuel. Par défaut, seuls les coups autour des pions déjà placés sont proposés pour optimiser la recherche.

### Contraintes Long Pro

1. **Premier coup Noir** : doit être en `(7,7)`.
2. **Deuxième coup (Blanc)** : libre.
3. **Troisième coup Noir** : interdit dans une zone `[4..10]×[4..10]` (gérée en filtrant les coups valides).

## Intelligence Artificielle : Algorithme Negamax

### Principe

J'utilise un **Negamax avec élagage alpha-bêta** pour choisir les meilleurs coups. L'idée est que maximiser son propre score revient à minimiser celui de l’adversaire en inversant simplement les valeurs d'évaluation.

### Fonctionnement

1. Conditions d'arrêt : victoire, défaite ou profondeur de recherche atteinte.
2. Génération des coups possibles.
3. Simulation de chaque coup avec `doMove()`.
4. Évaluation de l’état du plateau via `eval_barres_state()`.
5. Annulation du coup (rollback) avec `undoMove()`.
6. Utilisation de l’élagage alpha-bêta pour éviter des calculs inutiles.

### Optimisation : Table de Transposition

J'implémente une **table de transposition (TTdict)** pour stocker les évaluations des états déjà visités, évitant ainsi des recalculs coûteux en temps.

## Affichage et Gestion de la Partie

### Affichage du Plateau

La fonction `printBoard()` affiche la grille avec :

- `B` = Noir
- `W` = Blanc
- `.` = Case vide

### Logique de Jeu

La fonction `main()` gère le déroulement de la partie :

1. Initialisation du plateau.
2. Détermination du premier joueur (IA ou humain).
3. Application des règles Long Pro (premier coup Noir au centre, interdiction du 3e coup dans la zone restreinte).
4. Alternance des tours jusqu’à la victoire d’un joueur ou un plateau complet.
5. Choix des coups IA via `pickMove()` (appelant `negamax()`).

## Analyse

### Points Forts

- **Modularité** : séparation claire entre la génération des coups, l’évaluation et l'affichage.
- **Rapidité** : élagage alpha-bêta et pré-calcul des alignements permettent une exécution optimisée.
- **Pré-cacul des barre** : filtres explicite qui permet une bien plus grande intéligences de jeux, en éliminant directement les placements déjà mort et évaluant mieux ceux dangereux pour nous ou l'adversaire.

## Conclusion

J'ai développé une IA capable de jouer au Gomoku en respectant la variante Long Pro. L'algorithme **Negamax avec élagage alpha-bêta** offre des choix stratégiques tout en maintenant des performances raisonnables.
