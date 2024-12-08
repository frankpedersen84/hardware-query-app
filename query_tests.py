import sqlite3
import pandas as pd
from tabulate import tabulate

def run_query(query, description):
    print(f"\n=== {description} ===")
    try:
        conn = sqlite3.connect('hardware.db')
        result = pd.read_sql_query(query, conn)
        print(tabulate(result, headers='keys', tablefmt='psql', showindex=False))
        print(f"Results found: {len(result)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()

# List of test queries
queries = [
    ("SELECT COUNT(*) as total_cameras FROM cameras", 
     "1. Total number of cameras in the system"),
    
    ("SELECT model, COUNT(*) as count FROM hardware GROUP BY model ORDER BY count DESC", 
     "2. Distribution of camera models"),
    
    ("SELECT name, address, model FROM hardware WHERE enabled = 1 LIMIT 5",
     "3. First 5 enabled cameras with their addresses and models"),
    
    ("SELECT DISTINCT recordingserver, COUNT(*) as camera_count FROM cameras GROUP BY recordingserver",
     "4. Number of cameras per recording server"),
    
    ("SELECT h.name, h.model, h.firmwareversion FROM hardware h WHERE h.firmwareversion NOT LIKE '%DevicePack%' LIMIT 5",
     "5. Hardware firmware versions (excluding DevicePack)"),
    
    ("SELECT name, channel, recordingenabled, recordingframerate FROM cameras WHERE recordingenabled = 1 LIMIT 5",
     "6. Cameras with active recording and their frame rates"),
    
    ("SELECT DISTINCT g.[group], COUNT(*) as cameras_in_group FROM cameragroups g GROUP BY g.[group] ORDER BY cameras_in_group DESC",
     "7. Camera groups and their sizes"),
    
    ("SELECT h.name, h.model, h.macaddress FROM hardware h WHERE h.macaddress IS NOT NULL LIMIT 5",
     "8. Hardware MAC addresses"),
    
    ("SELECT c.name, c.motiondetectionmethod, c.motionmanualsensitivity FROM cameras c WHERE c.motionenabled = 1 LIMIT 5",
     "9. Motion detection settings"),
    
    ("SELECT cs.camera, cs.name, cs.livemode FROM camerastreams cs LIMIT 5",
     "10. Camera stream configurations"),
    
    ("SELECT DISTINCT setting, COUNT(*) as count FROM camerageneralsettings GROUP BY setting ORDER BY count DESC LIMIT 10",
     "11. Most common camera settings"),
    
    ("SELECT h.name, h.model, h.driverversion FROM hardware h WHERE h.driverversion LIKE '%DevicePack%' LIMIT 5",
     "12. Cameras using DevicePack drivers"),
    
    ("SELECT c.name, c.prebufferseconds, c.recordingframerate FROM cameras c WHERE c.prebufferenabled = 1 LIMIT 5",
     "13. Pre-buffer settings for cameras"),
    
    ("SELECT DISTINCT eventname, COUNT(*) as count FROM cameraevents GROUP BY eventname ORDER BY count DESC LIMIT 5",
     "14. Most common camera events"),
    
    ("SELECT c.name, c.hardware, c.channel FROM cameras c WHERE c.multicastenabled = 1 LIMIT 5",
     "15. Multicast-enabled cameras"),
    
    ("SELECT h.name, h.model, ptz.ptzenabled FROM hardware h JOIN hardwareptzsettings ptz ON h.name = ptz.hardware WHERE ptz.ptzenabled = 1 LIMIT 5",
     "16. PTZ-enabled cameras"),
    
    ("SELECT c.name, c.storage, c.recordingframerate FROM cameras c WHERE c.recordingframerate > 10 LIMIT 5",
     "17. High-framerate cameras"),
    
    ("SELECT DISTINCT rd.relateddevicetype, COUNT(*) as count FROM camerarelateddevices rd GROUP BY rd.relateddevicetype",
     "18. Types of related devices"),
    
    ("SELECT h.name, h.model, h.passwordlastmodified FROM hardware h WHERE h.passwordlastmodified != '00:00:00.000000' LIMIT 5",
     "19. Recently password-modified devices"),
    
    ("SELECT c.name, c.hardware, c.motionthreshold FROM cameras c WHERE c.motionenabled = 1 ORDER BY c.motionthreshold DESC LIMIT 5",
     "20. Cameras with highest motion sensitivity")
]

def main():
    print("Running 20 test queries on the camera database...")
    for query, description in queries:
        run_query(query, description)

if __name__ == "__main__":
    main()
