class SellableContainer extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        const itemId = this.getAttribute('itemId');
        const itemName = this.getAttribute('itemName');
        const itemPrice = this.getAttribute('itemPrice');
        const itemImageSrc = this.getAttribute('itemImageSrc');
        const sellerName = this.getAttribute('sellerName');
        this.innerHTML = `
            <div id=${itemId} class="flex flex-col items-center justify-center bg-slate-200 hover:bg-slate-300 p-6 rounded-xl shadow-lg">
                <img src="${itemImageSrc}" class="bg-white rounded-xl mb-3">
                <div class="flex flex-row gap-10">
                    <div class="font-bold">${itemName}</div>
                    <div class="font-bold">$${itemPrice}</div>
                </div>
                <div class="italic item">${sellerName}</div>
            </div>
        `;
  }

  
}

customElements.define('sellable-container', SellableContainer);