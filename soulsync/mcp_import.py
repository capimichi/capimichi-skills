import sys
import subprocess
import json
import shlex

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python3 mcp_import.py <subcommand> [args...]\nSubcommands:\n  scan <directory_path> [limit=20] [offset=0]\n  identify <file_path>\n  search <query> [source]\n  tracklist <album_id> <source>\n  fuzzy_match <file_path> <album_id> <source>\n  import <file_path> <album_id> <source> <track_index>"
        }, indent=2))
        sys.exit(1)

    subcommand = sys.argv[1]
    remote_args = sys.argv[1:]

    # Construct SSH command to run inside container
    # shlex.join preserves spaces in paths and quotes parameters correctly
    cmd_parts = ["docker", "exec", "-i", "soulsync-webui", "python3", "/app/mcp_import.py"] + remote_args
    remote_cmd = shlex.join(cmd_parts)

    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "root@192.168.1.100", remote_cmd]

    # Execute remote command
    res = subprocess.run(ssh_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(json.dumps({
            "status": "error",
            "message": res.stderr.strip() or f"SSH exited with code {res.returncode}"
        }, indent=2))
        sys.exit(res.returncode)

    # Output the remote script response (which is JSON)
    print(res.stdout.strip())

if __name__ == "__main__":
    main()
