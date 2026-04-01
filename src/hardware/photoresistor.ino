/*
 */
int etatBouton = HIGH; // Initialise avec l'état "non appuyé"


void setup() {
  Serial.begin(9600);   // Initialisation de la communication série
  pinMode(A3, INPUT);
  //pinMode(31, INPUT);   // Broche en entrée simple

  //pinMode(7, OUTPUT);
  //digitalWrite(7, HIGH);
}

void loop() {

  int value = analogRead(A3);  // Lecture de la tension sur A3

  Serial.println(value);
  
  int lecture = digitalRead(31);  // Lire l'état du bouton / renvoie entre 1 et 0

  // Détection de front montant (appui unique)
  //if (lecture == HIGH && etatBouton == LOW) {
  //  Serial.println("GO");  // Envoie "GO" sur le port série
  //  etatBouton = HIGH;     // mémorise l'état pour éviter les répétitions
  //} 
  //else if (lecture == LOW && etatBouton == HIGH) { // Relâchement
  //  Serial.println("GO");  // Envoie "GO" sur le port série
  //  etatBouton = LOW;
  //}

  delay(10);  // Pause pour la lisibilité
}
