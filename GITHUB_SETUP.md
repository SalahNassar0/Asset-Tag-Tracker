# GitHub Repository Setup Guide

## 🔧 How to Set Up GitHub Integration

### Step 1: Create a Private Repository
1. Go to [GitHub.com](https://github.com) and create a new repository
2. Name it something like `asset-tag-tracker` or `my-asset-data`
3. Make it **Private** for security
4. Don't initialize with README (empty repo is fine)

### Step 2: Generate GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Asset Tracker"
4. Select these permissions:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### Step 3: Configure Your App
1. Copy `env_example.txt` to `.env`
2. Edit `.env` file:
   ```
   GITHUB_TOKEN=ghp_your_actual_token_here
   GITHUB_REPO=your-username/your-repo-name
   ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run the App
```bash
streamlit run app.py
```

## ✅ What Happens

- **First Run**: App creates the JSON files in your GitHub repo
- **Data Sync**: All your asset tags are stored in the cloud
- **Backup**: Your data is automatically backed up to GitHub
- **Access**: Use the same data from any computer
- **Fallback**: If GitHub is unavailable, it uses local storage

## 📁 Repository Structure
Your GitHub repo will contain:
```
├── assets.json          # All your asset tags
├── countries.json       # Country codes (EGY, KSA, etc.)
└── manufacturers.json   # Manufacturer codes (ZE, HP, etc.)
```

## 🔒 Security
- Repository is private (only you can see it)
- Token has minimal required permissions
- Data is encrypted in transit

## 🆘 Troubleshooting

**"GitHub connection failed"**
- Check your token is correct
- Verify repository name format: `username/repo-name`
- Ensure token has `repo` permissions

**"Repository not found"**
- Make sure the repository exists and is spelled correctly
- Check you have access to the repository

**"Authentication failed"**
- Token might be expired or revoked
- Generate a new token and update `.env`