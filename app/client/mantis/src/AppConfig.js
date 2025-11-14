const idProject = window.djangoConfig?.projectId ?? 1
const apiBaseUrl = window.djangoConfig?.baseUrl ?? "http://localhost:8000"
const csrfToken = window.djangoConfig?.csrfToken ?? "falsocsrf"

export const appConfig = {
    "apiBaseUrl": apiBaseUrl,
    "csrfToken": csrfToken,
    "idProject": idProject,
    "urlLogo": apiBaseUrl + "/static/img/logo.png",
    "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
    },
    "URLProjectData": apiBaseUrl + "/api/projects/data/" + idProject + "/",
    "URLSourcesAvailable": apiBaseUrl + "/api/projects/resources/available/",
    "URLTechnicalsAvailable": apiBaseUrl + "/api/technicals/available/",
    "URLVehiclesAvailable": apiBaseUrl + "/api/vehicles/available/",
    "URLResourcesProject": apiBaseUrl + "/api/projects/" + idProject + "/resources/",
    "URLUpdateResourceItem": apiBaseUrl + "/api/projects/resources/update/",
    "URLDeleteResourceProject": apiBaseUrl + "/api/projects/resources/delete/${id_project_resource}/",
    "URLSheetProjects": apiBaseUrl + "/api/workorders/sheets/project/" + idProject + "/",
    "URLAddSheetProject": apiBaseUrl + "/api/workorders/sheets/create/",
    "URLAddResourceToProject": apiBaseUrl + "/api/projects/resources/add/",
    "URLCreateCustodyChain": apiBaseUrl + "/api/workorders/custody_chain/create/",
}