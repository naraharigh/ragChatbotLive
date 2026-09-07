import os
import sys
from pathlib import Path

import uvicorn

if __name__ == "__main__":
    # Direct script execution adds scripts/, not the project root, to sys.path.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        workers=1,
        log_config=None,
    )
