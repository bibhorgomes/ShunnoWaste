function showDetails(button) {
    // Get data attributes from the clicked button
    const name = button.getAttribute('data-name');
    const address = button.getAttribute('data-address');
    const materials = button.getAttribute('data-materials');
    const mapLink = button.getAttribute('data-map');
    const imageUrl = button.getAttribute('data-image');

    // Update the details section
    document.getElementById('location-name').innerText = name;
    document.getElementById('location-address').innerHTML = `<b>Address:</b> ${address}`;
    document.getElementById('accepted-materials').innerHTML = `<b>Accepted Materials:</b> ${materials}`;
    document.getElementById('google-maps-link').href = mapLink;
    const detailsImgDiv = document.getElementById('details-img');
    detailsImgDiv.style.backgroundImage = `url(${imageUrl})`;
}

