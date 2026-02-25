/**
 * Server Entry Point
 * 
 * This file initializes and configures the Express server, including:
 * - Database connection (MongoDB)
 * - Middleware setup (CORS, JSON parsing)
 * - Route registration
 * - Error handling
 * 
 * Required Environment Variables:
 * - MONGO_URI: MongoDB connection string
 * - JWT_SECRET: Secret key for JWT token generation/validation
 * - PORT: Server port (defaults to 5000)
 * - NODE_ENV: Environment mode (development/production)
 */

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const authRoutes = require('./routes/auth');
const pathosRoutes = require('./routes/pathos');
const pathosController = require('./pathos');

// Initialize Express application instance
const app = express();

// Configure global middleware
// - CORS: Enable Cross-Origin Resource Sharing
// - express.json: Parse JSON request bodies
app.use(cors());
app.use(express.json());

/**
 * MongoDB Connection Configuration
 * 
 * Options:
 * - useNewUrlParser: Use new URL string parser
 * - useUnifiedTopology: Use new Server Discovery and Monitoring engine
 * - useCreateIndex: Ensure index creation uses createIndex() instead of ensureIndex()
 * - useFindAndModify: Disable deprecated findAndModify() operation
 */
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  useCreateIndex: true,
  useFindAndModify: false
})
.then(() => console.log('MongoDB Connected'))
.catch(err => {
  console.error('MongoDB Connection Error:', err);
  process.exit(1);
});

/**
 * Register Test Modules
 * 
 * This section registers a set of dummy modules for testing purposes.
 * In a production environment, these would be replaced with actual
 * functional modules loaded dynamically or configured via a module system.
 */
const dummyModules = [
  'mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn',
  'uranus', 'neptune', 'pluto', 'ceres', 'eris', 'haumea',
  'makemake', 'gonggong', 'sedna', 'quaoar', 'orcus', 'ixion',
  'varuna', 'triton', 'titania', 'oberon', 'ariel', 'umbriel',
  'miranda'
];

dummyModules.forEach(moduleName => {
  pathosController.registerModule(moduleName, {
    execute: (input) => `${moduleName} module executed with input: ${JSON.stringify(input)}`
  });
});

// Register API routes
// - /api/auth: Authentication endpoints (login, register)
// - /api/pathos: PaTHos system endpoints (execute, modules)
app.use('/api/auth', authRoutes);
app.use('/api/pathos', pathosRoutes);

/**
 * Global Error Handling Middleware
 * 
 * Catches all unhandled errors in the application and sends a formatted response.
 * In development, includes the full error message.
 * In production, sends a generic error message for security.
 */
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    message: 'Something went wrong!',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

/**
 * Health Check Endpoint
 * 
 * Simple endpoint to verify the server is running and responsive.
 * Useful for container orchestration and monitoring systems.
 */
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Initialize server on specified port
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Available PaTHos modules: ${pathosController.getAvailableModules().join(', ')}`);
});

/**
 * Unhandled Promise Rejection Handler
 * 
 * Catches any unhandled promise rejections in the application.
 * Logs the error and optionally terminates the process in production.
 * This prevents the application from silently failing due to rejected promises.
 */
process.on('unhandledRejection', (err) => {
  console.error('Unhandled Promise Rejection:', err);
  // In production, you might want to exit and let your process manager restart the app
  // process.exit(1);
});
