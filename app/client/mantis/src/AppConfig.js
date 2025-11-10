const idProject = window.djangoConfig?.projectId ?? 7;
const apiBaseUrl = window.djangoConfig?.baseUrl ?? "http://localhost:8000";
const csrfToken = window.djangoConfig?.csrfToken ?? "falsocsrf";

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
    "URLResourcesProject": apiBaseUrl + "/api/projects/" + idProject + "/resources/",
    "URLSheetProjects": apiBaseUrl + "/api/workorders/sheet-projects/" + idProject + "/",
    "URLAddResourceToProject": apiBaseUrl + "/api/projects/resources/add/",
}