# Dicozorus

**Dicozorus** is a tool to generate and maintain web wordlists. 

It eliminates the overhead of managing multiple wordlists by storing paths enriched with metadata in a local SQLite database. 


**Just want a great wordlist without the tool?** Skip the setup and use [**lazy.txt**](./lazy.txt).

## Why Dicozorus?
Standard wordlists often present problems such as missing entries, lack of relevant sorting, inappropriate size or junk entries. 

Dicozorus solves these issues by associating entries with enriched metadata. This allows:

* **Smart Sorting:** Places the most critical and highly probable entries at the top of your list so you find valuable endpoints faster.
* **Targeted Extension Filtering:** If a site runs PHP, you can skip ASP and JSP extensions entirely, saving time and network bandwidth.
* **Adaptive Sizing:** Easily scale your wordlist size depending on target stability, rate limits, or network connectivity.
* **Contextual Fuzzing:** Generate lists specifically tuned for directory fuzzing, file fuzzing, or both.


## Installation
```bash
$ pipx install git+https://github.com/synacktiv/dicozorus/
```
## Dicozorus overview
<img width="800" alt="dicozorus_overview" src="https://github.com/user-attachments/assets/94dab30b-2db7-4077-8e66-7c0b9d6d33c2" />

## Architecture & Data Storage

Dicozorus stores data locally in an SQLite database located at `$HOME/.dicozorus/db.sqlite`. Each entry tracks the following attributes:

| Field | Description |
| :--- | :--- |
| **path** | The endpoint name (e.g., `jmx-console/` or `app-dev.php`). |
| **type** | Structural classification: `FILE`, `DIRECTORY`, or `PATH`. |
| **criticality** | Priority tier: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`, `UNRANKED`. |
| **count** | How many times this specific URL has been fed into the database. |
| **category**| Type of vulnerability it is attached (e.g., `RCE`, `ADMIN_INTERFACE` or `KNOWN_APP`)
| **tag** | Contextual tags for technology filtering (e.g., `PHP`, `JAVA`, `LINUX`). |
| **reference**| An optional link to an associated vulnerability, advisory, or known endpoint documentation. |


## Dicozorus built-in wordlists

For more convenience, dicozorus is packed with built-in wordlists. The entries present in these wordlists comes from various locations:
- Others wordlists or projects (`dirsearch`, `bo0om`, `Seclist`, `nuclei`. etc.)
- Public vulnerability reports (HackerOne reports, ExploitDB vulnerabilities, Github Advisories)
- Redteam / Pentests feedbacks

<img  width="800" alt="dicozorus_sources" src="https://github.com/user-attachments/assets/18195eb2-be3b-4bf5-a74b-023712aeff2e" />

### Current set of built-in wordlists
| Name | Description |
| :--- | :--- |
|critical.wordlist  | CRITICAL entries only|
|high.wordlist      | HIGH entries only|
|medium.wordlist    | MEDIUM entries only|
|low.wordlist       | LOW entries only|
|info.wordlist      | INFO entries only|
|unranked.wordlist  | Entries with no affected criticality|
|bo0om.wordlist     | Entries from BoOoM wordlist with no affected criticality|
|dirsearch.wordlist | Entries from dirsearch wordlist with no affected criticality|
|exploitdb.wordlist | Entries from exploitDB with no affected criticality|
|hackerone.wordlist | Entries from HackerOne public reports with no affected criticality|
|seen.wordlist      | Entries that were seen here and there, with no affected criticality|
|dangerous.wordlist | Dangerous entries such as `/shutdown` or `reboot`|

### lazy.txt
Each time a change is made to the built-in wordlists, [lazy.txt](./lazy.txt) is generated. It includes all built-in entries except dangerous ones, sorted by criticality and count.


## Usage
```bash
$ dicozorus
usage: dicozorus [-h] [-v] [--version] {feed,gen,init,modify,stats,check} ...

Dicozorus allows to generate custom wordlists. It can be fed with wordlists from your own or initialized using a predefined set of wordlists. Entries are
stored in a sqlite database located in $HOME/.dicozorus/db.sqlite

positional arguments:
  {feed,gen,init,modify,stats,check}
                        Subcommand to run
    feed                Feed dicozorus db with wordlist files or scan results
    gen                 Generate wordlist using the dicozorus db.
    init                Initialize the dicozorus database.
    modify              Modify dicozorus DB directly. Use it to add / remove / update one or multiple entries.
    stats               Show stats about the dicozorus database.
    check               The check command is used to compare entry or wordlists with the dicozorus database

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity
  --version             show program's version number and exit
```

### Initialize the dicozorus database
```bash
$ dicozorus init -F -W wordlists/
[+] Initializing dicozorus database
[+] Creating dicozorus tables
[+] Parsing dicozorus CSV file wordlists/low.wordlist
[+] Parsing dicozorus CSV file wordlists/unranked.wordlist
[+] Parsing dicozorus CSV file wordlists/hackerone.wordlist
[+] Parsing dicozorus CSV file wordlists/medium.wordlist
[+] Parsing dicozorus CSV file wordlists/exploitdb.wordlist
[+] Parsing dicozorus CSV file wordlists/critical.wordlist
[+] Parsing dicozorus CSV file wordlists/high.wordlist
[+] Parsing dicozorus CSV file wordlists/bo0om.wordlist
[+] Parsing dicozorus CSV file wordlists/seen.wordlist
[+] Parsing dicozorus CSV file wordlists/info.wordlist
[+] Parsing dicozorus CSV file wordlists/dirsearch.wordlist
```
### Feed the dicozorus database
```bash
$ dicozorus feed -w fuzz.txt
[+] Parsing wordlist fuzz.txt
```

### Generate a wordlist
```bash
$ dicozorus gen -m 5
app_dev.php
actuator/jolokia
jolokia
bitrix/admin/php_command_line.php
jenkins/script
```
### Check the metadata associated with a specific entry
```bash
$ dicozorus check -e '_fragment'
_fragment [type: FILE, criticality: CRITICAL, count: 2, category: RCE, taglist: ['PHP', 'Bo0oM'], reference: https://www.ambionics.io/blog/symfony-secret-fragment]
```

### Show stats about the dicozorus database
```bash
$ dicozorus stats
[+] Total count: 22376
[+] Entry count by criticality:
	Critical: 344
	High: 697
	Medium: 668
	Low: 1168
	Info: 4262
	Unranked: 15237
[+] Entry count by type:
	FILE: 12583
	DIRECTORY: 3449
	PATH: 6344
[+] Entry count by category:
	UNCATEGORIZED: 19499
	KNOWN_APP: 871
	RCE: 335
	INFO_LEAK: 280
[...]
```

## Contributing
### Custom CSV Format
If you want to contribute entries to the core lists or parse custom inputs natively, use the following quoted Comma-Separated Values (CSV) structure:

```
## path, criticality, count, category, tags, reference
"actions/authenticate.php","CRITICAL","1","RCE","PHP","https://nvd.nist.gov/vuln/detail/CVE-2020-35729"
```

### Adding an entry to the built-in wordlists
Here are a few rules when adding entries to the built-in wordlists:
- If the entry is **associated with a criticality** you can put it in one of the following files in dicozorus/data/ :
  - CRITICAL.wordlist
  - HIGH.wordlist
  - MEDIUM.wordlist
  - LOW.wordlist
- If the entry is not associated with any criticality, but the entry looks interesting **and generic** you can put it in the INFO.wordlist file.
  - Examples of generic interesting entries: `upload.php`, `admin.aspx`, `webshell.jsp`, `administration/`
- If the entry Criticality is LOW or above, you must add a reference to the CSV file
