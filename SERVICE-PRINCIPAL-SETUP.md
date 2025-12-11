# Creating Service Principal for GitHub Actions

The `functions-action` has issues with newer Azure setups. Since manual `func` deployment works, we'll use Azure CLI authentication instead.

## Step 1: Create Service Principal

Run this in your local PowerShell:

```powershell
# Login to Azure
az login

# Get your subscription ID
az account show --query id -o tsv

# Create service principal (replace SUBSCRIPTION_ID with output from above)
az ad sp create-for-rbac --name "github-trmnl-running-api" `
  --role contributor `
  --scopes /subscriptions/SUBSCRIPTION_ID/resourceGroups/YOUR_RESOURCE_GROUP/providers/Microsoft.Web/sites/trmnl-running-api `
  --sdk-auth
```

This will output JSON like:
```json
{
  "clientId": "xxxxx",
  "clientSecret": "xxxxx", 
  "subscriptionId": "xxxxx",
  "tenantId": "xxxxx"
}
```

## Step 2: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AZURE_CLIENT_ID` - from clientId
- `AZURE_CLIENT_SECRET` - from clientSecret  
- `AZURE_SUBSCRIPTION_ID` - from subscriptionId
- `AZURE_TENANT_ID` - from tenantId

## Step 3: Deploy

Push to trigger deployment - it will use Service Principal authentication which is more reliable than publish profiles.

---

**OR** we can keep it simple and just rely on manual deployment for now since that works!
