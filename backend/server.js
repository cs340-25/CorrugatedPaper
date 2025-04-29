const express = require('express');
const cors = require('cors');
const { MongoClient, ServerApiVersion } = require('mongodb');
const uri = "mongodb+srv://root:root@cluster0.cnbie.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";

// Set up express app
const app = express();
app.use(cors());

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(uri, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});

async function run() {
  try {
    // Connect the client to the server (optional starting in v4.7)
    await client.connect();
    // Send a ping to confirm a successful connection
    await client.db("admin").command({ ping: 1 });
    console.log("Pinged your deployment. You successfully connected to MongoDB!");

    const db = client.db('classes');
    const collection = db.collection('course');

    // Get entries from the database
    app.get('/entries', async (req, res) => {
      try {
        const entries = await collection.find({}).toArray();
        res.json(entries);
      } catch (error) {
        res.status(500).send("Error fetching entries");
      }
    });

// Modified endpoint to return multiple matches
app.get('/api/classes', async (req, res) => {
  const query = req.query.name?.toLowerCase();
  if (!query) return res.status(400).json({ error: "Missing search query" });
  try {
    const db = client.db('classes');
    const collection = db.collection('course');

    // Find multiple matches (limit to 10)
    const results = await collection.find({
      $or: [
        { courseTitle: { $regex: query, $options: "i" } },
        { courseNumber: { $regex: query, $options: "i" } },
        { subject: { $regex: query, $options: "i" } },
        { subjectCourse: { $regex: query, $options: "i" } }
      ]
    }).limit(10).toArray();


    res.json(results.length > 0 ? { success: true, data: results } : { success: false });
  } catch (error) {
    console.error("Error searching classes:", error);
    res.status(500).json({ success: false, error: "Search failed" });
  }
});  

  } catch (error) {
    console.error("An error occurred while connecting to MongoDB:", error);
  }
  // Closing the client will close the connection before any requests are handled
}

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

run().catch(console.dir);
