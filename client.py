from app.utils.kernel import *

url = "http://localhost:32774"
token = ""
res, session = connect(url, token)
name = "new_note.ipynb"

data = create_session(session, url)
kernel_id = data["kernel"]["id"]
session_id = data["id"]
print(kernel_id, session_id)

data = get_contents(session, url, name)
for cell in data["content"]["cells"]:
    code = cell["source"]
    # exec_code is a generator function which yields the output of the code
    # print the output of the code
    for output in exec_code(url, token, kernel_id, session_id, code):
        print(output)

# delete_session(session, url, session_id)
# shutdown_server(session, url)