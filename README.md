# 🏷️ Asset Tag Tracker

A modern Streamlit application for managing asset tags with GitHub integration for data persistence and collaboration.

## Features

- **Automatic Tag Generation**: Creates sequential asset tags in format `EG-ZE-00001` (Country-Manufacturer-SequentialNumber)
- **GitHub Integration**: Stores all data in a private GitHub repository
- **QR Code Generation**: Automatically generates QR codes for each asset tag
- **Modern UI**: Clean, responsive interface built with Streamlit
- **Data Analytics**: Charts and reports for asset management insights
- **Import/Export**: Backup and restore functionality
- **Team Collaboration**: Multiple users can access and update the same data

## Setup

### 1. Prerequisites

- Python 3.8+
- GitHub account
- Git

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd asset-tracker

# Install dependencies
pip install -r requirements.txt
```

### 3. GitHub Setup

1. **Create a private GitHub repository** for your asset data
2. **Generate a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate new token with `repo` permissions
   - Copy the token

3. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your values
   GITHUB_TOKEN=your_github_token_here
   GITHUB_REPO=your-username/asset-tracker
   ```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### Adding Assets

1. Go to "Add Asset" in the sidebar
2. Select country code and manufacturer
3. Enter asset name and description
4. Click "Generate Asset Tag" to create the tag
5. Save the asset to store it in GitHub

### Managing Manufacturers

1. Go to "Manage Manufacturers"
2. Add new manufacturers with custom codes
3. Remove manufacturers you no longer need

### Viewing Assets

1. Go to "View Assets" to see all your assets
2. Use search and filters to find specific assets
3. Click on any asset to see details and QR code

### Reports

1. Go to "Reports" for analytics and insights
2. View charts showing asset distribution
3. Export data to CSV for external analysis

## Data Structure

Assets are stored as JSON in your GitHub repository:

```json
{
  "tag": "EG-ZE-00001",
  "country_code": "EG",
  "manufacturer_code": "ZE", 
  "name": "Laptop",
  "description": "Dell Latitude 5520",
  "date_created": "2024-01-15T10:30:00"
}
```

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set environment variables in the Streamlit Cloud dashboard
5. Deploy!

### Other Platforms

The app can be deployed to any platform that supports Python:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS/GCP/Azure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details