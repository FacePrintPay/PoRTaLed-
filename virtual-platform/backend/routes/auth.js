/**
 * Authentication Routes
 * 
 * This module handles user authentication endpoints including registration
 * and login. It uses JWT for token-based authentication and bcrypt for
 * password hashing.
 * 
 * Base Path: /api/auth
 * 
 * Note: This implementation uses an in-memory user store for demonstration.
 * In production, users would be stored in a persistent database (e.g., MongoDB).
 */

const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// Mock in-memory user database
const users = [];

/**
 * User Registration
 * 
 * @route POST /api/auth/register
 * @param {string} req.body.username - Username for the new account
 * @param {string} req.body.password - Password for the new account
 * @returns {Object} JSON object containing:
 *   - token: JWT token for immediate authentication
 * @throws {400} If username already exists
 * @throws {500} If registration fails
 * 
 * Security measures:
 * - Password is hashed using bcrypt before storage
 * - JWT token is generated with 1-hour expiration
 */
router.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Check if user already exists
    if (users.find(user => user.username === username)) {
      return res.status(400).json({ message: 'User already exists' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create new user
    const user = {
      id: users.length + 1,
      username,
      password: hashedPassword
    };
    users.push(user);

    // Create and return JWT token
    const token = jwt.sign(
      { id: user.id, username: user.username },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({ token });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * User Login
 * 
 * @route POST /api/auth/login
 * @param {string} req.body.username - Username of the account
 * @param {string} req.body.password - Password of the account
 * @returns {Object} JSON object containing:
 *   - token: JWT token for authentication
 * @throws {400} If credentials are invalid
 * @throws {500} If login process fails
 * 
 * Security measures:
 * - Passwords are compared using bcrypt.compare()
 * - Generic error messages to prevent user enumeration
 * - JWT token includes minimal user data
 */
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Find user
    const user = users.find(user => user.username === username);
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    // Validate password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    // Create and return JWT token
    const token = jwt.sign(
      { id: user.id, username: user.username },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({ token });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
