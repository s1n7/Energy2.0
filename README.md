# Energy2.0

## Struktur

Das Django Projekt ist in unterschiedliche Applikationen aufgeteilt. Diese sind zwar stark verkoppelt, aber haben 
unterschiedliche Aufgaben.

- [base](#base)
  - [base.sensors](#base.sensors)
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