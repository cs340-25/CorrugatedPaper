const fs = require('fs');
const path = require('path');
const { MongoClient } = require('mongodb');

// MongoDB connection URI
const uri = "mongodb+srv://root:root@cluster0.cnbie.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
const client = new MongoClient(uri);

const dataDir = './F25SearchResults'; // Adjust this if your files are in a subfolder

async function importData() {
  try {
    await client.connect();
    const db = client.db('classes');
    const collection = db.collection('course');

    // Optional: Clear existing data
    await collection.deleteMany({});

    let totalInserted = 0;

    for (let i = 1; i <= 22; i++) {
      const filename = `searchResults${String(i).padStart(2, '0')}.json`; // Ensures 01–22 format
      const filepath = path.join(dataDir, filename);

      if (fs.existsSync(filepath)) {
        const fileContent = fs.readFileSync(filepath, 'utf-8');
        const jsonData = JSON.parse(fileContent);

        if (jsonData && Array.isArray(jsonData.data)) {
          const cleanData = jsonData.data.filter(c => c.courseTitle && c.subject);
          const result = await collection.insertMany(cleanData);
          totalInserted += result.insertedCount;
          console.log(`✔ Inserted ${result.insertedCount} records from ${filename}`);
        } else {
          console.warn(`⚠ No valid data in ${filename}`);
        }
      } else {
        console.warn(`⚠ File not found: ${filename}`);
      }
    }

    console.log(`✅ Import complete. Total documents inserted: ${totalInserted}`);
  } catch (error) {
    console.error("❌ Import failed:", error);
  } finally {
    await client.close();
  }
}

importData();
