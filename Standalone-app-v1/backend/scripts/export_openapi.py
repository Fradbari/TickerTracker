import json
import sys
from pathlib import Path

# Add the backend root directory to the python path so imports work correctly
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app

def export_openapi():
    """
    Exports the FastAPI OpenAPI schema to openapi.json.
    Can be loaded directly into Swagger UI or Postman.
    """
    schema = app.openapi()
    
    output_file = backend_dir / "openapi.json"
    schema_json = json.dumps(schema, indent=2)
    
    with open(output_file, "w") as f:
        f.write(schema_json)
        
    print(f"✅ OpenAPI schema successfully exported to {output_file}")


if __name__ == "__main__":
    export_openapi()
 
