import webdav.client as wc
import os # For path manipulations if needed later

def get_nextcloud_info(request_details: str) -> str:
    """Placeholder for interacting with Nextcloud."""
    if not request_details:
        return "How can I help you with Nextcloud?"
    return f"Interacting with Nextcloud regarding '{request_details}'... (Full functionality coming soon!)"

def handle_nextcloud_action(creds: dict, nlu_data: dict) -> str:
    """Handles Nextcloud actions based on NLU intent and entities, using provided credentials."""
    if not creds or not all(k in creds for k in ['url', 'user', 'password']):
        return "Nextcloud credentials are not set or incomplete. Please configure them in settings first."

    options = {
        'webdav_hostname': creds['url'].rstrip('/'), # Ensure no trailing slash for hostname
        'webdav_login': creds['user'],
        'webdav_password': creds['password']
    }
    
    # Adjust hostname if it already contains the remote.php/dav part common in user input
    # The library expects just the base hostname (e.g., https://cloud.example.com)
    # and constructs the /remote.php/dav/files/USER/ part itself.
    if '/remote.php/dav' in options['webdav_hostname']:
        options['webdav_hostname'] = options['webdav_hostname'].split('/remote.php/dav')[0]
    elif '/remote.php/webdav' in options['webdav_hostname']: # Common misconfiguration
        options['webdav_hostname'] = options['webdav_hostname'].split('/remote.php/webdav')[0]

    intent = nlu_data.get('intent')
    entities = nlu_data.get('entities', {})

    try:
        client = wc.Client(options)
        # client.verify = True # Set to False if SSL cert issues, True by default
    except Exception as e:
        print(f"Nextcloud: Error creating WebDAV client for {options.get('webdav_hostname')}: {e}")
        return f"Sorry, I couldn't connect to your Nextcloud at {options.get('webdav_hostname')}. Please check the URL and credentials. Error: {e}"

    if intent == "nextcloud_list_files":
        path_to_list = entities.get('path', '/').strip()
        # Ensure path is relative to the user's DAV files root, and doesn't start with /dav/files/USER
        # The library handles the user-specific root.
        if path_to_list.startswith(f"/remote.php/dav/files/{creds['user']}"):
            path_to_list = path_to_list[len(f"/remote.php/dav/files/{creds['user']}"):]
        elif path_to_list.startswith('/dav/files/') or path_to_list.startswith('/webdav/'):
             # Strip common prefixes if user included them thinking it was full path
            path_parts = path_to_list.split('/')
            if len(path_parts) > 3 and path_parts[3] == creds['user']:
                 path_to_list = '/'.join(path_parts[4:])
        
        if not path_to_list.startswith('/') and path_to_list != "":
            path_to_list = '/' + path_to_list
        if path_to_list == "/": # Library uses empty string for root for some operations
            path_to_list = ""

        return _list_nextcloud_path(client, path_to_list, creds['user'])
    
    elif intent == "nextcloud_query": # Generic query
        # For now, just confirm we received it. Later can add more actions.
        task_details = entities.get('task_details', 'your request')
        return f"Received your Nextcloud query about '{task_details}'. More specific Nextcloud actions are being developed! For now, I can list files."
    
    return "I understood you want to do something with Nextcloud, but I'm not sure what yet!"

def _list_nextcloud_path(client: wc.Client, path: str, username: str) -> str:
    """Helper function to list files and folders at a given path."""
    try:
        # The path for client.list is relative to /remote.php/dav/files/USERNAME/
        # So, if path is "/documents", it means /remote.php/dav/files/USERNAME/documents
        # If path is "" or "/", it means /remote.php/dav/files/USERNAME/
        
        actual_path_to_list = path.lstrip('/') # Library expects path relative to user's root, no leading slash usually
        
        items = client.list(actual_path_to_list)
        
        if not items:
            # Check if the path itself is a file
            try:
                if client.check(actual_path_to_list) and not client.is_dir(actual_path_to_list):
                    return f"'{path if path else '/'}' is a file, not a directory."
            except wc.WebDAVException:
                pass # If check fails, it's likely not found or not accessible
            return f"No files or folders found in Nextcloud at path: '{path if path else '/'}' or path does not exist/is not accessible."

        response_lines = [f"Contents of Nextcloud path '{path if path else '/'}:"]
        for item_name in items:
            full_item_path = os.path.join(actual_path_to_list, item_name.lstrip('/')).lstrip('/')
            is_dir = False
            try:
                # client.list() only returns names. We need to check type.
                # is_dir can be slow if called for many items. 
                # A PROPFIND would be more efficient for getting type along with name.
                # For simplicity, we'll use client.is_dir for now.
                # But be mindful this does an extra request per item.
                if client.is_dir(full_item_path):
                    is_dir = True
            except wc.WebDAVException as e:
                 # Could be a file that client.is_dir has issues with, or access error
                 print(f"Nextcloud: Could not determine type for {full_item_path}: {e}")
            
            item_display = item_name.lstrip('/')
            if is_dir:
                response_lines.append(f"- {item_display}/ (folder)")
            else:
                response_lines.append(f"- {item_display} (file)")
        
        return "\n".join(response_lines)

    except wc.WebDAVException as e:
        print(f"Nextcloud: WebDAV error listing '{path if path else '/'}' for user {username}: {e}")
        # Check for common errors based on status code if possible
        if e.response and e.response.status_code == 401:
            return "Nextcloud: Authentication failed. Please check your credentials in settings."
        if e.response and e.response.status_code == 404:
            return f"Nextcloud: Path '{path if path else '/'}' not found. Please check the path."
        return f"Sorry, an error occurred while accessing Nextcloud path '{path if path else '/'}'."
    except Exception as e:
        print(f"Nextcloud: Unexpected error listing '{path if path else '/'}' for user {username}: {e}")
        return f"An unexpected error occurred with Nextcloud: {e}"

# Placeholder for future functions:
# def upload_to_nextcloud(client: wc.Client, local_path: str, remote_path: str) -> str:
#     pass
# def download_from_nextcloud(client: wc.Client, remote_path: str, local_path: str) -> str:
#     pass 