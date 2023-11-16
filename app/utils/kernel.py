import subprocess
from urllib.parse import urlparse
import requests
import uuid
import json
from contextlib import closing
from websocket import create_connection, WebSocketTimeoutException
import time

def connect(url, token):
    headers = {"Authorization": f"token {token}"}
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(url)
    return response, session


def create_session(session, url, notebook_name):
    # First, perform a GET request to obtain the _xsrf token
    response = session.get(url)
    xsrf_token = session.cookies.get('_xsrf')

    if not xsrf_token:
        raise ValueError("Missing _xsrf token. Cannot create session.")

    # Now, include the _xsrf token in the POST request
    headers = {'X-XSRFToken': xsrf_token}
    response = session.post(
        url + "api/sessions",
        headers=headers,
        json={
            "kernel": {"name": "python3"},
            "name": notebook_name,  # Use the notebook_name parameter for the name
            "path": notebook_name,  # Use the notebook_name parameter for the path
            "type": "notebook",
        },
    )

    # Check if the POST request was successful
    if response.status_code != 201:
        raise Exception(f"Failed to create session: {response.json()}")

    data = response.json()
    return data



def delete_session(session, url, session_id):
    res = session.delete(url + f"api/sessions/{session_id}")
    return res


def shutdown_server(session, url):
    session.post(url + "api/shutdown")
    try:
        session.get(url)
    except requests.exceptions.ConnectionError:
        print("Server has been successfully shutdown!")


def list_dir(session, url):
    res = session.get(url + "api/contents/").json()
    return res["content"]


def list_dir_names(session, url):
    res = session.get(url + "api/contents/").json()
    return [name["name"] for name in res["content"]]


def list_sessions(session, url):
    res = session.get(url + "api/sessions").json()
    return res


def list_specs(session, url):
    res = session.get(url + "api/kernelspecs").json()
    return res


def create_notebook(session, url):
    res = session.post(url + "api/contents/", json={"type": "notebook"})
    return res


def rename_notebook(session, url, name, new_name):
    res = session.patch(url + "api/contents/" + name, json={"path": new_name})
    return res


def delete_notebook(session, url, name):
    # DELETE /api/contents/{path}
    res = session.delete(url + "api/contents/" + name)
    return res


def get_contents(session, url, name):
    res = session.get(url + "api/contents/" + name).json()
    return res


def add_cell(session, url, name, data, source):
    cell = {
        "cell_type": "code",
        "id": "0",
        "metadata": {},
        "source": [
            source,
        ],
        "outputs": [],
        "execution_count": 0,
    }
    data["content"]["cells"].append(cell)
    return data


def write_changes(session, url, name, data):
    res = session.put(
        url + "api/contents/" + name,
        json={"content": data["content"], "type": "notebook"},
    )
    return res


def recv_all(conn):
    while True:
        try:
            msg = json.loads(conn.recv())
        except WebSocketTimeoutException:
            break
        print(f" type: {msg['msg_type']:16} content: {msg['content']}")


def connect_server_ws(url, token, kernel_id, session_id):
    pass


def exec_code(url, token, kernel_id, session_id, code):
    ws_base_url = urlparse(url)._replace(scheme="ws").geturl()
    ws_url = ws_base_url + \
        f"api/kernels/{kernel_id}/channels?session_id={session_id}"
    headers = {"Authorization": f"token {token}"}

    code_msg_id = str(uuid.uuid1())
    code_msg = {
        "channel": "shell",
        "content": {"silent": False, "code": code},
        "header": {"msg_id": code_msg_id, "msg_type": "execute_request"},
        "metadata": {},
        "parent_header": {},
    }

    with closing(create_connection(ws_url, header=headers)) as conn:
        print(f"code: {code}")
        start_time = time.time()
        conn.send(json.dumps(code_msg))
        while True:
            try:
                msg = json.loads(conn.recv())
            except WebSocketTimeoutException:
                break

            if msg["msg_type"] == "stream":
                yield msg["content"]["text"]

            if msg["msg_type"] == "execute_reply":
                end_time = time.time()
                time_taken = round(end_time - start_time, 3)
                yield f"Time taken: {time_taken} seconds\n"
                break


if __name__ == "__main__":
    print("Hello I am main")