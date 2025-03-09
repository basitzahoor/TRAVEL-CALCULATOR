document.addEventListener("DOMContentLoaded", function() {
    const quotationDetails = document.getElementById("quotation-details");
    const downloadBtn = document.getElementById("download-quotation");
    
    const quotationData = JSON.parse(localStorage.getItem("quotation"));
    if (quotationData) {
        let detailsHTML = "<h3>Quotation Breakdown</h3>";
        detailsHTML += `<p><strong>Total People:</strong> ${quotationData.totalPeople}</p>`;
        detailsHTML += `<p><strong>Rooms:</strong> ${quotationData.rooms}</p>`;
        detailsHTML += `<p><strong>Days:</strong> ${quotationData.days}</p>`;
        detailsHTML += "<h4>Selected Hotels:</h4><ul>";
        
        quotationData.hotels.forEach(hotel => {
            detailsHTML += `<li>${hotel.location} - ${hotel.name} (₹${hotel.rate}/day)</li>`;
        });
        
        detailsHTML += "</ul>";
        detailsHTML += `<h3>Total Quotation: ₹${quotationData.finalPrice}</h3>`;
        quotationDetails.innerHTML = detailsHTML;
    }
    
    downloadBtn.addEventListener("click", function() {
        const pdfContent = document.body.innerHTML;
        const blob = new Blob([pdfContent], { type: "application/pdf" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "Quotation.pdf";
        link.click();
    });
});
