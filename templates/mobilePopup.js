document.addEventListener('DOMContentLoaded', function() {
    // Check if user is not already on mobile
    if (window.innerWidth > 768) {
        // Wait 5 seconds before showing the popup
        setTimeout(function() {
            showMobilePopup();
        }, 5000);
    }
});

function showMobilePopup() {
    // Create popup elements
    const overlay = document.createElement('div');
    overlay.className = 'mobile-popup-overlay';
    
    const popup = document.createElement('div');
    popup.className = 'mobile-popup';
    
    // Popup content
    popup.innerHTML = `
        <div class="mobile-popup-content">
            <h3>Better on Mobile!</h3>
            <p>Switch to your mobile device for a more immersive flashcard learning experience.</p>
            <button id="closePopup" class="mobile-popup-close">Got it</button>
        </div>
    `;
    
    // Add to DOM
    document.body.appendChild(overlay);
    document.body.appendChild(popup);
    
    // Add event listener to close button
    document.getElementById('closePopup').addEventListener('click', function() {
        overlay.remove();
        popup.remove();
    });
}
