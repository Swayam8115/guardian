const STORAGE_KEY = 'guardian_user';

function getUser() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)); }
    catch { return null; }
}

function requireAuth() {
    if (!getUser()) window.location.href = 'login.html';
}

function logout() {
    localStorage.removeItem(STORAGE_KEY);
    window.location.href = 'login.html';
}

function renderUserPill(containerId) {
    const user = getUser();
    if (!user) return;
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `
        <div class="user-pill" onclick="logout()" title="Click to logout">
            <img src="${user.picture || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.name)}" alt="avatar">
            <div class="user-pill-info">
                <div class="user-pill-name">${user.name}</div>
                <div class="user-pill-email">${user.email}</div>
            </div>
        </div>
    `;
}
