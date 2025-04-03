import requests

BASE_PATH = "https://pypi.org"
def get_project_data(project_name: str) -> dict[str, dict[str, str]]:
    url = BASE_PATH + f"/pypi/{project_name}/json"
    response = requests.get(url, headers={
        "Accept": "application/json"
    })

    if response.status_code != 200:
        raise Exception("Non-200 Response Code")

    response_data: dict[str, dict[str, str]] = response.json()
    return response_data

def get_pypi_version(project_data: dict[str, dict[str, str]]) -> str:
    info_data = project_data.get("info")

    if not info_data:
        raise Exception("Could not get PyPi Project")

    version_data: str = str(info_data.get("version"))

    return str(version_data)
