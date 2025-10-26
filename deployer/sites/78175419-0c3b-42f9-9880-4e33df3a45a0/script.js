document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('[data-carousel]');
    carousels.forEach((carousel) => {
        const container = carousel.querySelector('[data-carousel-container]');
        const prevButton = carousel.querySelector('[data-carousel-prev]');
        const nextButton = carousel.querySelector('[data-carousel-next]');
        const paginationContainer = carousel.querySelector('[data-carousel-pagination]');
        
        if (!container) return;

        const items = Array.from(container.children);
        let currentIndex = 0;
        const totalItems = items.length;

        if (totalItems <= 1) {
            if (prevButton) prevButton.style.display = 'none';
            if (nextButton) nextButton.style.display = 'none';
            if (paginationContainer) paginationContainer.style.display = 'none';
            return;
        }

        // Create pagination dots
        if (paginationContainer) {
            for (let i = 0; i < totalItems; i++) {
                const dot = document.createElement('button');
                dot.classList.add('w-3', 'h-3', 'rounded-full', 'bg-gray-300', 'hover:bg-gray-500', 'transition', 'mx-1');
                dot.setAttribute('data-carousel-dot', i);
                dot.addEventListener('click', () => {
                    currentIndex = i;
                    updateCarousel();
                });
                paginationContainer.appendChild(dot);
            }
        }
        const dots = paginationContainer ? paginationContainer.querySelectorAll('[data-carousel-dot]') : [];

        function updateCarousel() {
            container.style.transform = `translateX(-${currentIndex * 100}%)`;
            if(paginationContainer){
                dots.forEach((dot, i) => {
                    if (i === currentIndex) {
                        dot.classList.remove('bg-gray-300');
                        dot.classList.add('bg-[#8C2668]');
                    } else {
                        dot.classList.remove('bg-[#8C2668]');
                        dot.classList.add('bg-gray-300');
                    }
                });
            }
        }

        if (prevButton) {
            prevButton.addEventListener('click', () => {
                currentIndex = (currentIndex - 1 + totalItems) % totalItems;
                updateCarousel();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => {
                currentIndex = (currentIndex + 1) % totalItems;
                updateCarousel();
            });
        }

        updateCarousel();
    });
});
