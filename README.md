# GTM Engine — Hackathon MVP
Python 3.10+ recommended. From this directory:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Optional: set OPENAI_API_KEY and optionally OPENAI_MODEL for AI-generated ICPs. No key needed for template mode. API use may incur costs. Only product text is sent to the optional API.

Demo: approve advertising ICP, inspect ranked matches, explore graph, choose contact, edit/approve message, simulate send, inspect pipeline and audit. No real delivery. To demonstrate a stage change, select a lead currently Matched in the pipeline.

Limitations: synthetic/unverified data, no live research or citations, graph visualization from CSV not a native graph database, template outreach, historical pipeline is advertising-only, no durable session writes or bonus integrations. Other sector ICP templates are available but seed data is advertising only. This is a prototype, not full specification compliance. Deploy via Streamlit Community Cloud after uploading this directory to a GitHub repository; set secrets through host environment if using API. Never commit API keys.
