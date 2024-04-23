const express = require('express')
const { Pool } = require('pg');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express()
const port = 3000
app.use(bodyParser.urlencoded({ extended: false }));

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'postgres',
    password: 'man22477man',
    port: 5432,
  });
  
  app.use(express.json());

  async function creategenresTable() {
    try {
      const query = `
      CREATE TABLE IF NOT EXISTS movies (
        movieid VARCHAR(255) PRIMARY KEY,
        imdbid VARCHAR(255),
        tmdbid VARCHAR(255),
        title VARCHAR(255),
        poster VARCHAR(255),
        genres VARCHAR(255)[],
        "cast" VARCHAR(255)[]
        );
        CREATE TABLE IF NOT EXISTS users (
          userid varchar(255),
          recommendations varchar(255)[],
          password varchar(255),
          email varchar(255),
          username varchar(255)
        );
        CREATE TABLE IF NOT EXISTS "cast" (
          castid VARCHAR(255) PRIMARY KEY,
          "name" VARCHAR(255),
          photo VARCHAR(255)
        );
        CREATE TABLE IF NOT EXISTS ratings (
          userid VARCHAR(255),
          movieid VARCHAR(255),
          rating INTEGER,
          "timestamp" TIMESTAMP WITH TIME ZONE,
          PRIMARY KEY (userid, movieid)
        );
      `;
      await pool.query(query);
      console.log('tables created');
    } catch (err) {
      console.error(err);
      console.error('tables creation failed');
    }
  }
  creategenresTable();


app.get('/', (req, res) => {
    res.send('Hello World!')
  })
 app.post('/Movies', async (req, res) => {
    // Validate the incoming JSON data
    const { movieid, genres, title } = req.body;
    console.log(req.body);
    if (!movieid || !title || !genres ) {
      return res.status(400).send('One of the movieid, title or genres is missing in the data');
    }
    try {
      // try to send data to the database
      const query = `
        INSERT INTO genres (movieid, genres,title )
        VALUES ($1, $2, $3)
        RETURNING movieid;
      `;
      const values = [movieid, genres, title];
  
      const result = await pool.query(query, values);
      res.status(201).send({ message: 'New Movie created', AddedID: result.rows[0].movieid });
    } catch (err) {
      console.error(err);
      res.status(500).send('some error has occured');
    }
  });

  app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
  })

  app.get('/Movies', async (req, res) => {
    try {
      const query = 'SELECT * FROM genres;';
      const { rows } = await pool.query(query);
      res.status(200).json(rows);
    } catch (err) {
      console.error(err);
      res.status(500).send('failed');
    }
  });
  app.get('/Movies/:id', async (req, res) => {
    try {
      const { id } = req.params;
      const query = 'SELECT * FROM genres WHERE movieid = $1;';
      const { rows } = await pool.query(query, [id]);
  
      if (rows.length === 0) {
        return res.status(404).send('this movie is not in the database');
      }
  
      res.status(200).json(rows[0]);
    } catch (err) {
      console.error(err);
      res.status(500).send('failed');
    }
  });

  app.put('/Movies/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { genres, title } = req.body;
  
      if ( !title || !genres ) {
        return res.status(400).send('One of the title or genres is missing in the data');
      }
  
      const query = `
        UPDATE genres
        SET genres = $1,
            title  = $2
        WHERE movieid = $3
        RETURNING *;
      `;
      
      const { rows } = await pool.query(query, [genres, title, id]);
      if (rows.length === 0) {
        return res.status(404).send('Cannot find anything');
      }
      res.status(200).json(rows[0]);
    } catch (err) {
      console.error(err);
      res.status(500).send('Some error has occured failed');
    }
  });

  app.delete('/Movies/:id', async (req, res) => {
    try {
      const { id } = req.params;
      const query = 'DELETE FROM genres WHERE movieid = $1 RETURNING *;';
      const { rows } = await pool.query(query, [id]);
  
      if (rows.length === 0) {
        return res.status(404).send('we have not found the movie');
      }
      res.status(200).json(rows[0]);
    } catch (err) {
      console.error(err);
      res.status(500).send('some error has occured');
    }
  });
  function generateUniqueId() {
    const timestamp = Date.now().toString(36); // Convert current timestamp to base36
    const randomString = Math.random().toString(36).substr(2, 5); // Generate a random string
    return timestamp + randomString;
  }
  
  app.post('/signup', async (req, res) => {
    const { username, email, password } = req.body;
    const uniqueId = generateUniqueId();
    try {
        const query = 'INSERT INTO users (userid, username, email, password) VALUES ($1, $2, $3, $4) RETURNING userid';
        const result = await pool.query(query, [uniqueId, username, email, password]);
        if (result.rows.length > 0) {
            res.status(201).send({ message: 'New user created', AddedID: result.rows[0].userid });
        } else {
            res.status(500).send({ message: 'Failed to create new user' });
        }
    } catch (err) {
        console.error('Error creating new user:', err);
        res.status(500).send({ message: 'Failed to create new user' });
    }
});

app.post('/login', async (req, res) => {
    const { email, password } = req.body;
    try {
        const query = 'SELECT * FROM users WHERE email = $1 AND password = $2';
        const result = await pool.query(query, [email, password]);
        if (result.rows.length > 0) {
            res.status(200).send({ message: 'Login successful',Userid: result.rows[0].userid });
        } else {
            res.status(401).send({ message: 'Invalid login credentials' });
        }
    } catch (err) {
        console.error('Error during login:', err);
        res.status(500).send('An error occurred during login');
    }
});

function generateTimestamp()
{
// Create a new Date object
const currentDate = new Date();

// Get individual components of the date and time
const year = currentDate.getFullYear(); // Get the current year
const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // Month is zero-based, so add 1
const day = String(currentDate.getDate()).padStart(2, '0'); // Get the day of the month
const hours = String(currentDate.getHours()).padStart(2, '0'); // Get the hours (0-23)
const minutes = String(currentDate.getMinutes()).padStart(2, '0'); // Get the minutes (0-59)
const seconds = String(currentDate.getSeconds()).padStart(2, '0'); // Get the seconds (0-59)

// Get the timezone offset in hours
const timeZoneOffset = currentDate.getTimezoneOffset();
const timeZoneOffsetHours = Math.abs(Math.floor(timeZoneOffset / 60)).toString().padStart(2, '0');
const timeZoneSign = timeZoneOffset >= 0 ? '-' : '+';

// Combine date and time components
const formattedDate = `${year}-${month}-${day}`;
const formattedTime = `${hours}:${minutes}:${seconds}`;
const timeZone = `${timeZoneSign}${timeZoneOffsetHours}`;

// Concatenate date, time, and timezone
const dateTimeWithTimeZone = `${formattedDate} ${formattedTime}${timeZone}`;

// Output the current date and time with timezone
return dateTimeWithTimeZone;
}
app.post('/rating', async (req, res) => {
    const { userid, moviename ,rating } = req.body;
    const Movie='SELECT * FROM movies WHERE title =$1; ';
    const movieResult = await pool.query(Movie,[moviename]);
    const movieID = movieResult.rows[0].movieid;
    const timestamp=generateTimestamp();
    try {
        const query = 'INSERT INTO ratings (userid, movieid, rating, timestamp) VALUES ($1, $2, $3, $4) RETURNING userid';
        const result = await pool.query(query, [userid, movieID,rating,timestamp]);
        if (result.rows.length > 0) {
            res.status(200).send({ message: 'Rating Successful',Userid: result.rows[0].userid });
        } else {
            res.status(401).send({ message: 'Invalid rating credentials' });
        }
    } catch (err) {
        console.error('Error during rating:', err);
        res.status(500).send('An error occurred during rating');
    }
});
app.post('/recommend', (req, res) => {
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
app.get('/MovieID', async (req, res) => {
  try {
    const { id } = req.body;
    const query = 'SELECT * FROM movies WHERE movieid = $1;';
    const { rows } = await pool.query(query, [id]);
    if (rows.length === 0) {
      return res.status(404).send('this movie is not in the database');
    }  
    res.status(200).json(rows[0]);
  }catch (err) {
    console.error('Error during getting movie:', id);
    res.status(500).send('An error occurred during getting');
  }
  });
  app.get('/home', (req, res) => {
    res.send('Login successful');
  });