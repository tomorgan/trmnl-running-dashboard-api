# Azure Deployment Guide

## Prerequisites

1. Azure subscription
2. GitHub repository (already have it!)
3. Azure CLI installed (optional, can use Azure Portal)

## Step 1: Create Azure Function App

### Option A: Using Azure Portal (Recommended)

1. Go to https://portal.azure.com
2. Click **"Create a resource"**
3. Search for **"Function App"** and click Create

**Configuration:**
- **Subscription**: Your Azure subscription
- **Resource Group**: Create new or use existing (e.g., `running-dashboard-rg`)
- **Function App name**: Choose a unique name (e.g., `trmnl-running-api-<yourname>`)
  - This will be your URL: `https://trmnl-running-api-<yourname>.azurewebsites.net`
- **Runtime stack**: Python
- **Version**: 3.11
- **Region**: Choose closest to you (e.g., UK South, East US)
- **Operating System**: Linux
- **Plan type**: Consumption (Serverless)

4. Click **"Review + create"** then **"Create"**
5. Wait for deployment to complete (~2 minutes)

### Option B: Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name running-dashboard-rg --location uksouth

# Create storage account (required for Functions)
az storage account create \
  --name trmnlrunningstorage \
  --resource-group running-dashboard-rg \
  --location uksouth \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --name trmnl-running-api-yourname \
  --resource-group running-dashboard-rg \
  --storage-account trmanlrunningstorage \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --consumption-plan-location uksouth
```

## Step 2: Get Publish Profile

1. In Azure Portal, go to your Function App
2. Click **"Get publish profile"** (top menu)
3. This downloads a `.publishsettings` XML file
4. Open the file in a text editor and **copy all contents**

## Step 3: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**

**Add this secret:**
- Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
- Value: Paste the entire contents of the publish profile file
- Click **"Add secret"**

## Step 4: Update GitHub Action Workflow

Edit `.github/workflows/azure-deploy.yml`:

```yaml
env:
  AZURE_FUNCTIONAPP_NAME: 'trmnl-running-api-yourname'  # ⬅️ Change this to your Function App name
```

Commit and push:
```bash
git add .github/workflows/azure-deploy.yml
git commit -m "Update Function App name in workflow"
git push
```

## Step 5: Configure Environment Variables in Azure

In Azure Portal → Your Function App → **Configuration** → **Application settings**

Add these variables:

| Name | Value |
|------|-------|
| `STRAVA_CLIENT_ID` | `your_strava_client_id` |
| `STRAVA_CLIENT_SECRET` | `your_strava_client_secret` |
| `STRAVA_REFRESH_TOKEN` | `your_strava_refresh_token` |
| `OPENWEATHER_API_KEY` | `your_openweather_api_key` |
| `WEATHER_LAT` | `51.507351` (your latitude) |
| `WEATHER_LON` | `-0.127758` (your longitude) |
| `NEXT_EVENT_NAME` | `Your Event Name` |
| `NEXT_EVENT_DATE` | `2026-04-26` |
| `TRAINING_SCHEDULE` | `[{"weeks_until": 16, "target_miles": 15}, {"weeks_until": 12, "target_miles": 20}, {"weeks_until": 8, "target_miles": 25}, {"weeks_until": 6, "target_miles": 28}, {"weeks_until": 4, "target_miles": 30}, {"weeks_until": 2, "target_miles": 20}, {"weeks_until": 1, "target_miles": 10}]` |
| `WEEKLY_PLAN` | `[{"day": "Monday", "workout": "Rest day"}, {"day": "Tuesday", "workout": "Easy 5 miles"}, {"day": "Wednesday", "workout": "Tempo 6 miles"}, {"day": "Thursday", "workout": "Easy 4 miles"}, {"day": "Friday", "workout": "Rest day"}, {"day": "Saturday", "workout": "Long run 10 miles"}, {"day": "Sunday", "workout": "Recovery 3 miles"}]` |

Click **"Save"** at the top.

## Step 6: Deploy!

### Manual Deployment (First Time)

Push any commit to trigger the workflow:

```bash
git add .
git commit -m "Trigger initial deployment"
git push
```

### Monitor Deployment

1. Go to your GitHub repo → **Actions** tab
2. You'll see the workflow running
3. Click on it to see progress
4. Deployment takes ~3-5 minutes

### Verify Deployment

Once complete, test your API:

```bash
# Health check
curl https://your-function-app-name.azurewebsites.net/api/health

# Running data
curl https://your-function-app-name.azurewebsites.net/api/running-data
```

## Step 7: Future Updates

Now whenever you push to `main` branch:
1. GitHub Actions automatically runs
2. Code is deployed to Azure
3. Your API updates within ~3-5 minutes

**That's it!** 🎉

## Troubleshooting

### Deployment fails

1. Check **Actions** tab for error messages
2. Verify publish profile secret is set correctly
3. Check Function App name in workflow matches Azure

### API returns errors

1. Azure Portal → Your Function App → **Log stream**
2. Check Application Settings are configured
3. Verify all environment variables are set

### Strava authentication fails

1. Verify `STRAVA_REFRESH_TOKEN` hasn't expired
2. Check all three Strava variables are set
3. May need to re-run OAuth setup and update token

## Enable CORS (For TRMNL)

If TRMNL can't access your API:

1. Azure Portal → Your Function App → **CORS**
2. Add allowed origin: `https://usetrmnl.com`
3. Or use `*` to allow all (less secure)
4. Click **Save**

## Cost

**Consumption Plan (Serverless):**
- First 1 million executions: **FREE**
- After that: ~$0.20 per million executions
- Storage: ~$0.02/month

**Expected cost for this app: $0/month** (well within free tier)

## Monitoring

View logs and metrics:
- Azure Portal → Your Function App → **Monitor**
- Set up Application Insights for detailed tracking (optional)

---

**Ready?** Let's create your Azure Function App and deploy!
