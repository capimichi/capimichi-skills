#!/usr/bin/env python3
"""
Worldfilia Official API Client
Supporta sia l'endpoint GraphQL che l'endpoint REST Performance (/performance).
Documentazione ufficiale: https://portal.worldfilia.net/publisher/service/docs
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, date, time as dtime
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Assicura import paths da worldfilia
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from worldfilia.paths import get_credentials

GRAPHQL_ENDPOINT = "https://portal-api.worldfilia.net/graphql"
PERFORMANCE_ENDPOINT = "https://portal-api.worldfilia.net/performance"


class WorldfiliaAPI:
    def __init__(self, api_key: Optional[str] = None):
        creds = get_credentials()
        self.api_key = (api_key or creds.get("api_key") or "").strip()
        if not self.api_key:
            raise ValueError(
                "Variabile d'ambiente WORLDFILIA_API_KEY (o WORLDFILIA_TOKEN) non impostata! "
                "Esportala nel tuo ambiente prima di procedere."
            )

    def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Esegue una query GraphQL passando il token come parametro richiesto dalla documentazione."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        req = urllib.request.Request(
            GRAPHQL_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "errors" in data and data["errors"]:
                    raise RuntimeError(f"GraphQL Errors: {data['errors']}")
                return data.get("data", {})
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"HTTP Error {e.code}: {err_body}")

    def get_campaigns(
        self,
        take: int = 50,
        skip: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera le campagne disponibili su Worldfilia.
        Supporta filtri 'where', ordinamento e paginazione.
        """
        query_parts = [f'token: "{self.api_key}"', f"take: {take}"]
        if skip is not None:
            query_parts.append(f"skip: {skip}")
        if order_by:
            # es. {id: desc} o {ranking_value: desc}
            order_str = json.dumps(order_by).replace('"', '')
            query_parts.append(f"orderBy: {order_str}")
        if where:
            where_str = json.dumps(where).replace('"', '')
            query_parts.append(f"where: {where_str}")

        args_str = ", ".join(query_parts)
        query = f"""
        query {{
          readCampaigns({args_str}) {{
            id
            name
            status
            created
            modified
            categories
            payment_times
            ranking_value
            Landing
          }}
        }}
        """
        res = self.graphql(query)
        return res.get("readCampaigns", [])

    def get_links(
        self,
        take: int = 50,
        skip: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera i link affiliato creati dall'utente.
        """
        query_parts = [f'token: "{self.api_key}"', f"take: {take}"]
        if skip is not None:
            query_parts.append(f"skip: {skip}")
        if order_by:
            order_str = json.dumps(order_by).replace('"', '')
            query_parts.append(f"orderBy: {order_str}")
        if where:
            where_str = json.dumps(where).replace('"', '')
            query_parts.append(f"where: {where_str}")

        args_str = ", ".join(query_parts)
        query = f"""
        query {{
          readLinks({args_str}) {{
            id
            campaign_id
            landing_id
            created
            modified
            Campaign {{
              id
              name
            }}
            Landing {{
              id
              name
            }}
            subid1
            subid2
            publisher_domains
            social_title
            social_caption
            social_image_url
          }}
        }}
        """
        res = self.graphql(query)
        return res.get("readLinks", [])

    def get_performance(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        campaign_id: Optional[int] = None,
        landing_id: Optional[int] = None,
        subid1: Optional[str] = None,
        status: Optional[str] = None,
        group_by: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Interroga il servizio dedicato REST /performance per statistiche aggregate o dettagliate.
        Formato date: ISO 8601 UTC (es. '2026-11-01T00:00:00.000Z' o YYYY-MM-DD).
        """
        # Default intervallo: ultimi 7 giorni
        if not date_from:
            date_from = f"{date.today().isoformat()}T00:00:00.000Z"
        elif "T" not in date_from:
            date_from = f"{date_from}T00:00:00.000Z"

        if not date_to:
            date_to = f"{date.today().isoformat()}T23:59:59.999Z"
        elif "T" not in date_to:
            date_to = f"{date_to}T23:59:59.999Z"

        and_filters: List[Dict[str, Any]] = [
            {
                "AND": [
                    {"created": {"gte": date_from}},
                    {"created": {"lte": date_to}}
                ]
            }
        ]

        if campaign_id:
            and_filters.append({"OR": [{"campaignId": {"equals": campaign_id}}]})
        if landing_id:
            and_filters.append({"OR": [{"landingId": {"equals": landing_id}}]})
        if subid1:
            and_filters.append({"OR": [{"subid1": {"contains": subid1}}]})
        if status:
            and_filters.append({"OR": [{"status": {"equals": status}}]})

        payload: Dict[str, Any] = {
            "filter": {
                "AND": and_filters
            }
        }

        if group_by:
            payload["groupBy"] = group_by

        req = urllib.request.Request(
            PERFORMANCE_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"REST Performance HTTP Error {e.code}: {err_body}")
