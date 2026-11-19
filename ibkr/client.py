"""IBKR Web API Client (Client Portal Gateway)

Fornisce interazione in sola lettura con l'API Client Portal di Interactive Brokers.
Supporta la gestione automatica delle sessioni, keep-alive (tickle), e query su:
- Stato autenticazione e sessione
- Conti disponibili
- Riepilogo saldo, NAV e liquidità (Portfolio Summary)
- Posizioni aperte (Portfolio Positions)
- Saldo valute (Ledger)
- Eseguiti / Trade recenti
"""

import os
import sys
import json
import logging
from typing import Any, Dict, List, Optional
import urllib3
import requests

# Disabilita i warning SSL per certificati self-signed locali di CPGW
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("ibkr")


class IBKRClientError(Exception):
    """Eccezione base per errori del client IBKR."""
    pass


class IBKRAuthRequiredError(IBKRClientError):
    """Sollevata quando la sessione gateway non è autenticata."""
    pass


class IBKRConnectionError(IBKRClientError):
    """Sollevata quando il Gateway locale non è raggiungibile."""
    pass


class IBKRClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        account_id: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
        timeout: tuple = (3.0, 10.0),
    ):
        """Inizializza il client IBKR.
        
        Legge le impostazioni dalle variabili d'ambiente di sistema:
        - IBKR_GATEWAY_URL: Default 'https://localhost:5001'
        - IBKR_ACCOUNT_ID: Conto predefinito (es. 'U1234567')
        - IBKR_SSL_VERIFY: Se verificare SSL (default: False per localhost)
        """
        self.base_url = (
            base_url
            or os.environ.get("IBKR_GATEWAY_URL")
            or "https://localhost:5001"
        ).rstrip("/")
        self.account_id = account_id or os.environ.get("IBKR_ACCOUNT_ID")
        
        if verify_ssl is not None:
            self.verify_ssl = verify_ssl
        else:
            self.verify_ssl = os.environ.get("IBKR_SSL_VERIFY", "false").lower() in ("true", "1", "yes")
            
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = self.verify_ssl

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        try:
            resp = self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise IBKRConnectionError(
                f"Impossibile connettersi al Gateway IBKR su {self.base_url}.\n"
                f"Assicurati che il Gateway sia in esecuzione (es. 'bash $USER_SKILLS_DIR/ibkr/run_gateway.sh docker')."
            ) from e
        except requests.exceptions.Timeout as e:
            raise IBKRConnectionError(f"Timeout durante la richiesta al Gateway IBKR ({url}).") from e

        if resp.status_code == 401:
            raise IBKRAuthRequiredError(
                "Sessione IBKR non autenticata o scaduta.\n"
                f"Apri nel browser: {self.base_url} ed effettua il login confermando il 2FA."
            )
        elif resp.status_code == 403:
            raise IBKRClientError(
                f"Accesso negato (403) da {url}.\n"
                "Verifica la whitelist IP in conf.yaml del Gateway (ips.allow)."
            )

        try:
            return resp.json()
        except Exception:
            return resp.text

    def check_status(self) -> Dict[str, Any]:
        """Verifica lo stato del server e dell'autenticazione."""
        data = self._request("GET", "/v1/api/iserver/auth/status")
        return data if isinstance(data, dict) else {"raw": data}

    def init_session(self) -> Dict[str, Any]:
        """Inizializza il contesto brokerage SSO (/iserver/auth/ssodh/init)."""
        return self._request(
            "POST",
            "/v1/api/iserver/auth/ssodh/init",
            json={"publish": True, "compete": True},
        )

    def tickle(self) -> Dict[str, Any]:
        """Invia un keep-alive ping per prolungare la validità della sessione."""
        return self._request("POST", "/v1/api/tickle")

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Recupera la lista dei conti associati all'utente autenticato."""
        # Prima prova l'endpoint portfolio
        res = self._request("GET", "/v1/api/portfolio/accounts")
        if isinstance(res, list):
            return res
        # Fallback a iserver accounts
        res_iserver = self._request("GET", "/v1/api/iserver/accounts")
        if isinstance(res_iserver, dict) and "accounts" in res_iserver:
            return [{"id": acc} for acc in res_iserver["accounts"]]
        return []

    def resolve_account_id(self, target_account_id: Optional[str] = None) -> str:
        """Determina l'account ID da usare (esplicito, env, o primo conto disponibile)."""
        if target_account_id:
            return target_account_id
        if self.account_id:
            return self.account_id

        accounts = self.get_accounts()
        if not accounts:
            raise IBKRClientError("Nessun conto IBKR trovato associato a questa sessione.")
        
        first = accounts[0]
        acc_id = first.get("id") or first.get("accountId")
        if not acc_id:
            raise IBKRClientError(f"Impossibile determinare l'ID del conto da: {first}")
        return acc_id

    def get_summary(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Recupera il riepilogo finanziario del conto (NAV, Liquidità, Buying Power, PnL)."""
        acc_id = self.resolve_account_id(account_id)
        # Assicura inizializzazione contesto
        try:
            self.get_accounts()
        except Exception:
            pass
        return self._request("GET", f"/v1/api/portfolio/{acc_id}/summary")

    def get_positions(self, account_id: Optional[str] = None, page_id: int = 0) -> List[Dict[str, Any]]:
        """Recupera le posizioni aperte per il conto specificato."""
        acc_id = self.resolve_account_id(account_id)
        try:
            self.get_accounts()
        except Exception:
            pass

        # Prova endpoint rapido portfolio2
        try:
            res2 = self._request("GET", f"/v1/api/portfolio2/{acc_id}/positions")
            if isinstance(res2, list):
                return res2
        except Exception:
            pass

        # Fallback endpoint paginato standard
        res = self._request("GET", f"/v1/api/portfolio/{acc_id}/positions/{page_id}")
        return res if isinstance(res, list) else []

    def get_ledger(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Recupera il dettaglio dei saldi di liquidità per valuta (EUR, USD, ecc.)."""
        acc_id = self.resolve_account_id(account_id)
        return self._request("GET", f"/v1/api/portfolio/{acc_id}/ledger")

    def get_trades(self) -> List[Dict[str, Any]]:
        """Recupera gli ordini eseguiti (trades) recenti."""
        res = self._request("GET", "/v1/api/iserver/account/trades")
        return res if isinstance(res, list) else []
