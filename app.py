import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import qrcode
from PIL import Image
import io
import base64
from github import Github
from github import Auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AssetTracker:
    def __init__(self):
        # Try to get from Streamlit secrets first, then environment variables
        try:
            self.github_token = st.secrets["GITHUB_TOKEN"]
            self.repo_name = st.secrets["GITHUB_REPO"]
            # Debug: Show that secrets were found
            st.info(f"🔑 Found secrets: Token starts with {self.github_token[:10]}...")
        except (KeyError, FileNotFoundError) as e:
            # Fallback to environment variables
            self.github_token = os.getenv('GITHUB_TOKEN')
            self.repo_name = os.getenv('GITHUB_REPO', 'your-username/asset-tracker')
            # Debug: Show that falling back to env vars
            st.warning(f"⚠️ Secrets not found, using env vars: {str(e)}")
        self.data_file = 'assets.json'
        self.manufacturers_file = 'manufacturers.json'
        self.countries_file = 'countries.json'
        
        # Initialize GitHub connection
        if self.github_token:
            try:
                auth = Auth.Token(self.github_token)
                self.github = Github(auth=auth)
                self.repo = self.github.get_repo(self.repo_name)
                self.use_github = True
                st.success("🔗 Connected to GitHub repository")
            except Exception as e:
                st.warning(f"⚠️ GitHub connection failed: {str(e)}. Using local storage.")
                self.github = None
                self.repo = None
                self.use_github = False
        else:
            st.info("💾 Using local storage (no GitHub token found)")
            self.github = None
            self.repo = None
            self.use_github = False
        
        # Create data directory for local storage
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def load_data_from_github(self, filename):
        """Load data from GitHub repository"""
        if not self.repo:
            return []
        
        try:
            file_content = self.repo.get_contents(filename)
            data = json.loads(file_content.decoded_content.decode())
            return data
        except:
            return []
    
    def save_data_to_github(self, filename, data):
        """Save data to GitHub repository"""
        if not self.repo:
            return False
        
        try:
            # Check if file exists
            try:
                file_content = self.repo.get_contents(filename)
                # Update existing file
                self.repo.update_file(
                    filename,
                    f"Update {filename}",
                    json.dumps(data, indent=2),
                    file_content.sha
                )
            except:
                # Create new file
                self.repo.create_file(
                    filename,
                    f"Create {filename}",
                    json.dumps(data, indent=2)
                )
            return True
        except Exception as e:
            st.error(f"Error saving to GitHub: {str(e)}")
            return False
    
    def load_data_from_file(self, filename):
        """Load data from local file"""
        filepath = os.path.join('data', filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")
            return []
    
    def save_data_to_file(self, filename, data):
        """Save data to local file"""
        filepath = os.path.join('data', filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving {filename}: {str(e)}")
            return False
    
    def load_assets(self):
        """Load assets from GitHub or local file"""
        if self.use_github:
            return self.load_data_from_github(self.data_file)
        else:
            return self.load_data_from_file(self.data_file)
    
    def load_manufacturers(self):
        """Load manufacturers from GitHub or local file"""
        if self.use_github:
            manufacturers = self.load_data_from_github(self.manufacturers_file)
        else:
            manufacturers = self.load_data_from_file(self.manufacturers_file)
            
        if not manufacturers:
            # Default manufacturers
            manufacturers = [
                {"code": "ZE", "name": "Zebra Electronics"},
                {"code": "HP", "name": "Hewlett Packard"},
                {"code": "DE", "name": "Dell"},
                {"code": "LE", "name": "Lenovo"},
                {"code": "AP", "name": "Apple"}
            ]
        return manufacturers
    
    def load_countries(self):
        """Load countries from GitHub or local file"""
        if self.use_github:
            countries = self.load_data_from_github(self.countries_file)
        else:
            countries = self.load_data_from_file(self.countries_file)
            
        if not countries:
            # Default countries
            countries = [
                {"code": "EGY", "name": "Egypt"},
                {"code": "KSA", "name": "Saudi Arabia"}
            ]
        return countries
    
    def save_assets(self, assets):
        """Save assets to GitHub and local file"""
        success = True
        if self.use_github:
            success = self.save_data_to_github(self.data_file, assets)
        success = self.save_data_to_file(self.data_file, assets) and success
        return success
    
    def save_manufacturers(self, manufacturers):
        """Save manufacturers to GitHub and local file"""
        success = True
        if self.use_github:
            success = self.save_data_to_github(self.manufacturers_file, manufacturers)
        success = self.save_data_to_file(self.manufacturers_file, manufacturers) and success
        return success
    
    def save_countries(self, countries):
        """Save countries to GitHub and local file"""
        success = True
        if self.use_github:
            success = self.save_data_to_github(self.countries_file, countries)
        success = self.save_data_to_file(self.countries_file, countries) and success
        return success
    
    def generate_asset_tag(self, country_code, manufacturer_code, assets):
        """Generate next sequential asset tag"""
        # Find existing assets with same country and manufacturer
        existing_assets = [asset for asset in assets 
                          if asset.get('country_code') == country_code 
                          and asset.get('manufacturer_code') == manufacturer_code]
        
        if not existing_assets:
            next_number = 1
        else:
            # Extract numbers from existing tags
            numbers = []
            for asset in existing_assets:
                tag = asset.get('tag', '')
                if '-' in tag:
                    try:
                        number = int(tag.split('-')[-1])
                        numbers.append(number)
                    except:
                        pass
            
            next_number = max(numbers) + 1 if numbers else 1
        
        return f"{country_code}-{manufacturer_code}-{next_number:04d}"
    
    def generate_qr_code(self, tag):
        """Generate QR code for asset tag"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(tag)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to bytes for Streamlit
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

def import_existing_tags(tracker, assets, pasted_tags):
    """Import existing asset tags from pasted text"""
    try:
        # Split by lines and clean up
        tag_lines = [line.strip() for line in pasted_tags.split('\n') if line.strip()]
        
        imported_count = 0
        for tag_line in tag_lines:
            # Parse tag format: COUNTRY-MANUFACTURER-NUMBER
            if '-' in tag_line and len(tag_line.split('-')) == 3:
                parts = tag_line.split('-')
                country_code = parts[0].strip()
                manufacturer_code = parts[1].strip()
                tag_number = parts[2].strip()
                
                # Check if tag already exists
                if not any(asset['tag'] == tag_line for asset in assets):
                    # Create asset entry
                    new_asset = {
                        "tag": tag_line,
                        "country_code": country_code,
                        "manufacturer_code": manufacturer_code,
                        "name": f"Imported Asset {tag_number}",
                        "date_created": datetime.now().isoformat()
                    }
                    assets.append(new_asset)
                    imported_count += 1
        
        if imported_count > 0:
            # Save to file
            return tracker.save_assets(assets)
        else:
            return False
            
    except Exception as e:
        st.error(f"Error importing tags: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="Asset Tag Generator",
        page_icon="🏷️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize tracker
    if 'tracker' not in st.session_state:
        st.session_state.tracker = AssetTracker()
    
    tracker = st.session_state.tracker
    
    # Load data
    assets = tracker.load_assets()
    manufacturers = tracker.load_manufacturers()
    countries = tracker.load_countries()
    
    st.title("🏷️ Asset Tag Generator")
    st.markdown("Generate and manage asset tags for your Snipe-IT inventory")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["Generate Tags", "Manage Lists", "Recent Tags"])
    
    with tab1:
        show_tag_generator(tracker, assets, manufacturers, countries)
    
    with tab2:
        show_manage_lists(tracker, manufacturers, countries)
    
    with tab3:
        show_recent_tags(assets)
    
    # Import section in sidebar
    with st.sidebar:
        st.subheader("Import Previous Tags")
        with st.expander("Add Existing Asset Tags"):
            st.markdown("**Paste your existing asset tags here:**")
            st.markdown("*Format: one tag per line*")
            st.markdown("*Example:*")
            st.code("EGY-ZE-0001\nEGY-ZE-0002\nKSA-DE-0001")
            
            pasted_tags = st.text_area(
                "Asset Tags",
                placeholder="EGY-ZE-0001\nEGY-ZE-0002\nKSA-DE-0001",
                height=100
            )
            
            if st.button("Import Tags", type="secondary"):
                if pasted_tags:
                    import_result = import_existing_tags(tracker, assets, pasted_tags)
                    if import_result:
                        st.success("Tags imported successfully!")
                        st.rerun()
                    else:
                        st.error("Some tags could not be imported. Check the format.")

def show_tag_generator(tracker, assets, manufacturers, countries):
    st.subheader("Generate Asset Tags")
    
    with st.form("tag_generator_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            country_options = {f"{c['code']} - {c['name']}": c['code'] for c in countries}
            country_code = st.selectbox(
                "Country",
                options=list(country_options.keys()),
                help="Select the country for this asset"
            )
            country_code = country_options[country_code]
        
        with col2:
            manufacturer_options = {f"{m['code']} - {m['name']}": m['code'] for m in manufacturers}
            manufacturer_code = st.selectbox(
                "Manufacturer",
                options=list(manufacturer_options.keys()),
                help="Select the manufacturer for this asset"
            )
            manufacturer_code = manufacturer_options[manufacturer_code]
        
        with col3:
            num_tags = st.number_input(
                "Number of Tags",
                min_value=1,
                max_value=100,
                value=1,
                help="How many tags to generate"
            )
        
        asset_name = st.text_input(
            "Asset Name", 
            placeholder="e.g., Zebra Printer, Dell Laptop",
            help="Enter a descriptive name for the asset"
        )
        
        generate_btn = st.form_submit_button("Generate Tags", type="primary")
        
        if generate_btn:
            if not asset_name:
                st.error("Please enter an asset name")
            else:
                # Generate multiple tags
                generated_tags = []
                current_assets = assets.copy()
                
                for i in range(num_tags):
                    tag = tracker.generate_asset_tag(country_code, manufacturer_code, current_assets)
                    generated_tags.append(tag)
                    current_assets.append({
                        "tag": tag,
                        "country_code": country_code,
                        "manufacturer_code": manufacturer_code,
                        "name": f"{asset_name} #{i+1}",
                        "date_created": datetime.now().isoformat()
                    })
                
                # Store in session state for saving
                st.session_state.generated_tags = generated_tags
                st.session_state.asset_data_list = current_assets[len(assets):]  # Only new assets
                
                st.success(f"Generated {len(generated_tags)} tags!")
                
                # Show generated tags
                for i, tag in enumerate(generated_tags):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.code(tag)
                    with col2:
                        st.write(f"**{asset_name} #{i+1}**")
    
    # Save/Cancel buttons (outside form)
    if 'generated_tags' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save All Tags", type="primary", help="Save all generated tags to your inventory"):
                assets.extend(st.session_state.asset_data_list)
                if tracker.save_assets(assets):
                    st.success(f"Saved {len(st.session_state.asset_data_list)} asset tags successfully!")
                    # Clear session state
                    del st.session_state.generated_tags
                    del st.session_state.asset_data_list
                    st.rerun()
                else:
                    st.error("Failed to save asset tags")
        
        with col2:
            if st.button("Cancel", help="Discard generated tags"):
                del st.session_state.generated_tags
                del st.session_state.asset_data_list
                st.rerun()

def show_manage_lists(tracker, manufacturers, countries):
    st.subheader("Manage Countries and Manufacturers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Countries")
        
        # Add new country
        with st.expander("Add New Country"):
            with st.form("add_country"):
                new_country_code = st.text_input("Country Code", placeholder="e.g., EGY", max_chars=5).upper()
                new_country_name = st.text_input("Country Name", placeholder="e.g., Egypt")
                if st.form_submit_button("Add Country"):
                    if new_country_code and new_country_name:
                        if any(c['code'] == new_country_code for c in countries):
                            st.error("Country code already exists")
                        else:
                            countries.append({"code": new_country_code, "name": new_country_name})
                            if tracker.save_countries(countries):
                                st.success("Country added!")
                                st.rerun()
        
        # Display and edit countries
        st.write("**Current Countries:**")
        if countries:
            for country in countries:
                with st.container():
                    country_col1, country_col2, country_col3 = st.columns([1, 2, 1])
                    with country_col1:
                        st.code(country['code'])
                    with country_col2:
                        st.write(country['name'])
                    with country_col3:
                        if st.button("Remove", key=f"remove_country_{country['code']}"):
                            countries.remove(country)
                            if tracker.save_countries(countries):
                                st.success("Country removed!")
                                st.rerun()
        else:
            st.info("No countries found")
    
    with col2:
        st.subheader("Manufacturers")
        
        # Add new manufacturer
        with st.expander("Add New Manufacturer"):
            with st.form("add_manufacturer"):
                new_man_code = st.text_input("Manufacturer Code", placeholder="e.g., ZE", max_chars=5).upper()
                new_man_name = st.text_input("Manufacturer Name", placeholder="e.g., Zebra Electronics")
                if st.form_submit_button("Add Manufacturer"):
                    if new_man_code and new_man_name:
                        if any(m['code'] == new_man_code for m in manufacturers):
                            st.error("Manufacturer code already exists")
                        else:
                            manufacturers.append({"code": new_man_code, "name": new_man_name})
                            if tracker.save_manufacturers(manufacturers):
                                st.success("Manufacturer added!")
                                st.rerun()
        
        # Display and edit manufacturers
        st.write("**Current Manufacturers:**")
        if manufacturers:
            for manufacturer in manufacturers:
                with st.container():
                    man_col1, man_col2, man_col3 = st.columns([1, 2, 1])
                    with man_col1:
                        st.code(manufacturer['code'])
                    with man_col2:
                        st.write(manufacturer['name'])
                    with man_col3:
                        if st.button("Remove", key=f"remove_manufacturer_{manufacturer['code']}"):
                            manufacturers.remove(manufacturer)
                            if tracker.save_manufacturers(manufacturers):
                                st.success("Manufacturer removed!")
                                st.rerun()
        else:
            st.info("No manufacturers found")

def show_recent_tags(assets):
    st.subheader("Recent Asset Tags")
    
    if not assets:
        st.info("No asset tags yet. Generate your first one!")
        return
    
    # Show last 10 tags
    recent_assets = sorted(assets, key=lambda x: x.get('date_created', ''), reverse=True)[:10]
    
    for asset in recent_assets:
        with st.container():
            st.code(asset.get('tag', ''))
            st.write(f"**{asset.get('name', '')}**")
            st.caption(f"{asset.get('country_code', '')}-{asset.get('manufacturer_code', '')} • {asset.get('date_created', '')[:10]}")
            st.divider()
    
    # Quick stats
    st.subheader("Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tags", len(assets))
    with col2:
        unique_countries = len(set(asset.get('country_code', '') for asset in assets))
        st.metric("Countries", unique_countries)

if __name__ == "__main__":
    main()