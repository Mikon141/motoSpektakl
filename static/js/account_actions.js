// Funkcja sprawdzająca status logowania i zmieniająca odnośnik
function checkLoginStatus() {
    const accountLink = document.getElementById('account-link');
    const isLoggedIn = accountLink.getAttribute('data-is-logged-in') === 'true';  // Sprawdzenie atrybutu lub statusu

    if (isLoggedIn) {
        accountLink.href = '/account/';  // Przekierowanie na stronę konta
        accountLink.textContent = 'Moje Konto';  // Zmiana tekstu linku
    } else {
        accountLink.href = '/login/';  // Przekierowanie na stronę logowania
        accountLink.textContent = 'Zaloguj się';  // Zmiana tekstu linku
    }
}

// Uruchomienie funkcji po załadowaniu DOM
document.addEventListener('DOMContentLoaded', checkLoginStatus);