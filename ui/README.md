# Streamlit Frontend

Run the API first:

```bash
uvicorn api.main:app --reload
```

Then, in another terminal:

```bash
streamlit run app.py
```

The application opens a browser interface where users can describe their movie preferences in natural language and request recommendations.

The API URL can be changed from the sidebar.
