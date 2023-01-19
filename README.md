# Energy2.0

## Installation

1. Installieren von `python` und `pip`
2. Empfohlen: Virtuelle Enviroment erstellen
3. Projekt auf Computer clonen: `git clone git@github.com:s1n7/Energy2.0.git`
4. Alle packages installieren: `pip install -r requirements.txt`
5. Datenbank erstellen mit `python manage.py makemigrations` und dann `python manage.py migrate`
6. Server starten: `python manage.py runserver`

## Struktur

Das Django Projekt ist in unterschiedliche Applikationen aufgeteilt. Diese sind zwar stark verkoppelt, aber haben 
unterschiedliche Aufgaben.

- [base](#base)
  - [base.sensors](#basesensors)
  - [base.data]()
  - [base.contracts]()
- [input]()
- [output]()

### base
In _base_ werden alle Modelle und grundlegenden administrativen Serializer und Views definiert. In dieser Ebene wird nur das User Model
verwaltet.

##### User
In der Zukunft könnten hier Sachen implementiert werden, wie:  
- Anmelden auch mit Email
- Password vergessen/ändern

#### base.sensors

##### Sensor

##### Producer(Solaranlage)
- name
- street
- city
- zip_code
- peak_power
- sensor

##### Consumer(Wohneinheit)
