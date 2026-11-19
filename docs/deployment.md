# Deployment guide

## Current deployment status

The application is prepared for Streamlit Community Cloud, but it is **not yet publicly deployed**. Deployment requires the repository owner to sign in and authorize Streamlit Community Cloud through GitHub; the assistant cannot grant that OAuth permission on the owner's behalf.

## Free deployment path

Streamlit Community Cloud currently offers free app hosting. Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Connect/authorize the GitHub account that owns `davidwuphp-a11y/ai-financial-analyst`.
3. Choose **Create app** → **Yup, I have an app**.
4. Set repository to `davidwuphp-a11y/ai-financial-analyst`.
5. Set branch to `main` and entrypoint to `app.py`.
6. In Advanced settings, select Python 3.11.
7. Leave Secrets empty; the default Mock provider requires no API key.
8. Deploy.

The repository includes `.streamlit/config.toml` and `requirements.txt`. Subsequent commits to the selected branch are automatically reflected in the deployed app.

## Public demo safety

- Use the built-in public Apple sample or other public/synthetic data only.
- Do not configure real API keys for the public demo.
- Do not upload confidential, personal, material non-public, or restricted financial documents.
- Treat the hosted app as an experimental public prototype, not a production financial service.

## What remains after deployment

After Streamlit creates the app, copy its assigned `*.streamlit.app` URL into the GitHub repository's **About → Website** field and the profile README. Do not guess or publish a URL before the deployment succeeds.
