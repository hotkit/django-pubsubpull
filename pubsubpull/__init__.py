import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
_join_with_project_path = lambda a, *p: os.path.join(PROJECT_ROOT, a, *p)
