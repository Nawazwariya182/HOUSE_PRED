document.getElementById('predictionForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    const data = {
        title: formData.get('title'),
        location: formData.get('location'),
        rate_persqft: parseFloat(formData.get('rate_persqft')),
        area_insqft: parseFloat(formData.get('area_insqft')),
        building_status: formData.get('building_status')
    };

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('result').innerText = `Predicted House Price: ${data.predicted_price} Lakhs`;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = 'Error fetching data. Please try again later.';
    });
});
