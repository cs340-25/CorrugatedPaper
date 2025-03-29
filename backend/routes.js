// backend/routes.js
const express = require('express');
const router = express.Router();
const { MongoClient } = require('mongodb');

// MongoDB connection string
const uri = "mongodb+srv://root:root@cluster0.cnbie.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
let db = null;

// Connect to MongoDB once
async function connectDB() {
  if (db) return db;
  const client = new MongoClient(uri);
  await client.connect();
  db = client.db("classes");
  return db;
}

// API endpoint to get all courses
router.get('/courses', async (req, res) => {
  try {
    const database = await connectDB();
    const collection = database.collection("course");
    const courses = await collection.find({}).toArray();
    res.json(courses);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Failed to fetch courses' });
  }
});

// API endpoint to get a specific course
router.get('/courses/:subject/:courseNumber', async (req, res) => {
  try {
    const { subject, courseNumber } = req.params;
    const database = await connectDB();
    const collection = database.collection("course");
    
    const course = await collection.findOne({
      subject: subject,
      courseNumber: courseNumber
    });
    
    if (!course) {
      return res.status(404).json({ error: 'Course not found' });
    }
    
    res.json(course);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Failed to fetch course' });
  }
});

module.exports = router;