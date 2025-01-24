require('dotenv').config();
const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const { Expo } = require('expo-server-sdk');

const app = express();
app.use(cors());
app.use(express.json());

// Create MySQL connection
const connection = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

// Test database connection
connection.connect((err) => {
  if (err) {
    console.error('Error connecting to database:', err);
    return;
  }
  console.log('Connected to MySQL database');
});

// Example API endpoint
app.get('/api/items', (req, res) => {
  connection.query('SELECT * FROM items', (err, results) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(results);
  });
});

// Add this new endpoint for jobs
app.get('/api/classes', (req, res) => {
  connection.query('SELECT id_job, title, description, category, location, pay FROM jobs', (err, results) => {
    if (err) {
      console.log('Error fetching jobs:', err);
      res.status(500).json({ error: err.message });
      return;
    }
    console.log('Jobs fetched successfully:', results); // Debug log
    res.json(results);
  });
});

// Add this new endpoint for lessons
app.get('/api/lessons', (req, res) => {
  connection.query('SELECT id, title, description, class_id FROM lessons', (err, results) => {
    if (err) {
      console.log('Error fetching lessons:', err);
      res.status(500).json({ error: err.message });
      return;
    }
    console.log('Lessons fetched successfully:', results); // Debug log
    res.json(results);
  });
});

// Add endpoint for single lesson
app.get('/api/lessons/:id', (req, res) => {
  const lessonId = req.params.id;
  connection.query(
    'SELECT id, title, description, class_id FROM lessons WHERE id = ?',
    [lessonId],
    (err, results) => {
      if (err) {
        console.log('Error fetching lesson:', err);
        res.status(500).json({ error: err.message });
        return;
      }
      if (results.length === 0) {
        res.status(404).json({ error: 'Lesson not found' });
        return;
      }
      console.log('Lesson fetched successfully:', results[0]);
      res.json(results[0]);
    }
  );
});

const expo = new Expo();

// Add this to your existing MySQL tables
const createTableQuery = `
  CREATE TABLE IF NOT EXISTS device_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
`;

connection.query(createTableQuery);

// Register device tokens
app.post('/api/register-device', async (req, res) => {
  const { token } = req.body;
  console.log('Registering device token:', token);
  
  if (!Expo.isExpoPushToken(token)) {
    console.error('Invalid push token:', token);
    return res.status(400).json({ error: 'Invalid push token' });
  }

  try {
    await connection.promise().query(
      'INSERT INTO device_tokens (token) VALUES (?) ON DUPLICATE KEY UPDATE token = ?',
      [token, token]
    );
    console.log('Device token registered successfully');
    res.json({ message: 'Device registered successfully' });
  } catch (error) {
    console.error('Error registering device:', error);
    res.status(500).json({ error: error.message });
  }
});

// Function to send micro-learning notifications
async function sendMicroLearningNotifications() {
  try {
    // Get all lessons
    const [lessons] = await connection.promise().query('SELECT * FROM lessons');
    const [tokens] = await connection.promise().query('SELECT token FROM device_tokens');

    for (const lesson of lessons) {
      // Split description into smaller chunks (e.g., sentences)
      const contentChunks = lesson.description.match(/[^.!?]+[.!?]+/g) || [];
      
      // Create notification messages
      const messages = tokens.map(({ token }) => ({
        to: token,
        sound: 'default',
        title: `Quick Tip: ${lesson.title}`,
        body: contentChunks[Math.floor(Math.random() * contentChunks.length)]?.trim() || 'Learn something new!',
        data: { lessonId: lesson.id },
      }));

      // Send notifications in chunks
      const notificationChunks = expo.chunkPushNotifications(messages);
      for (const chunk of notificationChunks) {
        try {
          await expo.sendPushNotificationsAsync(chunk);
        } catch (error) {
          console.error('Error sending notifications:', error);
        }
      }
    }
  } catch (error) {
    console.error('Error in notification system:', error);
  }
}

// Schedule micro-learning notifications (e.g., every 4 hours)
setInterval(sendMicroLearningNotifications, 4 * 60 * 60 * 1000);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 