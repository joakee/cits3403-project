


class FilterButton extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        var max_price = 150;
        var min_price = 0;
        this.innerHTML = `
            <style>
                .dropdown {
                    transition: all 0.1s cubic-bezier(0.16, 1, 0.5, 1);
                    transform: translateY(0.5rem);
                    visibility: hidden;
                    opacity: 0;
                }

                .show {
                    transform: translateY(0rem);
                    visibility: visible;
                    opacity: 1;
                }
            </style>
            <button class="btn" id="btn">
            <svg class="w-6 h-6 text-slate-400 hover:text-slate-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7.75 4H19M7.75 4a2.25 2.25 0 0 1-4.5 0m4.5 0a2.25 2.25 0 0 0-4.5 0M1 4h2.25m13.5 6H19m-2.25 0a2.25 2.25 0 0 1-4.5 0m4.5 0a2.25 2.25 0 0 0-4.5 0M1 10h11.25m-4.5 6H19M7.75 16a2.25 2.25 0 0 1-4.5 0m4.5 0a2.25 2.25 0 0 0-4.5 0M1 16h2.25"/>
            </svg>
            </button>

            <div class="absolute left-0 w-full">
            <div class="dropdown bg-slate-200 rounded-lg m-5 shadow-lg p-10" id="dropdown">

                <div class="font-bold relative pb-8">
                    <span class="text-sm text-body">Max Price</span>
                    <input id="default-range" type="range" value="50" class="w-full h-2 bg-neutral-quaternary rounded-full appearance-none cursor-pointer">
                    <span class="text-sm text-body absolute start-0 bottom-2">$${min_price}</span>
                    <span class="text-sm text-body absolute end-0 bottom-2">$${max_price}</span>
                </div>
                <label class="font-bold inline-flex items-center cursor-pointer">
                    <input type="checkbox" value="" class="sr-only peer">
                    <div class="relative w-9 h-5 bg-neutral-quaternary peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-brand-soft dark:peer-focus:ring-brand-soft rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-buffer after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-brand"></div>
                    <span class="select-none ms-3 text-sm font-medium text-heading">Pickup at Uni</span>
                </label>
            </div>
            </div>

        `;

        const dropdownBtn = document.getElementById("btn");
        const dropdownMenu = document.getElementById("dropdown");

        const toggleDropdown = function () {
            console.log("test");
        dropdownMenu.classList.toggle("show");
        };

        dropdownBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleDropdown();
        });
    }
}

customElements.define('filter-button', FilterButton);



