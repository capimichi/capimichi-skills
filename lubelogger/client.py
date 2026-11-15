#!/usr/bin/env python3
"""
LubeLogger API Client
Fornisce l'interfaccia client per interagire con l'API REST di LubeLogger.
Legge le credenziali dalle variabili d'ambiente di sistema conformemente a ADD_SKILL_RULES.md:
- LUBELOGGER_URL o LUBELOGGER_BASE_URL (default: https://lubelogger.michelecapicchioni.com)
- LUBELOGGER_API_KEY o LUBELOGGER_APIKEY
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


class LubeLoggerClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (
            base_url
            or os.environ.get("LUBELOGGER_URL")
            or os.environ.get("LUBELOGGER_BASE_URL")
            or "https://lubelogger.michelecapicchioni.com"
        ).rstrip("/")

        self.api_key = (
            api_key
            or os.environ.get("LUBELOGGER_API_KEY")
            or os.environ.get("LUBELOGGER_APIKEY")
        )

        if not self.api_key:
            raise ValueError(
                "❌ Credenziali LubeLogger non trovate nelle variabili d'ambiente!\n"
                "Assicurati che LUBELOGGER_API_KEY (o LUBELOGGER_APIKEY) sia esportata.\n"
                "Verifica con: 'source ~/.config/zsh/envs/personal.zsh' o controlla l'ambiente della shell."
            )

    def _request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> Any:
        """Esegue una chiamata HTTP REST all'API di LubeLogger."""
        url = f"{self.base_url}{endpoint}"
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}
            if clean_params:
                url = f"{url}?{urlencode(clean_params)}"

        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "LubeLogger-Client/1.0",
        }

        body = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode("utf-8")

        req = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(req, timeout=30) as resp:
                status = resp.status
                content = resp.read().decode("utf-8")
                if not content:
                    return {"success": True, "status": status}
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        except HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            error_msg = f"HTTP {e.code} su {method} {url}: {err_body}"
            raise RuntimeError(error_msg) from e
        except URLError as e:
            raise RuntimeError(f"Errore connessione verso {url}: {e.reason}") from e

    # ==========================================
    # VEICOLI (Vehicles)
    # ==========================================

    def get_vehicles(self) -> List[Dict[str, Any]]:
        """Recupera l'elenco di tutti i veicoli registrati."""
        res = self._request("/api/vehicles", method="GET")
        return res if isinstance(res, list) else []

    def get_vehicle_info(self, vehicle_id: int) -> Dict[str, Any]:
        """Recupera le informazioni dettagliate di un veicolo specifico."""
        return self._request("/api/vehicle/info", method="GET", params={"vehicleId": vehicle_id})

    def add_vehicle(
        self,
        year: Union[int, str],
        make: str,
        model: str,
        license_plate: str,
        fuel_type: str = "Gasoline",
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiunge un nuovo veicolo nel garage."""
        payload = {
            "Year": str(year),
            "Make": make,
            "Model": model,
            "LicensePlate": license_plate,
            "Identifier": "LicensePlate",
            "FuelType": fuel_type,
            "ExtraFields": extra_fields or [],
        }
        return self._request("/api/vehicles/add", method="POST", data=payload)

    def delete_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """Elimina un veicolo tramite ID."""
        return self._request("/api/vehicles/delete", method="DELETE", params={"vehicleId": vehicle_id})

    def update_vehicle(
        self,
        vehicle_id: int,
        year: Union[int, str],
        make: str,
        model: str,
        license_plate: str,
        fuel_type: str = "Gasoline",
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiorna le informazioni e gli ExtraFields di un veicolo."""
        payload = {
            "Id": str(vehicle_id),
            "Year": str(year),
            "Make": make,
            "Model": model,
            "LicensePlate": license_plate,
            "Identifier": "LicensePlate",
            "FuelType": fuel_type,
            "ExtraFields": extra_fields or [],
        }
        return self._request("/api/vehicles/update", method="PUT", data=payload)

    # ==========================================
    # CHILOMETRAGGIO / ODOMETRO (Odometer)
    # ==========================================

    def get_odometer_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera lo storico delle letture contachilometri."""
        res = self._request("/api/vehicle/odometerrecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def get_latest_odometer(self, vehicle_id: int) -> Dict[str, Any]:
        """Recupera l'ultima lettura del contachilometri registrata."""
        return self._request("/api/vehicle/odometerrecords/latest", method="GET", params={"vehicleId": vehicle_id})

    def add_odometer_record(
        self,
        vehicle_id: int,
        date: str,
        odometer: Union[int, float, str],
        notes: str = "",
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Aggiunge una nuova lettura contachilometri.
        Data in formato ISO YYYY-MM-DD o YYYY/MM/DD.
        """
        payload = {
            "Date": date,
            "Odometer": str(odometer),
            "Notes": notes,
            "ExtraFields": extra_fields or [],
        }
        return self._request(
            "/api/vehicle/odometerrecords/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    # ==========================================
    # TAGLIANDI E MANUTENZIONE (Service Records)
    # ==========================================

    def get_service_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera lo storico di tutti i tagliandi e manutenzioni."""
        res = self._request("/api/vehicle/servicerecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def add_service_record(
        self,
        vehicle_id: int,
        date: str,
        mileage: Union[int, float, str],
        description: str,
        cost: Union[int, float, str],
        notes: str = "",
        tags: Optional[List[str]] = None,
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiunge una registrazione di tagliando o intervento di manutenzione."""
        payload = {
            "Date": date,
            "Odometer": str(mileage),
            "Description": description,
            "Cost": str(cost),
            "Notes": notes,
            "Tags": " ".join(tags) if tags else "",
            "ExtraFields": extra_fields or [],
        }
        return self._request(
            "/api/vehicle/servicerecords/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    def update_service_record(
        self,
        record_id: int,
        date: str,
        mileage: Union[int, float, str],
        description: str,
        cost: Union[int, float, str],
        notes: str = "",
        tags: Optional[List[str]] = None,
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiorna una registrazione di tagliando o intervento di manutenzione esistente."""
        payload = {
            "Id": str(record_id),
            "Date": date,
            "Odometer": str(mileage),
            "Description": description,
            "Cost": str(cost),
            "Notes": notes,
            "Tags": " ".join(tags) if tags else "",
            "ExtraFields": extra_fields or [],
        }
        return self._request("/api/vehicle/servicerecords/update", method="PUT", data=payload)

    # ==========================================
    # RIFORNIMENTI (Gas Records)
    # ==========================================

    def get_gas_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera lo storico dei rifornimenti carburante."""
        res = self._request("/api/vehicle/gasrecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def add_gas_record(
        self,
        vehicle_id: int,
        date: str,
        mileage: Union[int, float, str],
        gallons_or_liters: Union[int, float, str],
        cost: Union[int, float, str],
        is_filled: bool = True,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Registra un nuovo rifornimento di carburante."""
        payload = {
            "Date": date,
            "Mileage": str(mileage),
            "Gallons": str(gallons_or_liters),
            "Cost": str(cost),
            "IsFilled": is_filled,
            "Notes": notes,
        }
        return self._request(
            "/api/vehicle/gasrecords/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    # ==========================================
    # RIPARAZIONI (Repair Records)
    # ==========================================

    def get_repair_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera lo storico delle riparazioni straordinarie."""
        res = self._request("/api/vehicle/repairrecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def add_repair_record(
        self,
        vehicle_id: int,
        date: str,
        mileage: Union[int, float, str],
        description: str,
        cost: Union[int, float, str],
        notes: str = "",
    ) -> Dict[str, Any]:
        """Aggiunge una riparazione straordinaria."""
        payload = {
            "Date": date,
            "Odometer": str(mileage),
            "Description": description,
            "Cost": str(cost),
            "Notes": notes,
        }
        return self._request(
            "/api/vehicle/repairrecords/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    # ==========================================
    # PROMEMORIA E SCADENZE (Reminders)
    # ==========================================

    def get_reminders(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera l'elenco dei promemoria e scadenze (es. tagliando, revisione, bollo)."""
        res = self._request("/api/vehicle/reminders", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def add_reminder(
        self,
        vehicle_id: int,
        description: str,
        metric: str = "Date",
        due_date: Optional[str] = None,
        due_odometer: Optional[Union[int, str]] = None,
        urgency: str = "NotUrgent",
        notes: str = "",
    ) -> Dict[str, Any]:
        """Aggiunge un promemoria/scadenza (Metric: Date, Odometer, Both)."""
        payload = {
            "Description": description,
            "Metric": metric,
            "DueDate": due_date or "",
            "DueOdometer": str(due_odometer) if due_odometer is not None else "",
            "Urgency": urgency,
            "Notes": notes,
        }
        return self._request(
            "/api/vehicle/reminders/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    # ==========================================
    # NOTE E DIARIO DI BORDO (Notes)
    # ==========================================

    def get_notes(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera le note libere del veicolo."""
        res = self._request("/api/vehicle/notes", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def add_note(
        self,
        vehicle_id: int,
        description: str,
        note_text: str,
        is_pinned: bool = False,
        files: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiunge una nota in formato Markdown al veicolo."""
        payload = {
            "Description": description,
            "NoteText": note_text,
            "Pinned": str(is_pinned).lower(),
            "Files": files or [],
        }
        return self._request(
            "/api/vehicle/notes/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    def update_note(
        self,
        record_id: int,
        description: str,
        note_text: str,
        is_pinned: bool = False,
        files: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiorna una nota in formato Markdown esistente."""
        payload = {
            "Id": str(record_id),
            "Description": description,
            "NoteText": note_text,
            "Pinned": str(is_pinned).lower(),
            "Files": files or [],
        }
        return self._request("/api/vehicle/notes/update", method="PUT", data=payload)

    def upload_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Carica un documento o immagine tramite l'endpoint /api/documents/upload."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File non trovato: {file_path}")

        import subprocess
        cmd = [
            "curl", "-s", "-X", "POST",
            f"{self.base_url}/api/documents/upload",
            "-H", f"x-api-key: {self.api_key}",
            "-F", f"documents=@{file_path}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data

    # ==========================================
    # TASSE / BOLLO / ASSICURAZIONE (Tax Records)
    # ==========================================

    def get_tax_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera lo storico di bollo, assicurazione e tasse veicolo."""
        res = self._request("/api/vehicle/taxrecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    def add_tax_record(
        self,
        vehicle_id: int,
        date: str,
        description: str,
        cost: Union[int, float, str],
        notes: str = "",
        tags: Optional[List[str]] = None,
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiunge una registrazione di tassa o assicurazione."""
        payload = {
            "Date": date,
            "Description": description,
            "Cost": str(cost),
            "Notes": notes,
            "Tags": " ".join(tags) if tags else "",
            "ExtraFields": extra_fields or [],
        }
        return self._request(
            "/api/vehicle/taxrecords/add",
            method="POST",
            params={"vehicleId": vehicle_id},
            data=payload,
        )

    def update_tax_record(
        self,
        record_id: int,
        date: str,
        description: str,
        cost: Union[int, float, str],
        notes: str = "",
        tags: Optional[List[str]] = None,
        extra_fields: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Aggiorna una registrazione di tassa o assicurazione esistente."""
        payload = {
            "Id": str(record_id),
            "Date": date,
            "Description": description,
            "Cost": str(cost),
            "Notes": notes,
            "Tags": " ".join(tags) if tags else "",
            "ExtraFields": extra_fields or [],
        }
        return self._request("/api/vehicle/taxrecords/update", method="PUT", data=payload)

    # ==========================================
    # RICAMBI E MAGAZZINO (Supply Records)
    # ==========================================

    def get_supply_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera i ricambi e materiali di consumo a magazzino."""
        res = self._request("/api/vehicle/supplyrecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    # ==========================================
    # PIANI E INTERVENTI FUTURI (Plan Records)
    # ==========================================

    def get_plan_records(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """Recupera la lista degli interventi pianificati."""
        res = self._request("/api/vehicle/planrecords", method="GET", params={"vehicleId": vehicle_id})
        return res if isinstance(res, list) else []

    # ==========================================
    # CAMPI PERSONALIZZATI (Extra Fields)
    # ==========================================

    def get_extra_fields(self) -> List[Dict[str, Any]]:
        """Recupera la configurazione dei campi personalizzati (es. VIN)."""
        res = self._request("/api/extrafields", method="GET")
        return res if isinstance(res, list) else []
