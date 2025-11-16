import pygame
from pygame.locals import *
import random

class KST:
    __slots__ = ()  # empêche la ré-écriture accidentelle des constantes  

    # codes numériques pour les 4 directions, utilisés aussi par le module
    # d'inteface graphique
    HAUT = 0
    DROITE = 1
    BAS = 2
    GAUCHE = 3
    ESPACE = 4

class Interface:
    def __init__(self, dim_x, dim_y, titre):
        self.clock = pygame.time.Clock()
        self.cursor = (0, 0)
        self.taille_fonte_y = 40
        pygame.init()
        if not pygame.font.get_init():
            print("Désolé, les fontes de caractères sont absentes, je ne peux démarrer")
            quit()
        self.font = pygame.font.SysFont("Courrier, Monospace",
                                    self.taille_fonte_y)
        self.taille_fonte_x = self.font.size('M')[0]
        self.ecran = pygame.display.set_mode((dim_x * self.taille_fonte_x ,
                                          dim_y * self.taille_fonte_y))
        pygame.display.set_caption(titre)
        # dictionnaire de couleurs: comme une liste mais indexé par des chaînes 
        self.COULEUR = {  
            'vert'   : (11, 240, 11),    # "vert" défini par intensités (rouge, vert, bleu)
            'rouge'   : (213, 11, 11),
            'orange'   : (213, 180, 11),
            'jaune'   : (213, 213, 11),
            'bleu'    : (40, 40, 240),
            'blanc'   : (255, 255, 255),
            'gris'   : (210, 210, 210),
            'noir'    : (0, 0, 0)
        }
        # liste des noms de couleurs
        self.NOM_COULEUR = list(self.COULEUR.keys())
        # dictionnaire des indices des noms de couleurs
        self.IND_COULEUR = {}
        for indice,nom in enumerate(self.NOM_COULEUR):
            self.IND_COULEUR[nom] = indice

    # place le "curseur" : la position de la prochaine commande "write"
    def curseur(self, px, py):
        self.cursor = (px, py)
        
    # écrire une chaine à la position du curseur
    def write(self, texte, fgcolor=(255,255,255), bgcolor=(0,0,0)):
        texte = self.font.render(texte,
                            True,
                            pygame.Color(fgcolor),
                            pygame.Color(bgcolor))
        self.ecran.blit(texte,
                        (self.cursor[0]*self.taille_fonte_x,
                         self.cursor[1]*self.taille_fonte_y))

    # faire une temporisation
    def pause(self, tempo): 
        self.clock.tick(tempo)

    # affiche les modifications effectuées depuis le dernier appel
    def mise_a_jour(self):
        pygame.display.flip()

    # retourne code d'une touche de déplacement du clavier (touches "flêches")
    # ou None sinon
    # teste d'abord si nouvelle pression sur une touche
    def lire_touche(self):
        key = None
        for event in pygame.event.get():
            # teste d'abord si fermeture fenêtre
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    key = KST.HAUT
                elif event.key == pygame.K_DOWN:
                    key = KST.BAS
                elif event.key == pygame.K_LEFT:
                    key = KST.GAUCHE
                elif event.key == pygame.K_RIGHT:
                    key = KST.DROITE
                elif event.key == pygame.K_SPACE:
                    key = KST.ESPACE
        # l'appel à pygame.event.get() a mis à jour l'état des touches
        if key != None:
            return key
        # teste maintenant si pression continue (et pas nouvelle) sur touche
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            return KST.DROITE
        if keys[pygame.K_LEFT]:
            return KST.GAUCHE
        if keys[pygame.K_UP]:
            return KST.HAUT
        if keys[pygame.K_DOWN]:
            return KST.BAS
        if keys[pygame.K_SPACE]:
            return KST.ESPACE

        # si ici, alors pas de touche qui nous intéresse
        return None

    # ferme la librairie (au cas où la fenêtre graphique reste "bloquée"
    def fermer(self):
        pygame.quit()

if __name__ == "__main__":               
    # création d'un écran de 10x10 caractères
    ecran = Interface(10, 10, "Bureau d'étude")

    # illustrons la zone de l'écran
    for y in range(10):
        for x in range(10):
            ecran.cursor = (x, y)
            ecran.write("X")

    # testons la saisie de touches
    compteur_temps = 0
    temporisation = 100 # en millièmes de seconde, soit un dixième de seconde ici
    while True: # boucle d'animation, réglée par la pause en dernière instruction

        # affiche en bas un compteur en 1/10 de seconde (approximativement)
        ecran.curseur(2, 9) # placer d'abord le curseur, puis écrire après
        ecran.write(str(compteur_temps) + " ",
                    fgcolor=ecran.COULEUR['rouge'],
                    bgcolor=ecran.COULEUR['vert'])
        compteur_temps = (compteur_temps + 1) % 100

        # saisie une touche lettre et affiche au milieu sur fond de couleur alea
        numero_couleur = random.randint(0, len(ecran.NOM_COULEUR)-1)
        couleur_alea = ecran.COULEUR[ecran.NOM_COULEUR[numero_couleur]]
        # touche curseur pressée ?
        touche = ecran.lire_touche()
        if touche != None: # oui, une touche curseur pressée
            ecran.curseur(5, 5) # positionne au centre
            # affiche le code de touche du module KST en blanc sur fond alea 
            ecran.write(str(touche), fgcolor=ecran.COULEUR['blanc'],
                        bgcolor=couleur_alea)

        # affiche les écritures faites sur l'écran (SINON RIEN n'apparaît...)
        ecran.mise_a_jour()
        # règle la vitesse de l'animation avec une pause
        ecran.pause(temporisation)

    ecran.fermer()
