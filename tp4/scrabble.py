import pickle
from tkinter import Canvas, Tk, W, S, N, Frame, Button, messagebox, simpledialog, Label, StringVar, Toplevel
from pathlib import Path
from random import choice, shuffle

from tp4.joueur import Joueur
from tp4.plateau import Plateau
from tp4.jeton import Jeton
from tp4.utils import dessiner_jeton
from tp4.exceptions import *

BASE_DIR = Path(__file__).resolve().parent


class Scrabble(Tk):
    """
    Classe Scrabble qui implémente aussi une partie de la logique de jeu.
    En dérivant de la classe tkinter.Tk, la classe Scrabble gère aussi la fenêtre principale de l'interface graphique

    Attributes:
        dictionnaire (list): Contient tous les mots qui peuvent être joués sur dans cette partie.
                             (afin de savoir si un mot est permis, on va vérifier s'il est dans dictionnaire)
        plateau (Plateau): Un objet de la classe Plateau. On y place des jetons et il nous dit le nombre de points
                           gagnés.
        jetons_libres (list): La liste de tous les jetons dans le sac (instances de la classe Jeton), c'est là que
                              chaque joueur pige des jetons quand il en a besoin.
        joueurs: (list): L'ensemble des joueurs de la partie (instances de la classe Joueur)
        joueur_actif (Joueur): Le joueur qui est en train de jouer le tour en cours. Si aucun joueur alors None.
        nb_pixels_par_case (int): Nombre de pixel qu'occupe la représentation graphique d'une case.
        chevalet (tkinter.Canvas): Rendu graphique du chevalet du joueur actif.
        position_selection_chevalet (int): Mémorise la position du jeton sélectionné sur le chevalet
                                            (vaut None si aucun jeton n'est sélectionné)
    """

    def __init__(self):
        """
        Constructeur
        """
        super().__init__()

        self.title('Scrabble')

        self.nb_pixels_par_case = 50

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.plateau = Plateau(self, self.nb_pixels_par_case)
        self.plateau.grid(row=0, column=0, sticky=N)

        self.chevalet = Canvas(self, height=self.nb_pixels_par_case, width=7 * self.nb_pixels_par_case, bg='#645b4b')
        self.chevalet.grid(row=1, column=0, sticky=S)

        self.position_selection_chevalet = None

        # Création des boutons
        panneau_boutons = Frame(self)
        panneau_boutons.grid(row=0, column=1, sticky=S)

        bouton = (Button(panneau_boutons, text="Mélanger le chevalet", fg='#4285F4',
                         command=self.clic_melanger_chevalet, width=25,
                         height=2))
        bouton.grid(row=0, column=0, pady=15)

        bouton = (Button(panneau_boutons, text="Jouer", fg='#DB4437',
                         command=self.jouer_un_tour, width=25,
                         height=2))
        bouton.grid(row=1, column=0, pady=15)

        bouton = (Button(panneau_boutons, text="Passer son tour", fg='#F4B400',
                         command=self.passer_son_tour, width=25,
                         height=2))
        bouton.grid(row=2, column=0, pady=15)

        bouton = (Button(panneau_boutons, text="Nouvelle partie", fg='#0f9f58',
                         command=self.nouvelle_partie, width=25,
                         height=2))
        bouton.grid(row=3, column=0, pady=15)

        bouton = (Button(panneau_boutons, text="Contrôle",
                         command=self.fenetre_controle, width=25,
                        height=1))
        bouton.grid(row=4, column=0, pady=5)

        # Associe les évènements aux méthodes correspondants
        self.plateau.tag_bind('case', '<Button-1>', self.clic_case_plateau)
        self.chevalet.tag_bind('lettre', '<Button-1>', self.clic_lettre_chevalet)
        self.bind('<Button-3>', self.reinitialiser_tour)
        self.bind('<Escape>', self.reinitialiser_tour)

        # Vous pouvez afficher une boite de dialogue afin de demander à l'utilisateur le nombre de joueurs
        # et la langue souhaitée et ensuite passer ces valeurs en arguments à la méthode initialiser_jeu
        nbr_joueurs = simpledialog.askinteger('Joueurs', 'Entrez le nombre de joueurs (2-4)')
        while nbr_joueurs not in range(2, 5):
            messagebox.showerror('Oups!', "Le nombre de joueurs doit être entre 2 et 4")
            nbr_joueurs = simpledialog.askinteger('Joueurs', 'Entrez le nombre de joueurs (2-4)')
        langue = simpledialog.askstring('Langue', 'Entrez FR pour francais et EN pour anglais')
        while langue not in ('en' 'EN', 'fr', 'FR'):
            messagebox.showerror('Oups!', "La langue doit être FR ou EN")
            langue = simpledialog.askstring('Langue', 'Entrez FR pour francais et EN pour anglais')

        self.initialiser_jeu(nbr_joueurs, langue)
        # Creation des informations joueur
        self.afficher_info_joueurs()

    def fenetre_controle(self):
        window = Toplevel(self)
        window.geometry("750x150")
        window.title('Contrôle')
        regle = Label(window, text='<Escape> ou <Button-3> --> Ramène les jetons dans le chevalet', pady=10)
        regle.grid(row=1, column=0, sticky=W)
        regle = Label(window, text='                       <Button-1> --> Permet de prendre un jeton et permet de placer un jeton sur le plateau', pady=10)
        regle.grid(row=2, column=0, sticky=N)


    def nouvelle_partie(self):
        """Detruit la partie presente et en cree une nouvelle.
                """
        result = messagebox.askyesno('Nouvelle partie', 'Êtes-vous sur de vouloir créer une nouvelle partie ?',
                                     icon='question')
        if result is True:
            self.destroy()
            jeu = Scrabble()

            jeu.mainloop()
        else:
            pass

    def passer_son_tour(self):
        """Passe le tour du joueur.


                """
        self.reinitialiser_tour()
        self.joueur_suivant()

    def afficher_info_joueurs(self):
        """Affiche les info des joueurs.


        """
        panneau_joueurs = Frame(self)
        panneau_joueurs.grid(row=0, column=1, sticky=N)
        i = 0
        for x in self.joueurs:
            var = StringVar()
            var.set(x.__str__())
            if x == self.joueur_actif:
                l = Label(panneau_joueurs, textvariable=var, bg='#00fbff', relief='raised', width=25, pady=20)
            else:
                l = Label(panneau_joueurs, textvariable=var, pady=20)
            l.grid(row=0 + i, column=0)
            i = i + 1

    def initialiser_jeu(self, nb_joueurs=2, langue='fr'):
        """
        Étant donné un nombre de joueurs et une langue, cette méthode crée une partie de scrabble.

        Pour une nouvelle partie de scrabble:
        - La liste des joueurs est créée et chaque joueur porte automatiquement le nom Joueur 1, Joueur 2, ... Joueur n,
          où n est le nombre de joueurs;
        - Le joueur_actif est None.

        Args:
            nb_joueurs (int): nombre de joueurs de la partie (au minimun 2 au maximum 4).
            langue (str): 'FR' pour la langue française et 'EN' pour la langue anglaise. Charge en mémoire les mots
                          contenus dans le fichier "dictionnaire_francais.txt" ou "dictionnaire_anglais.txt".
            La langue détermine aussi les jetons de départ.
            Voir https://fr.wikipedia.org/wiki/Lettres_du_Scrabble
            Note: Dans notre scrabble, nous n'utiliserons pas les jetons blancs (jokers) qui ne contiennent aucune lettre.

        Raises:
            AssertionError:
                - Si la langue n'est ni 'fr', 'FR', 'en', ou 'EN'.
                - Si le nombre de joueurs n'est pas compris entre 2 et 4 (2 et 4 étant inclus).
        """
        if not langue.upper() in ['FR', 'EN']:
            raise MauvaiseLangue
        if not 2 <= nb_joueurs <= 4:
            raise MauvaisNbrJoueurs

        self.joueur_actif = None
        self.joueurs = [Joueur(f'Joueur {i + 1}') for i in range(nb_joueurs)]

        if langue.upper() == 'FR':
            # Infos disponibles sur https://fr.wikipedia.org/wiki/Lettres_du_Scrabble
            data = [('E', 15, 1), ('A', 9, 1), ('I', 8, 1), ('N', 6, 1), ('O', 6, 1),
                    ('R', 6, 1), ('S', 6, 1), ('T', 6, 1), ('U', 6, 1), ('L', 5, 1),
                    ('D', 3, 2), ('M', 3, 2), ('G', 2, 2), ('B', 2, 3), ('C', 2, 3),
                    ('P', 2, 3), ('F', 2, 4), ('H', 2, 4), ('V', 2, 4), ('J', 1, 8),
                    ('Q', 1, 8), ('K', 1, 10), ('W', 1, 10), ('X', 1, 10), ('Y', 1, 10),
                    ('Z', 1, 10)]


            chemin_fichier_dictionnaire = BASE_DIR / 'dictionnaire_francais.txt'
        elif langue.upper() == 'EN':
            # Infos disponibles sur https://fr.wikipedia.org/wiki/Lettres_du_Scrabble
            data = [('E', 12, 1), ('A', 9, 1), ('I', 9, 1), ('N', 6, 1), ('O', 8, 1),
                    ('R', 6, 1), ('S', 4, 1), ('T', 6, 1), ('U', 4, 1), ('L', 4, 1),
                    ('D', 4, 2), ('M', 2, 3), ('G', 3, 2), ('B', 2, 3), ('C', 2, 3),
                    ('P', 2, 3), ('F', 2, 4), ('H', 2, 4), ('V', 2, 4), ('J', 1, 8),
                    ('Q', 1, 10), ('K', 1, 5), ('W', 2, 4), ('X', 1, 8), ('Y', 2, 4),
                    ('Z', 1, 10)]
            chemin_fichier_dictionnaire = BASE_DIR / 'dictionnaire_anglais.txt'
        self.jetons_libres = [Jeton(lettre, valeur) for lettre, occurences, valeur in data for i in range(occurences)]
        with open(chemin_fichier_dictionnaire, 'r') as f:
            self.dictionnaire = [x[:-1].upper() for x in f.readlines() if len(x[:-1]) > 1]

        self.joueur_suivant()

    def clic_melanger_chevalet(self, event=None):
        """
        Modifie aléatoirement l'ordre des jetons sur le chevalet du joueur actif.

        Args:
            event (tkinter.Event): L'évènement ayant causé l'appel de la méthode (non utilisé).
        """
        self.reinitialiser_tour()
        self.joueur_actif.melanger_jetons()
        self.dessiner_chevalet()

    def reinitialiser_tour(self, event=None):
        """
        Lorsque le joueur actif a déplacé des jetons de son chevalet au plateau, cette méthode replace
        ces jetons sur le chevalet.

        Args:
            event (tkinter.Event): L'évènement ayant causé l'appel de la méthode (non utilisé).
        """
        liste_jetons = self.plateau.retirer_jetons_en_jeu()[0]
        for jeton in liste_jetons:
            self.joueur_actif.ajouter_jeton(jeton)

        self.position_selection_chevalet = None
        self.plateau.dessiner()
        self.dessiner_chevalet()
        self.afficher_info_joueurs()

    def clic_lettre_chevalet(self, event):
        """
        Gère la sélection d'un jeton sur le chevalet du joueur actif.

        Args:
            event (tkinter.Event): L'évènement ayant causé l'appel de la méthode.
        """
        self.position_selection_chevalet = event.x // self.nb_pixels_par_case
        self.dessiner_chevalet()

    def clic_case_plateau(self, event):
        """
        Gère le déplacement d'un jeton à partir du chevalet jusqu'au plateau.

        Args:
            event (tkinter.Event): L'évènement ayant causé l'appel de la méthode.
        """
        if self.position_selection_chevalet is None:
            return

        jeton = self.joueur_actif.retirer_jeton(self.position_selection_chevalet)

        if self.plateau.ajouter_jeton_en_jeu(jeton, event.x, event.y):
            self.position_selection_chevalet = None
            self.plateau.dessiner()
            self.dessiner_chevalet()
        else:
            self.joueur_actif.ajouter_jeton(self.position_selection_chevalet)

    def mot_permis(self, mot):
        """
        Permet de savoir si un mot est permis dans la partie ou pas 
        en vérifiant dans le dictionnaire.

        Args:
            mot (str): Mot à vérifier.

        Returns:
            bool: True si le mot est dans le dictionnaire, False sinon.
        """
        return mot.upper() in self.dictionnaire

    def determiner_gagnant(self):
        """
        Détermine le joueur gagnant.
        Le joueur gagnant doit avoir un pointage supérieur ou égal à celui des autres.

        Returns:
            Joueur: Le joueur gagnant. Si plusieurs sont à égalité, on en retourne un seul parmi ceux-ci.
        """
        return max(self.joueurs, key=lambda j: j.points)

    def partie_terminee(self):
        """
        Vérifie si la partie est terminée. Une partie est terminée si il n'existe plus de jetons libres ou il reste
        moins de deux (2) joueurs. C'est la règle que nous avons choisi d'utiliser pour ce travail, donc essayez de
        négliger les autres que vous connaissez ou avez lu sur Internet.

        Returns:
            bool: True si la partie est terminée, et False autrement.
        """
        return len(self.jetons_libres) == 0 or len(self.joueurs) < 2

    def joueur_suivant(self):
        """
        Change le joueur actif.
        Le nouveau joueur actif est celui à l'index du (joueur courant + 1) % nb_joueurs.
        Si on n'a aucun joueur actif, on détermine au hasard le suivant.
        """
        try:
            if self.joueur_actif is None:
                self.joueur_actif = choice(self.joueurs)
            else:
                self.joueur_actif = self.joueurs[(self.joueurs.index(self.joueur_actif) + 1) % len(self.joueurs)]

            if self.joueur_actif.nb_a_tirer() > 0:
                for jeton in self.tirer_jetons(self.joueur_actif.nb_a_tirer()):
                    self.joueur_actif.ajouter_jeton(jeton)
            self.position_selection_chevalet = None
            self.dessiner_chevalet()
            self.afficher_info_joueurs()
        except FinPartie:
            gagnant = self.determiner_gagnant()
            messagebox.showinfo('Oops', f'Le gagnant est {gagnant.nom} avec {gagnant.points} points')
            self.nouvelle_partie()
            self.quit()

    def dessiner_chevalet(self):
        """
        Dessine le chevalet du joueur actif sur l'interface graphique.
        """
        self.chevalet.delete('lettre')

        for j, jeton in enumerate(self.joueur_actif.chevalet):
            if jeton is not None:
                selection = j == self.position_selection_chevalet
                dessiner_jeton(self.chevalet, jeton, 0, j, self.nb_pixels_par_case, selection)

    def tirer_jetons(self, n):
        """
        Simule le tirage de n jetons du sac à jetons et renvoie ceux-ci. Il s'agit de prendre au hasard des jetons dans
        self.jetons_libres et de les retourner.

        Args:
            n (int): Le nombre de jetons à tirer.

        Returns:
            list: La liste des jetons tirés (instances de la classe Jeton).

        Raises:
            AssertionError: Si n n'est pas compris dans l'intervalle [0, nombre total de jetons libres].
        """
        if not 0 <= n <= len(self.jetons_libres):
            raise FinPartie
        shuffle(self.jetons_libres)
        res = self.jetons_libres[:n]
        self.jetons_libres = self.jetons_libres[n:]
        return res

    def jouer_un_tour(self):
        """
        Vérifie d'abord si les positions des jetons déposés sur le plateau par le joueur actif sont valides.
        Si c'est le cas, le tour est joué.

        NOTE: Vous devez compléter cette méthode afin de passer au joueur suivant!
        """

        try:
            points_depart = self.joueur_actif.points
            liste_jetons, liste_positions = self.plateau.retirer_jetons_en_jeu()
            if len(liste_positions) == 0:
                raise AucunJeton
            self.plateau.valider_positions_avant_ajout(liste_positions)

            mots, score = self.plateau.placer_mots(liste_jetons, liste_positions)

            if any([not self.mot_permis(m) for m in mots]):
                messagebox.showerror('Oups!', "Au moins l'un des mots formés est absent du dictionnaire.")
                for pos in liste_positions:
                    self.plateau.retirer_jeton(pos)
            else:
                messagebox.showinfo('Bravo!', f'Mots formés: {mots}\nScore obtenu: {score}')
                self.joueur_actif.ajouter_points(score)
                liste_jetons = []

            for jeton in liste_jetons:
                self.joueur_actif.ajouter_jeton(jeton)

            self.reinitialiser_tour()
            if points_depart != self.joueur_actif.points:
                self.joueur_suivant()

        except PositionInvalideException:
            for jeton in liste_jetons:
                self.joueur_actif.ajouter_jeton(jeton)
            messagebox.showerror('Oups!', "La position des lettres n'est pas valide.")
            self.reinitialiser_tour()
        except MotNonPermisException:
            for jeton in liste_jetons:
                self.joueur_actif.ajouter_jeton(jeton)
            messagebox.showerror('Oups!', "Au moins l'un des mots formés est absent du dictionnaire.")
            self.reinitialiser_tour()
        except CaseOccupeeException:
            for jeton in liste_jetons:
                self.joueur_actif.ajouter_jeton(jeton)
            messagebox.showerror('Oups!', "On ne peut placer un jeton sur cette case.")
            self.reinitialiser_tour()
        except AucunJeton:
            messagebox.showerror('Oups!', "Aucun jeton n'est pacé sur le plateau.")
            self.reinitialiser_tour()

    def sauvegarder_partie(self, nom_fichier):
        """
        Permet de sauvegarder l'objet courant dans le fichier portant le nom spécifié.
        La sauvegarde se fera grâce à la fonction dump du module pickle.

        Args:
            nom_fichier (str): Nom du fichier qui contient un objet scrabble.

        Returns:
            bool: True si la sauvegarde s'est bien déroulée,
                  False si une erreur est survenue durant la sauvegarde.
        """
        try:
            with open(nom_fichier, 'wb') as f:
                pickle.dump(self, f)
        except:
            return False

        return True


def charger_partie(nom_fichier):
    """
    Fonction permettant de créer un objet scrabble en lisant le fichier dans lequel l'objet avait été sauvegardé
    précédemment.

    Args:
        nom_fichier (str): Nom du fichier qui contient un objet scrabble.

    Returns
        Scrabble: L'objet chargé en mémoire.
    """
    with open(nom_fichier, 'rb') as f:
        return pickle.load(f)
