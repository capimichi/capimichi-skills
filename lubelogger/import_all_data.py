#!/usr/bin/env python3
"""
Script di importazione iniziale completo dei dati delle auto in LubeLogger.
Importa:
1. Extra Fields tecnici (VIN, Codice Motore, Potenza, Gomme, Intestatario, Omologazione)
2. Letture Odometro iniziali
3. Storico Interventi e Manutenzioni (Service Records)
4. Tasse e Assicurazioni (Tax Records)
5. Promemoria e Scadenze future (Reminders)
6. Note tecniche e diari di bordo (Notes)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from client import LubeLoggerClient


def main():
    client = LubeLoggerClient()
    print("🚀 Inizio sincronizzazione e importazione dati su LubeLogger...")

    # =========================================================================
    # 1. EXTRA FIELDS TECNICI DEI VEICOLI
    # =========================================================================
    print("\n📋 1. Aggiornamento Extra Fields veicoli...")

    # Fiat 500 (ID: 1)
    client.update_vehicle(
        vehicle_id=1,
        year="2017",
        make="Fiat",
        model="500",
        license_plate="M9705",
        fuel_type="Diesel",
        extra_fields=[
            {"Name": "VIN", "Value": "ZFA3120000J791260"},
            {"Name": "Codice Motore", "Value": "312B1000 (1.3 Multijet)"},
            {"Name": "Cilindrata & Potenza", "Value": "1248 cm³ / 70 kW (95 CV)"},
            {"Name": "Pneumatici a libretto", "Value": "185/55 R15 H"},
            {"Name": "Classe Ambientale", "Value": "Euro 6B (Reg. CE 136/2014)"},
            {"Name": "Intestatario", "Value": "Alessandro Capicchioni"},
        ],
    )
    print("   ✅ Fiat 500 (ID 1) aggiornata con Extra Fields.")

    # Volkswagen T-Roc (ID: 2)
    client.update_vehicle(
        vehicle_id=2,
        year="2023",
        make="Volkswagen",
        model="T-Roc",
        license_plate="S2001",
        fuel_type="Gasoline",
        extra_fields=[
            {"Name": "VIN", "Value": "WVGZZZA1ZRV004766"},
            {"Name": "Codice Motore", "Value": "DLA (1.0 TSI EA211)"},
            {"Name": "Cilindrata & Potenza", "Value": "999 cm³ / 81 kW (110 CV)"},
            {"Name": "Pneumatici a libretto", "Value": "215/60 R16 95V"},
            {"Name": "Classe Ambientale", "Value": "Euro 6 (Reg. CE 715/2007*2018/1832AP)"},
            {"Name": "Intestatario", "Value": "Michele Capicchioni"},
        ],
    )
    print("   ✅ Volkswagen T-Roc (ID 2) aggiornata con Extra Fields.")

    # =========================================================================
    # 2. LETTURE ODOMETRO
    # =========================================================================
    print("\n📍 2. Registrazione chilometraggi attuali...")
    client.add_odometer_record(
        vehicle_id=1,
        date="2026-11-13",
        odometer=91350,
        notes="Rilevamento chilometraggio Fiat 500 (pre-tagliando)",
    )
    print("   ✅ Fiat 500: 91.350 km registrati.")

    client.add_odometer_record(
        vehicle_id=2,
        date="2026-11-12",
        odometer=36688,
        notes="Rilevamento chilometraggio T-Roc",
    )
    print("   ✅ Volkswagen T-Roc: 36.688 km registrati.")

    # =========================================================================
    # 3. STORICO INTERVENTI & MANUTENZIONI (Service Records)
    # =========================================================================
    print("\n🔧 3. Importazione storico tagliandi e manutenzioni...")

    # Fiat 500
    interventions_500 = [
        {"date": "2023-07-01", "mileage": 60000, "desc": "Cambio gomme davanti da Brescia Gomme, sono estive", "cost": 120.0, "tags": ["gomme", "estive"]},
        {"date": "2024-03-03", "mileage": 70000, "desc": "Tagliando da Santini", "cost": 150.0, "tags": ["tagliando"]},
        {"date": "2024-09-16", "mileage": 75000, "desc": "Cambio batteria da Santini", "cost": 150.0, "tags": ["batteria"]},
        {"date": "2025-03-29", "mileage": 82000, "desc": "Cambio due ammortizzatori davanti e kit tamponi fine corsa", "cost": 297.0, "tags": ["ammortizzatori", "sospensioni"]},
        {"date": "2025-03-29", "mileage": 82000, "desc": "Cambio gomme dietro da Santini, Estive", "cost": 160.0, "tags": ["gomme", "estive"]},
        {"date": "2025-04-08", "mileage": 82500, "desc": "Cambio gomme Santini, davanti, estive (Nexen)", "cost": 160.0, "tags": ["gomme", "estive"]},
        {"date": "2025-04-09", "mileage": 82600, "desc": "Revisione periodica biennale obbligatoria RSM", "cost": 50.0, "tags": ["revisione"]},
        {"date": "2025-07-25", "mileage": 86000, "desc": "Tagliando da Santini", "cost": 165.0, "tags": ["tagliando"]},
        {"date": "2025-10-02", "mileage": 88000, "desc": "Cambio pasticche freni davanti", "cost": 35.0, "tags": ["freni", "pastiglie"]},
        {"date": "2026-11-08", "mileage": 91300, "desc": "Batteria VARTA Silver Dynamic EFB N60 60Ah 640A (Brico Io Titano) - Garanzia 2 anni fino all'08/11/2028", "cost": 99.0, "tags": ["batteria", "garanzia"]},
    ]
    if not client.get_service_records(1):
        for it in interventions_500:
            client.add_service_record(
                vehicle_id=1,
                date=it["date"],
                mileage=it["mileage"],
                description=it["desc"],
                cost=it["cost"],
                tags=it["tags"],
            )
        print(f"   ✅ Fiat 500: {len(interventions_500)} interventi registrati.")
    else:
        print("   ℹ️ Fiat 500: interventi già presenti.")

    # Volkswagen T-Roc
    interventions_troc = [
        {"date": "2025-10-18", "mileage": 25000, "desc": "Tagliando da Grip Garage + Inversione gomme", "cost": 297.0, "tags": ["tagliando", "gomme"]},
    ]
    if not client.get_service_records(2):
        for it in interventions_troc:
            client.add_service_record(
                vehicle_id=2,
                date=it["date"],
                mileage=it["mileage"],
                description=it["desc"],
                cost=it["cost"],
                tags=it["tags"],
            )
        print(f"   ✅ Volkswagen T-Roc: {len(interventions_troc)} interventi registrati.")
    else:
        print("   ℹ️ Volkswagen T-Roc: interventi già presenti.")

    # =========================================================================
    # 4. TASSE & ASSICURAZIONI (Tax Records)
    # =========================================================================
    print("\n🏛️ 4. Importazione tasse, bollo e assicurazioni...")

    taxes_500 = [
        {"date": "2024-11-30", "desc": "Pagamento bollo annuale Fiat 500 (RSM)", "cost": 80.0, "notes": "Validità 30/11/2024 - 30/11/2025", "tags": ["bollo", "rsm"]},
        {"date": "2026-11-08", "desc": "Pagamento bollo annuale Fiat 500 (RSM)", "cost": 80.0, "notes": "Validità 30/11/2026 - 30/11/2027", "tags": ["bollo", "rsm"]},
    ]
    for tx in taxes_500:
        client.add_tax_record(
            vehicle_id=1,
            date=tx["date"],
            description=tx["desc"],
            cost=tx["cost"],
            notes=tx["notes"],
            tags=tx["tags"],
        )
    print(f"   ✅ Fiat 500: {len(taxes_500)} pagamenti tasse/bollo registrati.")

    taxes_troc = [
        {"date": "2025-10-31", "desc": "Pagamento bollo annuale T-Roc (RSM)", "cost": 37.0, "notes": "Validità fino 31/10/2026", "tags": ["bollo", "rsm"]},
        {"date": "2025-11-29", "desc": "Pagamento assicurazione annuale T-Roc Allianz", "cost": 659.0, "notes": "Polizza Allianz annualità 2025-2026", "tags": ["assicurazione", "allianz"]},
        {"date": "2026-10-31", "desc": "Pagamento bollo annuale T-Roc (RSM)", "cost": 37.0, "notes": "Validità fino 31/10/2027", "tags": ["bollo", "rsm"]},
        {"date": "2026-11-09", "desc": "Pagamento assicurazione annuale T-Roc Allianz", "cost": 640.0, "notes": "Polizza Allianz 00566986024 (validità 29/11/2026 - 29/11/2027)", "tags": ["assicurazione", "allianz"]},
    ]
    for tx in taxes_troc:
        client.add_tax_record(
            vehicle_id=2,
            date=tx["date"],
            description=tx["desc"],
            cost=tx["cost"],
            notes=tx["notes"],
            tags=tx["tags"],
        )
    print(f"   ✅ Volkswagen T-Roc: {len(taxes_troc)} pagamenti bollo/assicurazione registrati.")

    # =========================================================================
    # 5. PROMEMORIA & SCADENZE (Reminders)
    # =========================================================================
    print("\n⏰ 5. Creazione scadenze e promemoria...")

    reminders_500 = [
        {"desc": "Tagliando annuale da effettuare presso Santini (olio 5W30 C2, filtro olio e aria)", "metric": "Date", "due_date": "2026-11-20", "urgency": "Urgent", "notes": "Prezzo stimato: € 160"},
        {"desc": "Inversione gomme estive Nexen (avanti/dietro)", "metric": "Date", "due_date": "2026-11-30", "urgency": "NotUrgent", "notes": "Pareggiare consumo pneumatici estivi"},
        {"desc": "Controllo usura e tensione cinghia servizi ausiliaria", "metric": "Date", "due_date": "2026-11-30", "urgency": "NotUrgent", "notes": "Verifica in officina col tagliando"},
        {"desc": "Revisione periodica biennale obbligatoria RSM", "metric": "Date", "due_date": "2027-04-17", "urgency": "NotUrgent", "notes": "Presso Centro Revisioni RSM"},
        {"desc": "Rinnovo tassa di circolazione (Bollo) RSM", "metric": "Date", "due_date": "2027-11-30", "urgency": "NotUrgent", "notes": "Coperto fino al 30/11/2027 (€ 80)"},
        {"desc": "Scadenza garanzia legale 2 anni batteria Varta N60", "metric": "Date", "due_date": "2028-11-08", "urgency": "NotUrgent", "notes": "Scontrino Brico Io Titano conservato su Paperless"},
    ]
    for rem in reminders_500:
        client.add_reminder(
            vehicle_id=1,
            description=rem["desc"],
            metric=rem["metric"],
            due_date=rem.get("due_date"),
            due_odometer=rem.get("due_odometer"),
            urgency=rem["urgency"],
            notes=rem["notes"],
        )
    print(f"   ✅ Fiat 500: {len(reminders_500)} promemoria impostati.")

    reminders_troc = [
        {"desc": "Controllo battistrada Goodyear ed eventuale sostituzione", "metric": "Both", "due_date": "2027-05-15", "due_odometer": 48000, "urgency": "NotUrgent", "notes": "Prevista a circa 45.000-50.000 km (€ 500)"},
        {"desc": "Secondo tagliando LongLife (olio 0W20 spec VW 508.00, filtri)", "metric": "Both", "due_date": "2027-10-15", "due_odometer": 55000, "urgency": "NotUrgent", "notes": "A 55.000 km o 2 anni dall'ultimo tagliando"},
        {"desc": "Controllo pastiglie freni anteriori", "metric": "Date", "due_date": "2027-10-15", "urgency": "NotUrgent", "notes": "In occasione del tagliando dei 55.000 km"},
        {"desc": "Rinnovo tassa di circolazione (Bollo) RSM", "metric": "Date", "due_date": "2027-10-31", "urgency": "NotUrgent", "notes": "Coperto fino al 31/10/2027 (€ 37)"},
        {"desc": "Rinnovo assicurazione annuale T-Roc Allianz", "metric": "Date", "due_date": "2027-11-29", "urgency": "NotUrgent", "notes": "Polizza Allianz 00566986024 (€ 640)"},
        {"desc": "Revisione periodica obbligatoria RSM (Prima revisione a 4 anni)", "metric": "Date", "due_date": "2027-11-27", "urgency": "NotUrgent", "notes": "Scadenza prima revisione riportata su libretto"},
    ]
    for rem in reminders_troc:
        client.add_reminder(
            vehicle_id=2,
            description=rem["desc"],
            metric=rem["metric"],
            due_date=rem.get("due_date"),
            due_odometer=rem.get("due_odometer"),
            urgency=rem["urgency"],
            notes=rem["notes"],
        )
    print(f"   ✅ Volkswagen T-Roc: {len(reminders_troc)} promemoria impostati.")

    # =========================================================================
    # 6. NOTE TECNICHE & SPECIFICHE (Notes)
    # =========================================================================
    print("\n📝 6. Creazione note tecniche...")

    note_500 = """### Scheda Tecnica e Manutenzione Fiat 500
- **Motore**: 1.3 Multijet Diesel (312B1000 - 1248 cm³, 70 kW / 95 CV, Euro 6B)
- **Olio motore consigliato**: 5W-30 specifica ACEA C2 (capacità circa 3.2 litri)
- **Distribuzione**: Catena metallica (nessuna sostituzione programmata; verificare rumorosità oltre 200.000 km)
- **Pneumatici**: 185/55 R15 H
  - Gomme montate: Nexen estive
  - Inversione programmata per pareggiare il consumo
- **Batteria**: VARTA Silver Dynamic EFB N60 60Ah 640A (installata 08/11/2026, scontrino su Paperless #1026)
- **Revisione**: Biennale (scadenza 17/04/2027)
- **Bollo RSM**: Scadenza 30/11/2027 (€ 80,00)"""

    client.add_note(
        vehicle_id=1,
        description="Specifiche Tecniche & Manutenzione",
        note_text=note_500,
        is_pinned=True,
    )
    print("   ✅ Fiat 500: nota tecnica salvata e pinnata.")

    note_troc = """### Scheda Tecnica e Manutenzione Volkswagen T-Roc
- **Motore**: 1.0 TSI Benzina (Codice DLA - famiglia EA211, 999 cm³, 81 kW / 110 CV, Euro 6)
- **Olio motore consigliato**: 0W-20 specifica VW 508.00 / 509.00 LongLife IV
- **Distribuzione**: Cinghia dentata LongLife motore EA211 (ispezione prevista a 210.000 km / 8°-10° anno)
- **Pneumatici**: 215/60 R16 95V
  - Gomme montate: Goodyear
  - Invertite a ottobre 2025; controllo battistrada previsto a 45.000-50.000 km
- **Assicurazione**: Allianz polizza 00566986024 (coperto fino al 29/11/2027)
- **Revisione**: Prima revisione a 4 anni (scadenza 27/11/2027)
- **Bollo RSM**: Scadenza 31/10/2027 (€ 37,00)"""

    client.add_note(
        vehicle_id=2,
        description="Specifiche Tecniche & Manutenzione",
        note_text=note_troc,
        is_pinned=True,
    )
    print("   ✅ Volkswagen T-Roc: nota tecnica salvata e pinnata.")

    print("\n🎉 Importazione completata con successo su LubeLogger!")


if __name__ == "__main__":
    main()
