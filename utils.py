import json

def sanitize_input(arg: str):
    # sanitizin' muh inputs
    arg = arg.replace('\n', '')
    exceptions = '!#$%&? ^*()-_=+[]{};:\'",./<>`~'
    for i in arg:
        if not i.isalnum() and i not in exceptions:
            arg = arg.replace(i, '')
    return arg


def load_creds(filepath):
    try:
        with open(filepath, "r") as c:
            credentials = json.loads(c.read())
        return credentials
    except Exception as e:
        print(f"Error: {e}.\nCredentials not loaded!")
        exit(1)