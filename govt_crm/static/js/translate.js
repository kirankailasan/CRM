function loadTranslations(languageCode, page) {
  // If the language is English, skip loading the JSON and keep the default text
  if (languageCode === 'en') {
    console.log('Using default English text');
    return;  // Exit early without loading any JSON
  }

  fetch(`/static/translations/${languageCode}/${page}.json`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Translation file not found');
      }
      return response.json();
    })
    .then(data => {
      // Iterate over the translation data and update the page
      for (const [key, value] of Object.entries(data)) {
        // Target elements by ID
        const elementById = document.getElementById(key);
        if (elementById) {
          elementById.textContent = value;
        } else {
          console.warn(`No element found for ID: ${key}`);
        }

        // Target elements by class
        const elementsByClass = document.querySelectorAll(`.${key}`);
        if (elementsByClass.length > 0) {
          elementsByClass.forEach(element => {
            element.textContent = value;
          });
        } else {
          console.warn(`No element found for class: ${key}`);
        }

        // Target elements with data-translate attribute
        const elementsByData = document.querySelectorAll(`[data-translate="${key}"]`);
        if (elementsByData.length > 0) {
          elementsByData.forEach(element => {
            if (element.tagName === 'IMG') {
              element.alt = value; // Update alt text for image
            } else {
              element.textContent = value; // Update text for other elements
            }
          });
        } else {
          console.warn(`No element found for data-translate attribute: ${key}`);
        }

        // Target elements by name attribute
        const elementsByName = document.querySelectorAll(`[name="${key}"]`);
        if (elementsByName.length > 0) {
          elementsByName.forEach(element => {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
              element.placeholder = value; // Update placeholder for input/textarea
            } else {
              element.textContent = value; // Update text for other elements
            }
          });
        } else {
          console.warn(`No element found for name: ${key}`);
        }
      }
    })
    .catch(error => {
      console.error('Error loading translations:', error);
    });
}

// Dynamically set the current page based on the URL
const currentPage = window.location.pathname
  .replace(/\/$/, '')          // Remove trailing slash
  .replace('.html', '')        // Remove .html extension
  .split('/').pop() || 'index';

let userLanguage = 'en'; // Default language

// Check for saved language in localStorage or browser language
if (localStorage.getItem('selectedLanguage')) {
  userLanguage = localStorage.getItem('selectedLanguage');
} else if (navigator.language.startsWith('hi') || navigator.language.startsWith('mr')) {
  userLanguage = navigator.language.split('-')[0]; // 'hi' or 'mr'
}

// Load the translations for the current page (skip for English)
loadTranslations(userLanguage, currentPage);

// Set the language dropdown to the saved or default language
document.getElementById('language-selector').value = userLanguage;

document.addEventListener('DOMContentLoaded', function() {
  var langSelector = document.getElementById('language-selector');
  if (langSelector) {
    langSelector.addEventListener('change', function() {
      var selectedLang = this.value;
      // Save language preference (optional)
      localStorage.setItem('selectedLanguage', selectedLang);
      // Reload or trigger translation logic
      location.reload(); // Or call your translation function here
    });
    // Optionally, set selector to saved language
    var savedLang = localStorage.getItem('selectedLanguage');
    if (savedLang) {
      langSelector.value = savedLang;
    }
  }
});
