const express = require('express')
const { Pool } = require('pg');
const app = express()
const port = 8080

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'postgres',
    password: 'man22477man',
    port: 5432,
  });
  
  app.use(express.json());

  async function createAlbumsTable() {
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

  createAlbumsTable();
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