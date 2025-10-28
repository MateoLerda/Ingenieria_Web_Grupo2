// Lightbox functionality for event gallery images

let currentImageIndex = 0;
let galleryImages = [];

// Initialize gallery images array when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get all gallery items that have images (not videos)
    const imageElements = document.querySelectorAll('.gallery-item[data-image]');
    galleryImages = Array.from(imageElements).map(item => item.getAttribute('data-image'));
});

/**
 * Opens the lightbox modal with the clicked image
 * @param {HTMLElement} element - The gallery item that was clicked
 */
function openLightbox(element) {
    const imageUrl = element.getAttribute('data-image');
    const lightboxModal = document.getElementById('lightboxModal');
    const lightboxImage = document.getElementById('lightboxImage');
    
    if (!imageUrl || !lightboxModal || !lightboxImage) {
        return;
    }
    
    // Find the index of the clicked image
    currentImageIndex = galleryImages.indexOf(imageUrl);
    
    // Set the image source and show the modal
    lightboxImage.src = imageUrl;
    lightboxModal.classList.add('active');
    
    // Prevent body scrolling when lightbox is open
    document.body.style.overflow = 'hidden';
}

/**
 * Closes the lightbox modal
 * @param {Event} event - The click event
 */
function closeLightbox(event) {
    const lightboxModal = document.getElementById('lightboxModal');
    const lightboxImage = document.getElementById('lightboxImage');
    
    // Only close if clicking on the modal background or close button
    if (event.target === lightboxModal || event.target.classList.contains('lightbox-close')) {
        lightboxModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

/**
 * Navigate to the next or previous image in the gallery
 * @param {number} direction - Direction to navigate (-1 for previous, 1 for next)
 * @param {Event} event - The click event
 */
function navigateLightbox(direction, event) {
    event.stopPropagation(); // Prevent closing the lightbox
    
    if (galleryImages.length === 0) {
        return;
    }
    
    // Calculate new index with wrapping
    currentImageIndex = (currentImageIndex + direction + galleryImages.length) % galleryImages.length;
    
    // Update the image
    const lightboxImage = document.getElementById('lightboxImage');
    if (lightboxImage) {
        // Add a fade effect
        lightboxImage.style.opacity = '0';
        
        setTimeout(() => {
            lightboxImage.src = galleryImages[currentImageIndex];
            lightboxImage.style.opacity = '1';
        }, 150);
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(event) {
    const lightboxModal = document.getElementById('lightboxModal');
    
    if (lightboxModal && lightboxModal.classList.contains('active')) {
        switch(event.key) {
            case 'Escape':
                closeLightbox({ target: lightboxModal });
                break;
            case 'ArrowLeft':
                navigateLightbox(-1, event);
                break;
            case 'ArrowRight':
                navigateLightbox(1, event);
                break;
        }
    }
});

// Prevent image dragging in lightbox
document.addEventListener('DOMContentLoaded', function() {
    const lightboxImage = document.getElementById('lightboxImage');
    if (lightboxImage) {
        lightboxImage.addEventListener('dragstart', function(e) {
            e.preventDefault();
        });
    }
});
