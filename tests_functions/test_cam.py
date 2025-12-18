import cv2
import time

print("Tentative d'ouverture de la caméra (index 0)...")

# On essaie d'ouvrir la première caméra connectée (index 0)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# On règle une petite résolution pour que ce soit fluide
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# On laisse 2 secondes à la caméra pour "chauffer" et régler sa lumière
time.sleep(2)

# Vérification si l'ouverture a réussi
if not cap.isOpened():
    print("ERREUR : Impossible d'ouvrir la caméra !")
    print("Vérifiez le branchement de la nappe ou le câble USB.")
    print("Si c'est une caméra nappe, avez-vous activé le 'Legacy Mode' dans raspi-config ?")
    exit()

print("Caméra OK ! Une fenêtre vidéo va s'ouvrir.")
print(">>> Appuyez sur la touche 'q' du clavier pour quitter <<<")

while True:
    # 1. On lit une image (frame) de la caméra
    ret, frame = cap.read()

    # 2. Si la lecture a échoué on arrête
    if not ret:
        print("Erreur de lecture de l'image (flux interrompu).")
        break

    # 3. On affiche l'image dans une fenêtre appelée "Test Camera"
    cv2.imshow('Test Camera', frame)

    # 4. On attend 1 milliseconde et on vérifie si la touche 'q' est pressée
    # Le "& 0xFF" est une sécurité pour que ça marche sur tous les claviers
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Arrêt demandé par l'utilisateur.")
        break

# Nettoyage final : on libère la caméra et on ferme la fenêtre
cap.release()
cv2.destroyAllWindows()
print("Test terminé.")