# Energy2.0

## Installation und Quick-Start

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

In _base_ werden alle Modelle und grundlegenden administrativen Serializer und Views definiert.
In dieser Ebene wird der [UserSerializer](base/serializers.py) definiert und die [Views](base/views.py),
also die API-Endpunkte definiert.

##### User

Viewset, für Dokumentation siehe [Django REST GUI](#api---endpunkte)

##### CustomLogin

Für API-DOkumentation siehe [hier]()  
Diese Klasse erweitert die von Standard Klasse für Token Authentifizierung von Django, damit zusätzlich zum Token,
die Parameter is_admin und customer_id für den einloggenden User mitgesendet werden.

##### Logout

Für API-DOkumentation siehe [hier]()

Hier wird ganz grundlegend eine Logout Funktion für Token-Authentifizierung implementiert, indem der Token des
ausloggenden
Benutzers gelöscht wird und damit ein neuer Token generiert werden muss.

### base.sensors

In dieser Ebenen wird die Entität Sensor definiert und alle Entitäten, die direkt einem Sensor zugeordnet sind.

Hier sollte erwähnt werden, dass die Serializer für Producer und Consumer so definiert sind, dass die Sensoren zusammen
mit einem Producer/Consumer erstellt werden und nicht seperat. Genauso wird ein User zusammen mit einem Konsumenten
erstellt.

##### Sensor

Sensoren, sind die Entitäten, welche die konkreten Lorawan Sensoren abbilden, welche in unserem Projekt zum Einsatz
kommen.
Sensoren speichern die Gerätenummer und sind einem von drei Typen zugeordnet, damit eingehende Daten (siehe [input]())
einem
Sensor zugeordnet werden kann und ob dieser Sensor Produktion(PM), Netzeinspeisung(GM) oder Verbrauch(CM) misst.

###### Attribute

| Attribute   | Type                     | Description                                                                    |
|:------------|:-------------------------|:-------------------------------------------------------------------------------|
| `device_id` | `string`                 | Eindeutige Nummer (z.B EAN) aus datahub                                        |
| `type`      | `ENUM["PM", "GM", "CM"]` | bestimmt ob es sich um einen Production-, Grid- oder Consumptionsensor handelt |

##### Producer

Ein Produzent (bspw. Solaranalge) bildet die oberste Einheit in unserem Projekt. Ein Produzent hat immer zwei Sensorenn,
ein für die Produktion und einen für die Netzeinspeisung. Des Weiteren werden beschreibende Attribute gespeichert, wie
ein
Anzeigename oder eine Addresse

###### Attribute

| Attribute                 | Type       | Description                                                                                                                                                                                                                                              |
|:--------------------------|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                    | `string`   |                                                                                                                                                                                                                                                          |
| `street`                  | `string`   |                                                                                                                                                                                                                                                          |
| `city`                    | `string`   |                                                                                                                                                                                                                                                          |
| `zip_code`                | `string`   |                                                                                                                                                                                                                                                          |
| `peak_power`              | `integer`  |                                                                                                                                                                                                                                                          |
| `production_sensor`       | `Sensor`   |                                                                                                                                                                                                                                                          |
| `grid_sensor`             | `Sensor`   |                                                                                                                                                                                                                                                          |
| `last_grid_reading`       | `datetime` | wird automatisch erstellt, wenn ein [Reading]() erstellt wird (siehe [update_last_reading](base/data/models.py)), und wird im [/input verarbeitung](input/input_handlers.py) genutzt,  um sich die Datenbankabfrage nach den jüngsten Readings zu sparen |
| `last_production_reading` | `Sensor`   |                                                                                                                                                                                                                                                          |

##### Consumer

Ein Konsument(bspw. eine Wohneinheit) konsumiert Energie, welche von einem Sensor gemessen wird und ist genau einem
Produzenten zugeordnet. Darüber hinaus werden Attribute zur Kontaktaufnahme gespeichert.
Ein Konsument ist genau einem Benutzer zugeordnet, damit eine Authentifizierung

###### Attribute

| Attribute      | Type              | Description                                                                                                                                                                                                                                              |
|:---------------|:------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`         | `string`          |                                                                                                                                                                                                                                                          |
| `email`        | `string`          |                                                                                                                                                                                                                                                          |
| `phone`        | `string`          |                                                                                                                                                                                                                                                          |
| `user`         | `User`            |                                                                                                                                                                                                                                                          |
| `sensor`       | `Sensor`          |                                                                                                                                                                                                                                                          |
| `producer`     | `Producer.url`    |                                                                                                                                                                                                                                                          |
| `rates`        | `Array<Rate.url>` |                                                                                                                                                                                                                                                          |
| `last_reading` | `datetime`        | wird automatisch erstellt, wenn ein [Reading]() erstellt wird (siehe [update_last_reading](base/data/models.py)), und wird im [/input verarbeitung](input/input_handlers.py) genutzt,  um sich die Datenbankabfrage nach den jüngsten Readings zu sparen |

#### base.data

## API - Endpunkte

Die Endpunkte der einzelnen Entitäten, welche oben beschrieben sind, werden hier nicht dokumentiert. Django REST
erstellt
automatisch eine Grafisches Interface zur REST-API und ist damit selbst beschreibend. Hierfür muss einfach der Server
gestartet werden, wie [oben](#installation-und-quick-start) beschrieben.

Folgende Endpunkte sind nicht im Django REST GUI enthalten und werden im folgendem dokumentiert.

- [/login]()
    - [Authentisierung]()
- [/logout]()
- [/input]()
- [/output]()

### /login/

```http
POST /login/
```

#### Request

| Form Data  | Type     | Description                        |
|:-----------|:---------|:-----------------------------------|
| `username` | `string` | **Required**. Your Gophish API key |
| `password` | `string` | **Required**. Your Gophish API key |

#### Response

```javascript
{
    status: 200,
        data
:
    {
        token: string,
            is_admin
    :
        bool,
            consumer_id
    :
        integer | None,
    }
}
```

### /logout/

```http
POST /logout/
```

#### Request

Authentifizierung erforderlich

#### Response

```json
{
  status: 200,
  data: {
    message: "{username} logged out successfully"
  }
}
```

### /input/

```http
POST /input/
```

#### Request

Das folgende Format ist in datahub definiert. Die verwendeten Parameter sind im folgendem aufgezählt.

```json
  {
  'device_id': integer,
  'source_time': datetime,
  'parsed': {
    'Bezug_Gesamt_kWh': float,
    'Lieferung_Gesamt_kWh': float,
    'Leistung_Summe_W': float
  }
}
```

#### Response

```json
{
  status: 200
}
```

### /output/

```http
GET /output/
```

#### Request

Das folgende Format ist in datahub definiert. Die verwendeten Parameter sind im folgendem aufgezählt.

| Query Parameter | Type       | Description |
|:----------------|:-----------|:------------|
| `producer_id`   | `integer`  |             |
| `consumer_id`   | `integer`  |             |
| `start_date`    | `datetime` |             |
| `end_date`      | `datetime` |             |

#### Response

With producer_id and consumer_id not set:

```json
{
  "producers_total_production": Decimal,
  "producers_total_used": Decimal,
  "producers_total_revenue": Decimal,
  "producers_total_saved": Decimal,
  "producers_total_consumption": Decimal,
  "producers": {
    "{producer_name}": {
      "total_production": Decimal,
      "total_used": Decimal,
      "consumers_total_revenue": Decimal,
      "consumers_total_saved": Decimal,
      "total_consumption": Decimal,
      "productions": Array<Production>,
      "consumers": {
        "{consumer_name}": {
          "total_used": Decimal,
          "total_price": Decimal,
          "total_reduced_price": Decimal,
          "total_grid_price": Decimal,
          "total_saved": Decimal,
          "total_consumption": Decimal,
          "total_self_consumption": Decimal,
          "total_grid_consumption": Decimal,
          "productions": Array<Production>,
          "consumptions": Array<Consumption>
        }
      }
    }
  }
}
}
```

With producer_id set:

```json
{
  "total_production": Decimal,
  "total_used": Decimal,
  "consumers_total_revenue": Decimal,
  "consumers_total_saved": Decimal,
  "consumers_total_consumption": Decimal,
  "productions": Array<Production>,
  "consumers": {
    "{consumer_name}": {
      "total_used": Decimal,
      "total_price": Decimal,
      "total_reduced_price": Decimal,
      "total_grid_price": Decimal,
      "total_saved": Decimal,
      "total_consumption": Decimal,
      "total_self_consumption": Decimal,
      "total_grid_consumption": Decimal,
      "productions": Array<Production>,
      "consumptions": Array<Consumption>
    }
  },
  "consumptions": Array<Consumption(aggregated)>
}
```

With consumer_id set:

```json
{
  "total_used": Decimal,
  "total_price": Decimal,
  "total_reduced_price": Decimal,
  "total_grid_price": Decimal,
  "total_saved": Decimal,
  "total_consumption": Decimal,
  "total_self_consumption": Decimal,
  "total_grid_consumption": Decimal,
  "productions": Array<Production>,
  "consumptions": Array<Consumption> 
}
```

