---
name: iss-prescription
description: Automate prescription renewal requests (ordinary and repetitive) and track request status on the ISS (Istituto per la Sicurezza Sociale) San Marino online portal.
---

# ISS San Marino - Prescription Renewal Skill

This skill automates the generation and submission of medical prescription renewal requests for the ISS (Istituto per la Sicurezza Sociale) San Marino online portal (`https://servizionline.iss.sm/#new-1`).

## Safety First
By default, the CLI operates in **DRY-RUN** mode. It displays the formatted summary and JSON payload without sending any submission request to the ISS server. The request is only transmitted when `--submit` is explicitly specified.

---

## Configuration & Environment Variables

Following the repository standard (`ADD_SKILL_RULES.md`), all patient credentials and settings are read **strictly from system environment variables**:

| Variable | Description | Example / Format | Required |
|---|---|---|:---:|
| `ISS_CODE` | Patient ISS code (1-7 numeric digits) | `121030` | Yes |
| `ISS_FIRST_NAME` | Patient first name | `Michele` | Yes |
| `ISS_LAST_NAME` | Patient last name | `Capicchioni` | Yes |
| `ISS_BIRTH_DATE` | Patient birth date | `19/05/1995` | Yes |
| `ISS_PHONE` | Patient phone number | `+39 338 77 91 592` | Yes |
| `ISS_EMAIL` | Patient email address for updates | `capimichi@gmail.com` | Optional |
| `ISS_DOCTOR` | Assigned primary care doctor name or ID | `Milena Cannuccia` or `Cannuccia` | Yes |

### Resolution Order:
1. CLI parameter (e.g. `--doctor "Milena Cannuccia"`)
2. Environment variable (`ISS_*`)

---

## Dynamic Doctor Resolution

Doctor IDs are not hardcoded. The CLI connects to `servizionline.iss.sm` at runtime, reads the live list of primary care doctors, and matches the requested doctor name (case-insensitive, partial matching allowed). If the ISS management system changes the internal IDs in the future, the script adapts dynamically without requiring code changes.

---

## CLI Usage

The CLI helper is located at `$USER_SKILLS_DIR/iss/prescription/cli.py` and runs with Python:

```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py <command> [options]
```

### 1. List Available Doctors
Fetch live list of doctors and assigned clinics (Borgo Maggiore, Murata, Serravalle):

```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py doctors
```
Filter doctors:
```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py doctors --search "Cannuccia"
```

### 2. Request Prescription Renewal

#### Dry Run (Default - Safe Preview):
```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py request \
  --medications "Tachipirina 1000 - 1 bustina al bisogno (max 3/die)" \
  --type ordinary
```

For repetitive prescriptions:
```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py request \
  --medications "Cardioaspirina 100mg - 1 compressa al giorno" \
  --type repetitive
```

#### Actual Live Submission (`--submit`):
```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py request \
  --medications "Tachipirina 1000 - 1 bustina al bisogno" \
  --type ordinary \
  --submit
```
On success, the CLI outputs the unique tracking code (Request ID).

### 3. Check Request Status
Track whether a submitted request is pending, completed, or cancelled:

```bash
python3 $USER_SKILLS_DIR/iss/prescription/cli.py status --request-id "<REQUEST_ID>"
```
