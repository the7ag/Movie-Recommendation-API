const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Route to receive data from Flutter
app.post('/data', (req, res) => {
  const flutterData = req.body;

  // Send data to Python script
  axios.post('http://127.0.0.1:5000/process-data', flutterData)
    .then((response) => {
      console.log(response.data);
      res.send(response.data); // Optionally, send response back to Flutter
    })
    .catch((error) => {
      console.error(error);
      res.status(500).send('Error processing data');
    });
});

app.listen(port, () => {
  console.log(`Express server is running on http://localhost:${port}`);
});
