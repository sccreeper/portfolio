from datetime import datetime
from src.constants import DATA_VERSION_PATH

def migrate(old_ver: int, cur_ver: int):
    
    while old_ver < cur_ver:

        start = datetime.now().timestamp()

        match old_ver:
            case -1:
                from src.db.migration.versions import v0
                v0.migrate()
            case _:
                raise ValueError(f"invalid version {old_ver}")
            
        old_ver += 1

        print(f"Migrated to {cur_ver} in {datetime.now().timestamp()-start}")

    # Write version to version file if successful
    with open(DATA_VERSION_PATH, "w") as f:
        f.write(str(cur_ver))