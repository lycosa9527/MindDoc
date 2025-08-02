from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

def print_banner():
    """Display ASCII banner when application starts"""
    banner = """
================================================================================
    ███╗   ███╗██╗███╗   ██╗██████╗ ███╗   ███╗ █████╗ ████████╗███████╗
    ████╗ ████║██║████╗  ██║██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
    ██╔████╔██║██║██╔██╗ ██║██║  ██║██╔████╔██║███████║   ██║   █████╗  
    ██║╚██╔╝██║██║██║╚██╗██║██║  ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
    ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
================================================================================
                              MindDoc v0.1
                    Document Analysis & AI Assistant
                        Made by MindSpring Team
                           Author: lycosa9527
================================================================================
    """
    print(banner)

def print_startup_info():
    """Display startup information"""
    print("🔧 Application Configuration:")
    print("   • Environment: Development")
    print("   • Debug Mode: Enabled")
    print("   • Host: 0.0.0.0")
    print("   • Port: 5000")
    print("   • URL: http://localhost:5000")
    print()
    print("📋 Available Features:")
    print("   • Document upload (.docx files)")
    print("   • Real-time paragraph analysis")
    print("   • AI-powered writing suggestions")
    print("   • Live document editing")
    print("   • Download analyzed documents")
    print()
    print("🎯 Ready to analyze documents!")
    print("=" * 60)

if __name__ == '__main__':
    # Display banner
    print_banner()
    
    # Create and start application
    app = create_app()
    
    # Display startup info
    print_startup_info()
    
    # Start the server
    app.run(debug=True, host='0.0.0.0', port=5000) 