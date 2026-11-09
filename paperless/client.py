#!/usr/bin/env python3
"""
Paperless-ngx API Client
Fornisce l'interfaccia client per interagire con l'API REST di Paperless-ngx.
Legge le credenziali dalle variabili d'ambiente (gestite da chezmoi / Bitwarden):
- PAPERLESS_BASE_URL (o PAPERLESS_URL)
- PAPERLESS_API_KEY (o PAPERLESS_TOKEN, PAPERLESS_API_TOKEN)
"""

import os
import sys
import json
import subprocess
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urlencode, quote

# Header obbligatorio per simulare un browser reale e bypassare eventuali WAF/Cloudflare (Errore 1010)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class PaperlessClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (
            base_url
            or os.environ.get("PAPERLESS_BASE_URL")
            or os.environ.get("PAPERLESS_URL")
            or "https://paperless.michelecapicchioni.com"
        ).rstrip("/")

        self.api_key = (
            api_key
            or os.environ.get("PAPERLESS_API_KEY")
            or os.environ.get("PAPERLESS_API_TOKEN")
            or os.environ.get("PAPERLESS_TOKEN")
        )

        if not self.api_key:
            raise ValueError(
                "❌ Credenziali Paperless non trovate nelle variabili d'ambiente!\n"
                "Assicurati che PAPERLESS_API_KEY (o PAPERLESS_TOKEN) sia esportata.\n"
                "Le credenziali sono configurate in chezmoi da Bitwarden:\n"
                "  item: 'paperless.michelecapicchioni.com capimichi'\n"
                "Verifica con: 'source ~/.config/zsh/envs/personal.zsh' o riesegui chezmoi apply."
            )

        self._correspondents_cache: Optional[Dict[str, int]] = None
        self._tags_cache: Optional[Dict[str, int]] = None
        self._doc_types_cache: Optional[Dict[str, int]] = None

    def _get_headers(self, content_type: Optional[str] = "application/json") -> Dict[str, str]:
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Accept": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}
            if clean_params:
                url += ("&" if "?" in url else "?") + urlencode(clean_params, doseq=True)

        try:
            import requests

            req_headers = self._get_headers(content_type=None if files else "application/json")
            if files:
                resp = requests.request(method, url, headers=req_headers, data=data, files=files, timeout=60)
            elif data is not None:
                resp = requests.request(method, url, headers=req_headers, json=data, timeout=30)
            else:
                resp = requests.request(method, url, headers=req_headers, timeout=30)

            if resp.status_code >= 400:
                try:
                    err_json = resp.json()
                    err_msg = json.dumps(err_json, ensure_ascii=False)
                except Exception:
                    err_msg = resp.text
                raise RuntimeError(f"HTTP {resp.status_code} su {url}: {err_msg}")

            if "application/json" in resp.headers.get("Content-Type", ""):
                return resp.json()
            return resp.content
        except ImportError:
            # Fallback a urllib standard se requests non è disponibile
            import urllib.request
            import urllib.error

            body_bytes = None
            content_type = "application/json"
            if data is not None:
                body_bytes = json.dumps(data).encode("utf-8")
            
            headers = self._get_headers(content_type=content_type)
            req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_bytes = response.read()
                    try:
                        return json.loads(res_bytes.decode("utf-8"))
                    except Exception:
                        return res_bytes
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"HTTP {e.code} su {url}: {err_text}")

    # --- Metadati: Corrispondenti, Tag, Tipi documento ---

    def list_correspondents(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"page_size": 200}
        if search:
            params["name__icontains"] = search
        res = self.request("api/correspondents/", params=params)
        return res.get("results", [])

    def get_correspondent_id(self, name_or_id: Union[str, int]) -> Optional[int]:
        if isinstance(name_or_id, int) or (isinstance(name_or_id, str) and name_or_id.isdigit()):
            return int(name_or_id)
        
        name_str = str(name_or_id).strip().lower()
        if self._correspondents_cache is None:
            items = self.list_correspondents()
            self._correspondents_cache = {c["name"].lower(): c["id"] for c in items}
        
        # Exact match
        if name_str in self._correspondents_cache:
            return self._correspondents_cache[name_str]
        
        # Partial match
        for k, v in self._correspondents_cache.items():
            if name_str in k or k in name_str:
                return v
        return None

    def create_correspondent(self, name: str, owner: Optional[int] = None) -> Dict[str, Any]:
        """Crea un nuovo corrispondente su Paperless e aggiorna la cache."""
        data = {
            "name": name.strip(),
            "owner": owner,
            "matching_algorithm": 6,
        }
        res = self.request("api/correspondents/", method="POST", data=data)
        self._correspondents_cache = None  # Invalida la cache
        return res

    def list_tags(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"page_size": 200}
        if search:
            params["name__icontains"] = search
        res = self.request("api/tags/", params=params)
        return res.get("results", [])

    def get_tag_id(self, name_or_id: Union[str, int]) -> Optional[int]:
        if isinstance(name_or_id, int):
            return name_or_id
        
        name_str = str(name_or_id).strip().lower()
        if self._tags_cache is None:
            items = self.list_tags()
            self._tags_cache = {t["name"].lower(): t["id"] for t in items}
        
        if name_str in self._tags_cache:
            return self._tags_cache[name_str]
        
        if isinstance(name_or_id, str) and name_or_id.isdigit():
            return int(name_or_id)
        
        for k, v in self._tags_cache.items():
            if name_str in k or k in name_str:
                return v
        return None

    def create_tag(
        self, name: str, color: Optional[str] = None, owner: Optional[int] = None
    ) -> Dict[str, Any]:
        """Crea un nuovo tag su Paperless e aggiorna la cache."""
        data: Dict[str, Any] = {
            "name": name.strip(),
            "owner": owner,
            "matching_algorithm": 6,
        }
        if color:
            data["color"] = color
        res = self.request("api/tags/", method="POST", data=data)
        self._tags_cache = None  # Invalida la cache
        return res

    def list_document_types(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"page_size": 200}
        if search:
            params["name__icontains"] = search
        res = self.request("api/document_types/", params=params)
        return res.get("results", [])

    def get_document_type_id(self, name_or_id: Union[str, int]) -> Optional[int]:
        if isinstance(name_or_id, int) or (isinstance(name_or_id, str) and name_or_id.isdigit()):
            return int(name_or_id)
        
        name_str = str(name_or_id).strip().lower()
        if self._doc_types_cache is None:
            items = self.list_document_types()
            self._doc_types_cache = {dt["name"].lower(): dt["id"] for dt in items}
        
        if name_str in self._doc_types_cache:
            return self._doc_types_cache[name_str]
        for k, v in self._doc_types_cache.items():
            if name_str in k or k in name_str:
                return v
        return None

    def create_document_type(self, name: str, owner: Optional[int] = None) -> Dict[str, Any]:
        """Crea un nuovo tipo di documento su Paperless e aggiorna la cache."""
        data = {
            "name": name.strip(),
            "owner": owner,
            "matching_algorithm": 6,
        }
        res = self.request("api/document_types/", method="POST", data=data)
        self._doc_types_cache = None  # Invalida la cache
        return res

    # --- Documenti ---

    def search_documents(
        self,
        query: Optional[str] = None,
        correspondent: Optional[Union[str, int]] = None,
        tag: Optional[Union[str, int, List[Union[str, int]]]] = None,
        document_type: Optional[Union[str, int]] = None,
        year: Optional[Union[str, int]] = None,
        page: int = 1,
        page_size: int = 25,
        ordering: str = "-created",
    ) -> Dict[str, Any]:
        params = {
            "page": page,
            "page_size": page_size,
            "ordering": ordering,
        }
        if query:
            params["query"] = query

        if correspondent is not None:
            c_id = self.get_correspondent_id(correspondent)
            if c_id:
                params["correspondent__id"] = c_id
            else:
                print(f"⚠️ Corrispondente '{correspondent}' non trovato, filtro ignorato.")

        if document_type is not None:
            dt_id = self.get_document_type_id(document_type)
            if dt_id:
                params["document_type__id"] = dt_id
            else:
                print(f"⚠️ Tipo documento '{document_type}' non trovato, filtro ignorato.")

        if tag is not None:
            tags_list = tag if isinstance(tag, list) else [tag]
            tag_ids = []
            for t in tags_list:
                t_id = self.get_tag_id(t)
                if t_id:
                    tag_ids.append(t_id)
                else:
                    print(f"⚠️ Tag '{t}' non trovato, ignorato.")
            if tag_ids:
                params["tags__id__in"] = ",".join(map(str, tag_ids))

        if year:
            params["created__year"] = str(year)

        return self.request("api/documents/", params=params)

    def get_document(self, doc_id: int) -> Dict[str, Any]:
        return self.request(f"api/documents/{doc_id}/")

    def update_document(self, doc_id: int, **fields) -> Dict[str, Any]:
        """
        Aggiorna campi di un documento esistente (titolo, tags, correspondent, document_type, ecc.).
        """
        if "tags" in fields and isinstance(fields["tags"], list):
            resolved_tags = []
            for t in fields["tags"]:
                t_id = self.get_tag_id(t)
                if t_id:
                    resolved_tags.append(t_id)
            fields["tags"] = resolved_tags

        if "correspondent" in fields and fields["correspondent"] is not None:
            c_id = self.get_correspondent_id(fields["correspondent"])
            if c_id:
                fields["correspondent"] = c_id

        if "document_type" in fields and fields["document_type"] is not None:
            dt_id = self.get_document_type_id(fields["document_type"])
            if dt_id:
                fields["document_type"] = dt_id

        return self.request(f"api/documents/{doc_id}/", method="PATCH", data=fields)

    def add_note(self, doc_id: int, note: str) -> List[Dict[str, Any]]:
        """Aggiunge una nota a un documento."""
        return self.request(f"api/documents/{doc_id}/notes/", method="POST", data={"note": note.strip()})

    def list_custom_fields(self) -> List[Dict[str, Any]]:
        """Elenca tutti i custom fields configurati."""
        res = self.request("api/custom_fields/")
        return res.get("results", [])

    def create_custom_field(self, name: str, data_type: str = "string") -> Dict[str, Any]:
        """Crea un nuovo campo personalizzato (data_type: string, date, boolean, integer, float, monetary, url, select)."""
        return self.request("api/custom_fields/", method="POST", data={"name": name.strip(), "data_type": data_type})

    def download_document(
        self, doc_id: int, original: bool = False, output_path: Optional[str] = None
    ) -> str:
        endpoint = f"api/documents/{doc_id}/download/" if original else f"api/documents/{doc_id}/preview/"
        content = self.request(endpoint)
        if isinstance(content, dict):
            # Nel caso l'endpoint restituisse JSON anziché stream binario
            raise RuntimeError(f"Download inatteso (risposta JSON): {content}")

        doc_info = self.get_document(doc_id)
        default_name = doc_info.get("original_file_name") or f"document_{doc_id}.pdf"

        if output_path:
            dest = Path(output_path)
            if dest.is_dir():
                dest = dest / default_name
        else:
            dest = Path(default_name)

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(content)
        return str(dest.resolve())

    def repair_pdf(self, input_pdf: str, output_pdf: Optional[str] = None) -> str:
        """
        Controlla e ripara eventuali PDF corrotti usando qpdf (risolve tabelle xref danneggiate).
        """
        in_p = Path(input_pdf)
        out_p = Path(output_pdf) if output_pdf else in_p.parent / f"{in_p.stem}_repaired.pdf"

        # Check integrità
        check = subprocess.run(["qpdf", "--check", str(in_p)], capture_output=True, text=True)
        if check.returncode == 0:
            return str(in_p.resolve())

        print(f"🔧 Rilevata anomalia nel PDF (exit code {check.returncode}). Riparazione in corso con qpdf...")
        repair = subprocess.run(["qpdf", str(in_p), str(out_p)], capture_output=True, text=True)
        # qpdf restituisce 0 per successo, 3 per successo con warning
        if repair.returncode in (0, 3) and out_p.exists():
            print(f"✅ PDF riparato con successo: {out_p}")
            return str(out_p.resolve())
        else:
            print(f"⚠️ Impossibile riparare il file con qpdf: {repair.stderr}")
            return str(in_p.resolve())

    def upload_document(
        self,
        file_path: str,
        title: Optional[str] = None,
        correspondent: Optional[Union[str, int]] = None,
        tags: Optional[List[Union[str, int]]] = None,
        document_type: Optional[Union[str, int]] = None,
        created: Optional[str] = None,
        auto_repair: bool = True,
    ) -> Any:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File non trovato: {file_path}")

        actual_file_to_upload = str(path)
        if auto_repair and path.suffix.lower() == ".pdf":
            try:
                actual_file_to_upload = self.repair_pdf(str(path))
            except Exception as e:
                print(f"⚠️ Warning controllo PDF: {e}")

        data: Dict[str, Any] = {}
        if title:
            data["title"] = title
        if created:
            data["created"] = created

        if correspondent:
            c_id = self.get_correspondent_id(correspondent)
            if c_id:
                data["correspondent"] = c_id

        if document_type:
            dt_id = self.get_document_type_id(document_type)
            if dt_id:
                data["document_type"] = dt_id

        if tags:
            tag_ids = []
            for t in tags:
                tid = self.get_tag_id(t)
                if tid:
                    tag_ids.append(tid)
            if tag_ids:
                data["tags"] = tag_ids

        mime_type, _ = mimetypes.guess_type(actual_file_to_upload)
        mime_type = mime_type or "application/octet-stream"

        with open(actual_file_to_upload, "rb") as f:
            files = {
                "document": (Path(actual_file_to_upload).name, f, mime_type)
            }
            res = self.request("api/documents/post_document/", method="POST", data=data, files=files)
            return res
