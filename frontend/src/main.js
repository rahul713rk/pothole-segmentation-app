const API_URL = 'https://pothole-segmentation-app.onrender.com';

const formData = new FormData();
formData.append('file', selectedFile);  // assuming you have this

const res = await fetch(`${API_URL}/predict`, {
  method: 'POST',
  body: formData,
});
const data = await res.json();