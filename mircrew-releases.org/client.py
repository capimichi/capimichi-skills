import os
import sys
import json
import subprocess
from urllib.parse import urljoin, parse_qs, urlparse
from bs4 import BeautifulSoup
from cloakbrowser import launch_persistent_context

DEFAULT_PROFILE_DIR = os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')), 'browser-profiles', 'mircrew')
BASE_URL = "https://mircrew-releases.org"


def get_credentials_from_bitwarden():
    """Tenta di recuperare le credenziali da Bitwarden CLI se disponibile."""
    try:
        cmd = ["bw", "list", "items", "--search", "mircrew"]
        session = os.environ.get("BW_SESSION")
        if session:
            cmd.extend(["--session", session])
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        items = json.loads(res.stdout)
        for item in items:
            login = item.get("login")
            if login and login.get("username") and login.get("password"):
                return login.get("username"), login.get("password")
            # Controlla se presenti nelle note
            notes = item.get("notes", "")
            if "MIRCREW_USERNAME=" in notes and "MIRCREW_PASSWORD=" in notes:
                u, p = None, None
                for line in notes.splitlines():
                    if line.startswith("MIRCREW_USERNAME="):
                        u = line.split("=", 1)[1].strip()
                    elif line.startswith("MIRCREW_PASSWORD="):
                        p = line.split("=", 1)[1].strip()
                if u and p:
                    return u, p
    except Exception:
        pass
    return None, None


class MircrewBrowser:
    def __init__(self, profile_dir=DEFAULT_PROFILE_DIR, headless=False):
        self.profile_dir = profile_dir
        self.headless = headless
        self.context = None
        self.page = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        if not self.context:
            os.makedirs(self.profile_dir, exist_ok=True)
            self.context = launch_persistent_context(self.profile_dir, headless=self.headless)
            self.page = self.context.new_page()
            self.page.set_viewport_size({"width": 1280, "height": 800})
        return self

    def close(self):
        if self.context:
            self.context.close()
            self.context = None
            self.page = None

    def is_logged_in(self) -> bool:
        """Verifica se la sessione corrente è autenticata."""
        self.page.goto(BASE_URL, wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)
        logout_btn = self.page.locator("a[href*='mode=logout']")
        return logout_btn.count() > 0

    def login(self, username=None, password=None) -> bool:
        """Esegue il login su mircrew-releases.org."""
        if not username or not password:
            username = os.environ.get("MIRCREW_USERNAME")
            password = os.environ.get("MIRCREW_PASSWORD")

        if not username or not password:
            bw_user, bw_pass = get_credentials_from_bitwarden()
            if bw_user and bw_pass:
                username, password = bw_user, bw_pass

        if not username or not password:
            raise ValueError("Credenziali mancanti. Imposta MIRCREW_USERNAME e MIRCREW_PASSWORD.")

        self.page.goto(f"{BASE_URL}/ucp.php?mode=login", wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)

        # Compilazione form di login
        self.page.locator("input[name='username']").fill(username)
        self.page.locator("input[name='password']").fill(password)

        autologin = self.page.locator("input[name='autologin']")
        if autologin.count() > 0:
            autologin.check()

        viewonline = self.page.locator("input[name='viewonline']")
        if viewonline.count() > 0:
            viewonline.check()

        self.page.locator("input[type='submit'][name='login']").click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(3000)

        return self.is_logged_in()

    def ensure_logged_in(self, username=None, password=None):
        """Verifica lo stato di login e autentica se necessario."""
        if not self.is_logged_in():
            print("Sessione non autenticata. Esecuzione login...")
            if not self.login(username, password):
                raise RuntimeError("Autenticazione fallita su mircrew-releases.org.")
            print("Autenticazione completata con successo.")
        else:
            print("Sessione già autenticata.")

    def search(self, query: str, title_only: bool = True, limit: int = 30) -> list[dict]:
        """Esegue una ricerca su Mircrew e restituisce la lista delle release."""
        self.ensure_logged_in()

        sf_param = "titleonly" if title_only else "all"
        search_url = (
            f"{BASE_URL}/search.php?keywords={query}"
            f"&terms=all&author=&sc=1&sf={sf_param}&sr=topics&sk=t&sd=d&st=0&ch=300&t=0&submit=Cerca"
        )

        self.page.goto(search_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(2500)

        soup = BeautifulSoup(self.page.content(), "html.parser")
        results = []

        rows = soup.select("li.row")
        for row in rows:
            link = row.select_one("a.topictitle")
            if not link or not link.get("href"):
                continue

            href = link["href"]
            full_url = urljoin(BASE_URL, href)
            title = link.get_text(" ", strip=True)

            # Estrazione topic ID
            topic_id = None
            parsed = urlparse(full_url)
            qs = parse_qs(parsed.query)
            if "t" in qs:
                topic_id = qs["t"][0]

            # Forum / Categoria
            forum_link = row.select_one("a.forumtitle, .forum-link")
            forum_name = forum_link.get_text(strip=True) if forum_link else ""

            # Autore e Data se presenti
            author_link = row.select_one(".username, .username-coloured")
            author = author_link.get_text(strip=True) if author_link else ""

            results.append({
                "id": topic_id,
                "title": title,
                "url": full_url,
                "forum": forum_name,
                "author": author
            })

            if len(results) >= limit:
                break

        return results

    def get_topic_details(self, topic_url_or_id: str, auto_thank: bool = True) -> dict:
        """
        Apre la pagina di un topic, preme il tasto Ringrazia se necessario,
        ed estrae tutti i link magnet e torrent.
        """
        self.ensure_logged_in()

        if topic_url_or_id.startswith("http"):
            url = topic_url_or_id
        else:
            url = f"{BASE_URL}/viewtopic.php?t={topic_url_or_id}"

        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)

        # Se il contenuto è bloccato o se auto_thank è True, clicchiamo sul pulsante di ringraziamento
        if auto_thank:
            thank_selector = (
                ".post a:has(i.fa-thumbs-o-up),"
                " .post a:has(i.fa-thumbs-up),"
                " .post a:has(i.icon-thumbs-up)"
            )
            thank_button = self.page.locator(thank_selector)
            if thank_button.count() > 0 and thank_button.first.is_visible():
                try:
                    thank_button.first.click()
                    self.page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"Nota: impossibile cliccare il tasto ringraziamento: {e}")

        soup = BeautifulSoup(self.page.content(), "html.parser")

        # Titolo del topic
        title_el = soup.select_one("h2.topic-title, .topic-title")
        title = title_el.get_text(strip=True) if title_el else self.page.title()

        # Estrazione magnet links
        magnets = []
        for a in soup.select("a[href^='magnet:']"):
            href = a.get("href")
            if href and href not in magnets:
                magnets.append(href)

        # Estrazione eventuali file .torrent
        torrent_links = []
        for a in soup.select("a[href*='.torrent'], a[href*='download/file.php']"):
            href = a.get("href")
            if href and href.startswith("http") and not href.startswith("magnet:"):
                torrent_links.append(href)
            elif href and not href.startswith("magnet:"):
                torrent_links.append(urljoin(BASE_URL, href))

        return {
            "title": title,
            "url": url,
            "magnets": magnets,
            "torrent_links": torrent_links
        }
