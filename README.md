# Calculator Încărcare Țeavă HDPE

Aplicație web pentru optimizarea încărcării țevilor HDPE în camioane de transport.

## Structura Proiectului

```
TLC4Pipe/
├── docs/          # Documentație
├── backend/       # Backend Python (FastAPI)
├── frontend/      # Frontend React
├── shared/        # Resurse partajate
├── scripts/       # Scripturi utilitate
├── docker/        # Containerizare
└── .github/       # GitHub Actions CI/CD
```

## Funcționalități Principale

- **Telescopare țevi** (nesting) - optimizare spațiu prin introducerea țevilor mici în cele mari
- **Calcul încărcare** - algoritmi Bin Packing și First Fit Decreasing
- **Vizualizare 3D** - reprezentare grafică a încărcării camioanelor
- **Conformitate legală** - verificare limite greutate și distribuție sarcină pe axe
- **Generare rapoarte** - PDF cu instrucțiuni de încărcare

## Tehnologii

- **Backend**: Python, FastAPI, PostgreSQL, OR-Tools
- **Frontend**: React, Three.js, Redux
- **Infrastructură**: Docker, GitHub Actions

## Dezvoltare

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Licență

Proprietar
