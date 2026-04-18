#!/usr/bin/env python3
"""
build_package.py - Build and optionally install the PegaRE package

This script helps you build the PegaRE package for distribution or local installation.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr.strip()}")
        return False


def clean_build():
    """Clean previous build artifacts."""
    import shutil
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"🧹 Removing {path}")
                shutil.rmtree(path)
            else:
                path.unlink()


def build_package(clean=True):
    """Build the package distribution."""
    if clean:
        clean_build()
    
    print("📦 Building PegaRE package...")
    
    # Build source distribution and wheel
    if not run_command("python -m build", "Building package"):
        return False
    
    print("✅ Package built successfully!")
    print("\nGenerated files:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"   📄 {file}")
    
    return True


def install_package(install_mode="dev"):
    """Install the package."""
    if install_mode == "dev":
        # Editable development install
        cmd = "pip install -e ."
        description = "Installing in development mode (editable)"
    else:
        # Regular install
        cmd = "pip install ."
        description = "Installing package"
    
    return run_command(cmd, description)


def install_from_dist():
    """Install from built distribution."""
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))
    
    if not wheel_files:
        print("❌ No wheel file found in dist/. Run --build first.")
        return False
    
    wheel_file = wheel_files[0]  # Use the first wheel file
    cmd = f"pip install {wheel_file}"
    return run_command(cmd, f"Installing from {wheel_file}")


def check_dependencies():
    """Check if build dependencies are available."""
    try:
        import build
        return True
    except ImportError:
        print("❌ Build dependencies not found. Install with:")
        print("   pip install build")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Build and install PegaRE package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_package.py --build                 # Just build the package
  python build_package.py --build --install       # Build and install in development mode
  python build_package.py --install-dist          # Install from pre-built dist/
  python build_package.py --clean                 # Just clean build artifacts
        """
    )
    
    parser.add_argument("--build", action="store_true", help="Build the package")
    parser.add_argument("--install", action="store_true", help="Install in development mode (editable)")
    parser.add_argument("--install-prod", action="store_true", help="Install in production mode")
    parser.add_argument("--install-dist", action="store_true", help="Install from built distribution")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--no-clean", action="store_true", help="Don't clean before building")
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 0
    
    success = True
    
    # Clean only
    if args.clean and not args.build:
        clean_build()
        print("✅ Build artifacts cleaned")
        return 0
    
    # Check dependencies if building
    if args.build and not check_dependencies():
        return 1
    
    # Build package
    if args.build:
        success = build_package(clean=not args.no_clean)
        if not success:
            return 1
    
    # Install package
    if args.install:
        success = install_package("dev")
    elif args.install_prod:
        success = install_package("prod")
    elif args.install_dist:
        success = install_from_dist()
    
    if success and (args.install or args.install_prod or args.install_dist):
        print("\n✅ Installation completed!")
        print("\nYou can now use:")
        print("   pegare 'analyze my application' --input /path/to/jars")
        print("   python -c 'from pega_re import PegaAnalyzer; print(\"Import successful!\")'")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
