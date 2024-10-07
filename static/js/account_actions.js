function checkLoginStatus() {
    const accountLink = document.getElementById('account-link');
    const isLoggedIn = accountLink.getAttribute('data-is-logged-in') === 'true';

    if (isLoggedIn) {
        accountLink.href = '/account/';
        accountLink.textContent = 'Moje Konto';
    } else {
        accountLink.href = '/login/';
        accountLink.textContent = 'Zaloguj się';
    }
}

document.addEventListener('DOMContentLoaded', checkLoginStatus);