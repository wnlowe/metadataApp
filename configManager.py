import configparser
import os
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # Define default templates for different section types
        self.section_templates = {
            'UI': {
                'Selected File': '',
                'Output Directory': '',
                'UCS Cat': 'False',
                'UCS List': 'False'
            },
            'Basic File': {
                'CatID': '',
                'Category': '',
                'SubCategory': '',
                'FX Name': '',
                'Creator ID': '',
                'User Category': '',
                'Vendor Category': '',
                'Source ID': '',
            },
            'Advanced File': {
                'Description': '',
                'Title': '',
                'Keywords': '',
                'Designer': '',
                'Microphone': '',
                'Recording Medium': '',
                'Microphone Configuration': '',
                'Microphone Perspective': '',
                'Inside or Outside': '',
                'Library': '',
                'URL': 'https://www.cleancuts.com',
                'Manufacturer': 'Clean Cuts',
                'Location': 'United States, Washington, DC',
                'Notes': ''
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file, create if doesn't exist"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            print(f"Loaded configuration from {self.config_file}")
        else:
            print(f"Config file {self.config_file} not found. Creating with default settings.")
            self.create_default_config()
    
    def create_default_config(self):
        """Create a default config file with basic sections"""
        # Add default sections
        # self.add_section('UI')
        # self.add_section('FileSettings')
        self.save_config()
    
    def add_section(self, section_name, template_type=None):
        """
        Add a new section with default template values
        
        Args:
            section_name: Name of the section to add
            template_type: Type of template to use (defaults to section_name)
        """
        if template_type is None:
            template_type = section_name
        
        if section_name in self.config:
            # print(f"Section '{section_name}' already exists!")
            return True
        
        if template_type not in self.section_templates:
            print(f"Template '{template_type}' not found. Available templates: {list(self.section_templates.keys())}")
            return False
        
        # Add section with template values
        self.config.add_section(section_name)
        template = self.section_templates[template_type]
        
        for key, value in template.items():
            self.config.set(section_name, key, value)
        
        print(f"Added section '{section_name}' with template '{template_type}'")
        return True
    
    def add_custom_section(self, section_name, custom_defaults=None):
        """
        Add a section with custom default values
        
        Args:
            section_name: Name of the section
            custom_defaults: Dictionary of key-value pairs for the section
        """
        if section_name in self.config:
            print(f"Section '{section_name}' already exists!")
            return False
        
        self.config.add_section(section_name)
        
        if custom_defaults:
            for key, value in custom_defaults.items():
                self.config.set(section_name, key, str(value))
        
        print(f"Added custom section '{section_name}'")
        return True
    
    def get_value(self, section, key, fallback=None):
        """Get a value from config with fallback"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def set_value(self, section, key, value):
        """Set a value in config"""
        if section not in self.config:
            print(f"Section '{section}' doesn't exist. Creating it first.")
            # self.add_section(section)
        
        
        self.config.set(section, key, str(value))
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def list_sections(self):
        """List all sections in config"""
        return self.config.sections()
    
    def list_section_items(self, section):
        """List all items in a section"""
        try:
            return dict(self.config.items(section))
        except configparser.NoSectionError:
            print(f"Section '{section}' not found")
            return {}
    
    # def add_template(self, template_name, template_dict):
    #     """Add a new template type"""
    #     self.section_templates[template_name] = template_dict
    #     print(f"Added template '{template_name}'")
    
    # def list_templates(self):
    #     """List available templates"""
    #     return list(self.section_templates.keys())
    
    def remove_section(self, section_name):
        """Remove a section from config"""
        if self.config.remove_section(section_name):
            print(f"Removed section '{section_name}'")
            return True
        else:
            print(f"Section '{section_name}' not found")
            return False


# # Example usage
# if __name__ == "__main__":
#     # Create config manager
#     config_mgr = ConfigManager("my_app_config.ini")
    
#     # Add sections using templates
#     config_mgr.add_section('MainUI', 'UI')  # Uses UI template
#     config_mgr.add_section('DatabaseConnection', 'Database')  # Uses Database template
#     config_mgr.add_section('ExportSettings', 'Export')  # Uses Export template
    
#     # Add custom section
#     custom_settings = {
#         'debug_mode': 'false',
#         'log_level': 'INFO',
#         'max_threads': '4'
#     }
#     config_mgr.add_custom_section('Advanced', custom_settings)
    
#     # Add a new template and use it
#     api_template = {
#         'base_url': 'https://api.example.com',
#         'timeout': '30',
#         'retries': '3',
#         'api_key': ''
#     }
#     config_mgr.add_template('API', api_template)
#     config_mgr.add_section('WeatherAPI', 'API')
    
#     # Set some values
#     config_mgr.set_value('MainUI', 'window_width', '1400')
#     config_mgr.set_value('DatabaseConnection', 'host', '192.168.1.100')
    
#     # Get values
#     width = config_mgr.get_value('MainUI', 'window_width', '1200')
#     print(f"Window width: {width}")
    
#     # List sections and templates
#     print(f"Sections: {config_mgr.list_sections()}")
#     print(f"Available templates: {config_mgr.list_templates()}")
    
#     # Save the configuration
#     config_mgr.save_config()
    
#     # Show section contents
#     print(f"MainUI settings: {config_mgr.list_section_items('MainUI')}")