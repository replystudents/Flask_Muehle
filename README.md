# Mühle Brettspiel

- implementiert in Flask


# requirements
```bash
pip install flask-socketio
pip install eventlet
```


# TODO list
- Spiel nach neu laden korrekt anzeigen (gideon)
- Spielseite schöner machen (gideon)
  - Aufgeben
  - unentschieden  
- Spiel starten -> popup schließen (gideon)
- AI Funktion einbringen (lorenz)
- Spielhistorie anzeigen lassen (lorenz) und dann auch alte Spiele laden (gideon)
- Startseite zusammenbauen (lorenz)
- Unendschieden Regeln einbauen (lorenz)
- Regel Page

-Kein Popup bei Bot Game

evtl. 
- Leaderboard anzeigen lassen
- contact und impressum
- Anmelden und registrieren


Am ende: 
- code refactoring (zusammen)

# BUG
- bei neuer DB Absturz wenn man ein AI Spiel starten will
- kein Unentschieden nach 20 Zügen, der Wert wird nicht inkrementiert