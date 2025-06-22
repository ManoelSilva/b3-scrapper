import os
import shutil
import subprocess
from pathlib import Path
import sys


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def check_docker():
    try:
        subprocess.check_output(['docker', '--version'])
    except Exception:
        print('Docker not found! Install Docker for Lambda-compatible builds.')
        sys.exit(1)


BUILD_DIR = Path(__file__).parent
ROOT_DIR = BUILD_DIR.parent
SRC_DIR = ROOT_DIR / 'src'
REQUIREMENTS = ROOT_DIR / 'requirements.txt'
LAMBDA_ZIP = BUILD_DIR / 'lambda.zip'
LAYERS_DIR = BUILD_DIR / 'layers'

# 1. Ensure build and build/layers directories
ensure_dir(BUILD_DIR)
ensure_dir(LAYERS_DIR)

# List of dependencies already available in the Lambda runtime
LAMBDA_RUNTIME_PACKAGES = {
    'boto3', 'botocore', 'urllib3', 'six', 'python-dateutil',
    'jmespath', 's3transfer', 'docutils', 'pandas', 'pyarrow'
}

check_docker()

# 2. Create individual layers for each dependency
layer_zips = []
if REQUIREMENTS.exists():
    with open(REQUIREMENTS, 'r') as f:
        requirements = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

    for requirement in requirements:
        package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()

        if package_name.lower() in LAMBDA_RUNTIME_PACKAGES:
            print(f'Skipping {package_name} (already available in Lambda runtime)')
            continue

        print(f'Creating layer for {package_name}...')

        # Temporary directory for this layer
        layer_temp_dir = BUILD_DIR / f'layer_{package_name.lower().replace("-", "_")}'
        layer_python_dir = layer_temp_dir / 'python' / 'lib' / 'python3.12' / 'site-packages'

        # Clean directory if it exists
        if layer_temp_dir.exists():
            shutil.rmtree(layer_temp_dir)

        # Create layer directory
        ensure_dir(layer_python_dir)

        # Install only this dependency using Docker
        try:
            docker_cmd = [
                'docker', 'run', '--rm',
                '-v', f'{layer_python_dir.absolute()}:/var/task/python/lib/python3.12/site-packages',
                'public.ecr.aws/sam/build-python3.12',
                'pip', 'install', requirement, '-t', '/var/task/python/lib/python3.12/site-packages'
            ]
            subprocess.check_call(docker_cmd)

            # Create ZIP of the layer in build/layers folder
            layer_zip = LAYERS_DIR / f'layer_{package_name.lower().replace("-", "_")}.zip'
            if layer_zip.exists():
                layer_zip.unlink()

            shutil.make_archive(str(layer_zip)[:-4], 'zip', root_dir=layer_temp_dir)
            layer_zips.append(f'layers/{layer_zip.name}')
            print(f'Layer {package_name} created: layers/{layer_zip.name}')

        except subprocess.CalledProcessError as e:
            print(f'Error installing {package_name}: {e}')
        finally:
            # Clean temporary directory
            if layer_temp_dir.exists():
                shutil.rmtree(layer_temp_dir)
else:
    print('requirements.txt not found, skipping dependencies.')

# 3. Package only the Lambda code (without dependencies)
print(f'Packaging Lambda code into {LAMBDA_ZIP}...')
if LAMBDA_ZIP.exists():
    LAMBDA_ZIP.unlink()

shutil.make_archive(str(LAMBDA_ZIP)[:-4], 'zip', root_dir=SRC_DIR)

# 4. Summary
print('\n=== Build finished! ===')
print(f'Lambda ZIP: {LAMBDA_ZIP.name}')
if layer_zips:
    print('Created layers:')
    for layer in layer_zips:
        print(f'  - {layer}')
else:
    print('No layer created (all dependencies are already in the Lambda runtime)')
