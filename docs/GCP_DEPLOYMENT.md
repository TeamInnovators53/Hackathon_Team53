# Google Cloud Platform (GCP) & Firebase Deployment Guide
### Hackathon Team 53 • Team Innovators

This guide shows how to deploy the Key Privilege Voice & Chat Multi-Agent Bot so that everyone on your GCP project and hackathon team can access and interact with it from anywhere.

---

## ⚡ Option 1: Firebase Hosting (Recommended • Fastest 2-Minute Deploy)

Because we built a dual-mode engine (`web/agent_engine.js`), the entire Multi-Agent Bot, DTMF touch-tone generator, Voice synthesis, and Fee Avoidance Engine can run **100% serverless** on Firebase Hosting with zero server cost or backend maintenance.

### Steps to Deploy:
1. In your terminal, ensure you are in the project folder:
   ```bash
   cd "C:\Users\SINGAPO\OneDrive - Key Corp\Desktop\TeamInnovators\Hackathon_Team53"
   ```

2. Login to your GCP / Firebase account:
   ```bash
   npx firebase-tools login
   ```

3. Link to your GCP Project ID:
   ```bash
   npx firebase-tools use <YOUR_GCP_PROJECT_ID>
   ```
   *(e.g., `npx firebase-tools use my-hackathon-team53-project`)*

4. Deploy directly to Firebase Hosting:
   ```bash
   npx firebase-tools deploy --only hosting
   ```

5. **Done!** Firebase will output your team's live URL:
   ```
   Hosting URL: https://<YOUR_GCP_PROJECT_ID>.web.app
   ```
   Share this URL with all team members and hackathon judges!

---

## 🚀 Option 2: Google Cloud Run (Full Container Deployment)

If you want the Python backend server (`run_server.py`) and REST APIs running inside a container on Google Cloud:

### Steps to Deploy:
1. Ensure your Google Cloud SDK is authenticated:
   ```bash
   gcloud auth login
   gcloud config set project <YOUR_GCP_PROJECT_ID>
   ```

2. Deploy directly from source (Cloud Run automatically builds the included `Dockerfile`):
   ```bash
   gcloud run deploy key-privilege-bot \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080
   ```

3. **Done!** Cloud Run provides your live service URL:
   ```
   Service URL: https://key-privilege-bot-xxxxxx-uc.a.run.app
   ```

---

## 🪣 Option 3: Google Cloud Storage (Bucket Static Web Hosting)

If you prefer to host via a GCP Cloud Storage bucket:
1. Create a bucket or use an existing one:
   ```bash
   gsutil mb -c STANDARD -l us-central1 gs://key-privilege-bot-team53/
   ```
2. Upload the `web/` directory:
   ```bash
   gsutil -m cp -r web/* gs://key-privilege-bot-team53/
   ```
3. Set the web configuration and public read permissions:
   ```bash
   gsutil web set -m index.html gs://key-privilege-bot-team53
   gsutil iam ch allUsers:objectViewer gs://key-privilege-bot-team53
   ```
4. Access via: `https://storage.googleapis.com/key-privilege-bot-team53/index.html`
