Robot Squid Game – Détection de mouvement
Description du projet

Ce projet consiste à concevoir un robot inspiré de la poupée de Squid Game reproduisant le jeu « 1, 2, 3 Soleil ».
Le robot est capable de :

Tourner la tête grâce à un servomoteur

Jouer de la musique

Surveiller les joueurs à l’aide d’une caméra

Détecter les mouvements des joueurs lorsque la poupée est tournée

Annoncer vocalement quel joueur a bougé

Le projet a été réalisé en trois grandes étapes : simulation, tests matériels, puis intégration finale sur Raspberry Pi 4B.

Principe du jeu

La poupée est tournée dos aux joueurs :

La musique joue

Les joueurs peuvent bouger

La poupée se retourne :

La musique s’arrête

La caméra surveille les joueurs

Si un joueur bouge pendant l'espionnage

Il est détecté

Un message vocal annonce son élimination

Technologies utilisées

Python

Flask (interface web)

OpenCV (vision par ordinateur)

Raspberry Pi Pico (simulation)

Raspberry Pi 4B (version finale)

pigpio (contrôle précis du servomoteur)

ALSA / aplay (lecture audio)

Wokwi (simulation électronique)

Étape 1 – Simulation sur Wokwi
Objectif

Valider la logique du jeu avant d’utiliser le matériel réel.

Environnement

Simulateur : Wokwi

Carte utilisée : Raspberry Pi Pico

Composants simulés

Servomoteur

Capteur PIR (détection de mouvement)

LEDs (yeux de la poupée)

Buzzer (musique / son)

Fonctionnalités implémentées

Rotation de la tête (0° / 180°)


Détection de mouvement via capteur PIR

Signal sonore d’élimination

Animation de la tête (mouvement “non”)

Code de simulation

Le code Python utilisé pour la simulation est inclus dans le projet et fonctionne directement sur Wokwi avec un Raspberry Pi Pico.

Étape 2 – Tests matériels sur Raspberry Pi 4B
Objectif

Tester chaque composant indépendamment sur le matériel réel.

Matériel utilisé :

Raspberry Pi 4B

Micro servomoteur 9g

Caméra USB

Enceintes (haut-parleurs USB / jack)

Tests réalisés

Test du servomoteur (rotation 0° / 180°)

Test de la caméra USB avec OpenCV

Test de la lecture audio avec aplay

Vérification du pilotage GPIO avec pigpio

Chaque composant a été validé séparément avant l’intégration finale.

Étape 3 – Intégration finale (jeu complet)
Objectif

Combiner caméra + servo + audio + logique du jeu dans une seule application.

Interface Web (Flask)

Page /setup

Choix du nombre de joueurs (2 à 4)

Saisie des prénoms

Page /view

Flux vidéo en direct

Boutons START / STOP

Détection en temps réel via la caméra

Détection de mouvement

Image découpée en zones horizontales

Chaque zone correspond à un joueur

Comparaison d’images successives (différence de pixels)

Si mouvement détecté pendant FEU ROUGE → élimination

Annonce vocale

Lecture d’un fichier .wav spécifique pour chaque joueur

Exemple :

joueur1_elimine.wav

joueur2_elimine.wav

Mouvement de la poupée

Servo à 0° → FEU VERT

Servo à 180° → FEU ROUGE

Contrôle précis via pigpio

Code principal

Le code Flask fourni dans le projet est le programme final, intégrant :

Gestion du jeu

Détection des mouvements

Contrôle du servo

Lecture audio

Interface web




Lancer le projet
Prérequis
sudo apt install python3-opencv pigpio
sudo pigpiod

Lancement
python3 main.py


Puis ouvrir dans un navigateur :

http://<IP_RASPBERRY>:5001



Améliorations possibles
Reconnaissance faciale ou tracking par IA
Système de score ou élimination progressive
Mode multijoueurs avancé

FIN!