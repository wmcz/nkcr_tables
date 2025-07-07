# Nástroje pro práci s daty NKČR a Wikidata

Tento repozitář obsahuje sadu Python skriptů určených pro zpracování, propojování a správu dat mezi autoritní bází Národní knihovny ČR (NKČR) a Wikidaty.

## Přehled skriptů

*   `vkol.py`: Hlavní skript pro stahování dat z NKČR pomocí OAI-PMH protokolu a jejich následné parsování z formátu MARCXML.
*   `nkcr.py`: Obsahuje funkce pro porovnávání a propojování dat mezi NKČR a Wikidaty, včetně vyhledávání osob a měst, a také funkce pro aktualizaci databáze.
*   `import_autority.py`: Skript pro import autoritních záznamů z lokální databáze do vlastní instance Wikibase.
*   `user-config.py`: Konfigurační soubor pro Pywikibot, který definuje uživatelské účty a výchozí nastavení pro komunikaci s Wikidaty a dalšími MediaWiki weby.
*   Ostatní soubory (`autrecord.py`, `autxmlhandler.py`, atd.): Pomocné skripty a moduly, které zajišťují specifické funkce, jako je zpracování XML, deduplikace, logování a další.

## Hlavní funkce

*   **Stahování dat z NKČR:** Skripty umožňují stahovat záznamy z NKČR ve formátu MARC21 přes OAI-PMH.
*   **Zpracování MARCXML:** Nástroje obsahují funkce pro parsování MARCXML záznamů a extrakci potřebných informací.
*   **Propojování s Wikidaty:** Klíčovou funkcí je propojování autoritních záznamů NKČR s odpovídajícími položkami na Wikidatech. Skripty vyhledávají shody na základě jména, dat narození a úmrtí a dalších údajů.
*   **Správa vlastní Wikibase instance:** Možnost importovat a vytvářet nové položky ve vlastní instanci Wikibase na základě dat z NKČR.
*   **Generování reportů:** Skripty umožňují vytvářet různé CSV soubory pro analýzu a reporting, například seznamy autorit k aktualizaci, statistiky a další.

## Instalace a nastavení

1.  **Naklonujte repozitář:**
    ```bash
    git clone <URL-repozitare>
    cd <nazev-repozitare>
    ```

2.  **Nainstalujte závislosti:**
    Ujistěte se, že máte nainstalovaný Python 3 a `pip`. Poté nainstalujte potřebné knihovny:
    ```bash
    pip install -r requirements.txt
    ```
    *(Poznámka: `requirements.txt` není v repozitáři přítomen, je třeba ho vytvořit na základě importů v jednotlivých skriptech. Mezi hlavní závislosti patří `pywikibot`, `requests`, `pymarc`, `lxml`, `mysqlclient` a další.)*

3.  **Nastavte `user-config.py`:**
    Upravte soubor `user-config.py` a zadejte své přihlašovací údaje pro bota na Wikidatech a případně na vaší vlastní Wikibase instanci.

4.  **Nastavení databáze:**
    Některé skripty vyžadují připojení k lokální MySQL databázi. Ujistěěte se, že máte databázi vytvořenou a přihlašovací údaje jsou správně nastaveny ve skriptech, které ji používají.

## Použití

Jednotlivé skripty lze spouštět z příkazové řádky. Níže jsou uvedeny příklady použití některých z nich:

*   **Stažení a zpracování dat z NKČR:**
    ```bash
    python vkol.py
    ```

*   **Propojení autorit s Wikidaty:**
    ```bash
    python nkcr.py
    ```

*   **Import autorit do Wikibase:**
    ```bash
    python import_autority.py
    ```

Pro detailní informace o funkci jednotlivých skriptů a jejich parametrech se podívejte přímo do jejich zdrojového kódu.
