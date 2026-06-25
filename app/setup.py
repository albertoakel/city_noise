#setup.py
import sys
from pathlib import Path

def setup_path():
    # diretório atual (app/)
    current_dir = Path(__file__).resolve().parent

    # raiz do projeto
    project_root = current_dir.parent

    # adiciona no sys.path se ainda não estiver
    project_root_str = str(project_root)

    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)