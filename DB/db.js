const express = require('express')
const { Pool } = require('pg');
const bodyParser = require('body-parser');

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
        CREATE TABLE IF NOT EXISTS genres (
            movieid integer,
            genres text[],
            title text
        );
      `;
      await pool.query(query);
      console.log('genres table created');
    } catch (err) {
      console.error(err);
      console.error('genres table creation failed');
    }
  }
  creategenresTable();

  async function createUsersTable() {
    try {
      const query = `
        CREATE TABLE IF NOT EXISTS users (
          userid varchar(255),
          recommendations varchar(255)[],
          password varchar(255),
          email varchar(255),
          username varchar(255)
        );
      `;
      await pool.query(query);
      console.log('users table created');
    } catch (err) {
      console.error(err);
      console.error('users table creation failed');
    }
  }
  createUsersTable();

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
    try
    {
    const query = `INSERT INTO users (userid,username, email, password)
     VALUES ('${uniqueId}','${username}', '${email}', '${password}')
     RETURNING userid`;
     const result = await pool.query(query);
     if (result.rows.length > 0) {
      res.status(201).send({ message: 'New user created', AddedID: result.rows[0].userid });
    } else {
      res.status(500).send({ message: 'Failed to create new user' });
    }
     }
    catch (err) {
      console.error('Error creating new user:', error);
      res.status(500).send({ message: 'Failed to create new user' });
    }
  });
  app.post('/login', async (req, res) => {
    const { email, password } = req.body;..\
    try
    {
    const query = `SELECT * FROM users WHERE email = '${email}' AND password = '${password}'`;
    const result = await pool.query(query);
    if (result.rows.length > 0) {
      res.status(201).send({ message: 'Login successful'});
      res.redirect('/home');
    } else {
      res.status(500).send({ message: 'Invalid login credentials' });
    }
    }
    catch (err) {
      console.error(err);
      res.status(500).send('some error has occured');
    }
  });
  app.get('/home', (req, res) => {
    res.send('Login successful');
  });