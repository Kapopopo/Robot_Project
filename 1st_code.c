#include <Servo.h>
#include <DFRobotDFPlayerMini.h>
#include <SoftwareSerial.h>

Servo servoTete;
int pinServo = 9;

int pinLedRouge = 6;
int pinMouvement = 7;
bool mouvementDetecte = false;

SoftwareSerial mySerial(10, 11);
DFRobotDFPlayerMini myDFPlayer;

unsigned long derniereMusique = 0;
bool musiqueJoue = false;

void setup()
{
  // On initialise le setup
  Serial.begin(9600);
  mySerial.begin(9600);

  servoTete.attach(pinServo);
  servoTete.write(90);

  pinMode(pinLedRouge, OUTPUT);

  pinMode(pinMouvement, INPUT);

  if (!myDFPlayer.begin(mySerial))
  {
    Serial.println("Pas initialisé");
    while (true)
      ;
  }

  myDFPlayer.volume(20);
}

void loop()
{
  // La premiere etape c'est de jouer la musique
  if (!musiqueJoue)
  {
    myDFPlayer.play(1);
    musiqueJoue = true;
  }

  // Lorsque la musique s'arrete la tete elle tourne de maniere aleatoire
  if (musiqueJoue && !myDFPlayer.isPlaying())
  {
    delay(1000);
    int angle = random(60, 120);
    servoTete.write(angle);
    musiqueJoue = false;

    // on active les lumieres rouge
    digitalWrite(pinLedRouge, HIGH);
  }

  // des qu'il detecte un joueur le joueur est eliminé
  mouvementDetecte = digitalRead(pinMouvement);
  if (mouvementDetecte)
  {
    myDFPlayer.play(2);
    Serial.println("Joueur éliminé !");
    delay(2000);
  }

  // et la j'ai mis en 5 tours juste pour test et si le joueur 3 est a fait plus de 5 tours il a gagné !
  static int tours = 0;
  if (tours > 5)
  {
    myDFPlayer.play(3);
    Serial.println("Gagné t'es chaud + !");
    while (true)
      ;
  }
}
