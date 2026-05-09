# SpekGen Ops — Claude Instructions

This repo contains automation scripts for SpekGen agency (Pedro Lopez + Gibran Alonzo, La Paz MX).

## Agency OS
Full agency OS lives in Google Drive Shared Drive (`SPK - SPEKGEN AGENCY`), owned by gibran.alonzo0506@gmail.com.
Read `_SPEKGEN_OS.md` (Drive ID: `1qhVh5KgBWJlw7ReTT6BqGOqDygbvrzHt`) before any session.

## Critical Rules
- NEVER commit `.env` files — credentials stay local only
- NEVER read or expose token values in responses
- Scripts download files from Drive via API — no FUSE mounts
- All client data files live in Drive, not in this repo

## Scripts
- `spekgen_morning_intelligence.py` — daily 8am report (Meta ads + ClickUp + Narrative Memo)

## Setup
1. Copy `.env.example` to `.env` and fill in credentials
2. `pip install -r requirements.txt`
3. `python spekgen_morning_intelligence.py --dry-run`

## Drive IDs to fill in (ask Gibran)
- `PLACEHOLDER_LF_ENV_DRIVE_ID` — LO FITNESS `.env` file in Drive
- `PLACEHOLDER_GR_ENV_DRIVE_ID` — GREENRAY `.env` file in Drive
- `PLACEHOLDER_HC_ENV_DRIVE_ID` — HEALTHY CHUCHOS `.env` file in Drive
- `PLACEHOLDER_SPEKGEN_CLIENTS_AD_LOG_DRIVE_ID` — unified AD LOG xlsx
- `PLACEHOLDER_REPORTS_FOLDER_DRIVE_ID` — morning-intelligence/reports/ folder
- `PLACEHOLDER_HC_CLICKUP_LIST_ID` — HC ClickUp list ID
- `PLACEHOLDER_F24_CLICKUP_LIST_ID` — F24 ClickUp list ID
