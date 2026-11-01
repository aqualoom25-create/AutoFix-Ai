@echo off
title AutoFix AI — 2013 Maruti Suzuki Alto 800 (F8D Petrol) Diagnostic SaaS
echo ===========================================================================
echo   AutoFix AI — Automotive Engineering ^& DIY Diagnostic SaaS (v1.0)
echo   Target Vehicle: 2013 Maruti Suzuki Alto 800 (0.8L F8D 12V MPFI Petrol)
echo   Dashboard URL:  http://localhost:8080
echo   API Docs URL:   http://localhost:8080/docs
echo ===========================================================================
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
