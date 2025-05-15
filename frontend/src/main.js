const API_URL = 'https://pothole-segmentation-app.onrender.com';

const res = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    body: formData,
});
